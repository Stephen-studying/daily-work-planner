#!/usr/bin/env python3
"""Build a simple personal estimation profile from review logs."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from classify_work_mode import classify_work_mode


@dataclass
class ModeStats:
    mode: str
    sessions: int
    planned_minutes: int
    actual_minutes: int
    average_delta_minutes: float
    average_delta_ratio: float
    recommendation: str


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                entries.append(current)
            current = {"date": line[3:].strip()}
            continue
        if current is not None and line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            current[key.strip().lower()] = value.strip()
    if current:
        entries.append(current)
    return entries


def to_int(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def build_profile(paths: list[str]) -> list[ModeStats]:
    buckets = defaultdict(lambda: {"sessions": 0, "planned": 0, "actual": 0})
    for path in paths:
        entries = parse_entries(Path(path).read_text(encoding="utf-8"))
        for entry in entries:
            planned = to_int(entry.get("planned minutes"))
            actual = to_int(entry.get("actual minutes"))
            if planned is None or actual is None:
                continue
            mode = entry.get("work mode") or classify_work_mode(entry.get("goal", ""), []).mode
            normalized = mode.lower().replace(" mode", "").replace(" ", "-")
            bucket = buckets[normalized]
            bucket["sessions"] += 1
            bucket["planned"] += planned
            bucket["actual"] += actual

    stats: list[ModeStats] = []
    for mode, bucket in sorted(buckets.items()):
        sessions = bucket["sessions"]
        planned = bucket["planned"]
        actual = bucket["actual"]
        delta = actual - planned
        avg_delta = delta / sessions if sessions else 0
        ratio = (delta / planned) if planned else 0
        if ratio > 0.20:
            rec = "Increase future estimates and buffer substantially."
        elif ratio > 0.05:
            rec = "Add modest buffer to this mode."
        elif ratio < -0.20:
            rec = "Estimates are conservative; consider shorter blocks."
        else:
            rec = "Current estimates are close."
        stats.append(ModeStats(mode, sessions, planned, actual, avg_delta, ratio, rec))
    return stats


def render_markdown(stats: list[ModeStats]) -> str:
    lines = [
        "# Estimation Profile",
        "",
        "| Mode | Sessions | Planned | Actual | Avg delta | Ratio | Recommendation |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in stats:
        lines.append(
            f"| {item.mode} | {item.sessions} | {item.planned_minutes} | {item.actual_minutes} | "
            f"{item.average_delta_minutes:.1f} | {item.average_delta_ratio:.0%} | {item.recommendation} |"
        )
    if not stats:
        lines.append("| none | 0 | 0 | 0 | 0 | 0% | Add completed review-log entries first. |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize planned-vs-actual timing from review logs.")
    parser.add_argument("logs", nargs="+")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    stats = build_profile(args.logs)
    if args.format == "json":
        print(json.dumps([asdict(item) for item in stats], ensure_ascii=False, indent=2))
    else:
        print(render_markdown(stats), end="")


if __name__ == "__main__":
    main()
