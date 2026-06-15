#!/usr/bin/env python3
"""Local-first task memory for Daily Work Planner."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def memory_paths(memory_dir: str | Path) -> tuple[Path, Path]:
    root = Path(memory_dir)
    return root / "memory.jsonl", root / "MEMORY.md"


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_entries(memory_dir: str | Path) -> list[dict]:
    jsonl, _ = memory_paths(memory_dir)
    if not jsonl.exists():
        return []
    entries: list[dict] = []
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def speed_signal(planned: int | None, actual: int | None) -> str:
    if not planned or not actual:
        return "unknown"
    ratio = actual / planned
    if ratio >= 1.25:
        return "slower-than-plan"
    if ratio <= 0.80:
        return "faster-than-plan"
    return "close-to-plan"


def safe_file_names(files: list[str]) -> list[str]:
    return [Path(value).name for value in files]


def build_entry(
    goal: str,
    mode: str,
    completed: list[str],
    planned_minutes: int | None = None,
    actual_minutes: int | None = None,
    files: list[str] | None = None,
    habit: list[str] | None = None,
    note: str = "",
) -> dict:
    return {
        "created_at": now_iso(),
        "goal": goal,
        "mode": mode or "mixed",
        "completed": completed,
        "planned_minutes": planned_minutes,
        "actual_minutes": actual_minutes,
        "speed_signal": speed_signal(planned_minutes, actual_minutes),
        "files": safe_file_names(files or []),
        "habit": habit or [],
        "note": note,
    }


def entry_from_session(
    session_path: str | Path,
    completed: list[str],
    actual_minutes: int | None = None,
    habit: list[str] | None = None,
    note: str = "",
) -> dict:
    session = load_json(session_path)
    review = session.get("review") or {}
    actual = actual_minutes or review.get("actual_minutes")
    if isinstance(actual, str) and actual.isdigit():
        actual = int(actual)
    if not completed:
        completed = [event.get("note", "") for event in session.get("events", []) if event.get("state") in {"finished", "reviewed"}]
        completed = [item for item in completed if item]
    if not completed:
        completed = ["Session completed."]
    return build_entry(
        goal=session.get("goal", ""),
        mode=session.get("mode", "mixed"),
        completed=completed,
        planned_minutes=session.get("planned_minutes"),
        actual_minutes=actual if isinstance(actual, int) else None,
        files=session.get("files", []),
        habit=habit,
        note=note,
    )


def summarize_entries(entries: list[dict]) -> str:
    buckets = defaultdict(lambda: {"sessions": 0, "planned": 0, "actual": 0})
    habits: list[str] = []
    for entry in entries:
        mode = entry.get("mode") or "mixed"
        planned = entry.get("planned_minutes")
        actual = entry.get("actual_minutes")
        bucket = buckets[mode]
        bucket["sessions"] += 1
        if isinstance(planned, int):
            bucket["planned"] += planned
        if isinstance(actual, int):
            bucket["actual"] += actual
        habits.extend(str(item) for item in entry.get("habit", []) if item)

    lines = [
        "# Daily Work Planner Memory",
        "",
        "Local-first task memory. Keep this file private unless the user explicitly wants to share it.",
        "",
        "## Usage Profile",
        "",
        "| Mode | Sessions | Planned | Actual | Signal |",
        "|---|---:|---:|---:|---|",
    ]
    if not buckets:
        lines.append("| none | 0 | 0 | 0 | Add completed sessions first. |")
    else:
        for mode, bucket in sorted(buckets.items()):
            planned = bucket["planned"]
            actual = bucket["actual"]
            if planned and actual >= planned * 1.2:
                signal = "increase estimates or buffer"
            elif planned and actual <= planned * 0.8:
                signal = "estimates may be conservative"
            else:
                signal = "close to plan"
            lines.append(f"| {mode} | {bucket['sessions']} | {planned} | {actual} | {signal} |")

    lines.extend(["", "## Habit Notes", ""])
    if habits:
        for habit in sorted(set(habits)):
            lines.append(f"- {habit}")
    else:
        lines.append("- No explicit habit notes yet.")

    lines.extend(["", "## Recent Sessions", ""])
    for entry in entries[-10:][::-1]:
        completed = "; ".join(entry.get("completed", [])) or "completed"
        lines.append(
            f"- {entry.get('created_at')} | {entry.get('mode')} | {entry.get('goal')} | "
            f"planned={entry.get('planned_minutes')} actual={entry.get('actual_minutes')} | {completed}"
        )
    return "\n".join(lines) + "\n"


def remember(memory_dir: str | Path, entry: dict) -> tuple[Path, Path]:
    jsonl, markdown = memory_paths(memory_dir)
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    with jsonl.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    entries = load_entries(memory_dir)
    markdown.write_text(summarize_entries(entries), encoding="utf-8")
    return jsonl, markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Record local Daily Work Planner task memory.")
    parser.add_argument("--memory-dir", default=".daily-work-planner")
    parser.add_argument("--session", help="Optional session.json to summarize.")
    parser.add_argument("--goal", default="")
    parser.add_argument("--mode", default="mixed")
    parser.add_argument("--planned-minutes", type=int)
    parser.add_argument("--actual-minutes", type=int)
    parser.add_argument("--completed", action="append", default=[])
    parser.add_argument("--habit", action="append", default=[])
    parser.add_argument("--note", default="")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    if args.session:
        entry = entry_from_session(args.session, args.completed, args.actual_minutes, args.habit, args.note)
    else:
        entry = build_entry(
            goal=args.goal,
            mode=args.mode,
            completed=args.completed or ["Task completed."],
            planned_minutes=args.planned_minutes,
            actual_minutes=args.actual_minutes,
            files=args.files,
            habit=args.habit,
            note=args.note,
        )
    _, markdown = remember(args.memory_dir, entry)
    print(str(markdown))


if __name__ == "__main__":
    main()
