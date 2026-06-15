#!/usr/bin/env python3
"""Validate a generated Daily Work Planner Markdown plan."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def planning_cap(minutes: int) -> int:
    if minutes <= 60:
        return 3
    if minutes <= 240:
        return 8
    if minutes <= 480:
        return 15
    return 20


def max_planning_budget(minutes: int) -> int:
    return max(1, min(round(minutes * 0.05), planning_cap(minutes)))


def extract_budget(text: str) -> int | None:
    match = re.search(r"planning budget\D+(\d+)\s*min", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def milestone_rows(text: str) -> list[str]:
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped.lower():
            continue
        if "time" in stripped.lower() and "task" in stripped.lower():
            continue
        if stripped.count("|") >= 4:
            rows.append(stripped)
    return rows


def validate_plan(text: str, available_minutes: int | None = None) -> list[Check]:
    lower = text.lower()
    rows = milestone_rows(text)
    checks = [
        Check("soft_deadline", "soft deadline" in lower, "Plan should include a soft deadline."),
        Check("hard_deadline", "hard deadline" in lower, "Plan should include a hard deadline."),
        Check("minimum_deliverable", "minimum deliverable" in lower, "Plan should define a protected minimum deliverable."),
        Check("buffer", "buffer" in lower, "Plan should reserve buffer time."),
        Check("delay_response", "delay response" in lower or "fallback" in lower or "reschedule" in lower, "Plan should include delay handling."),
        Check("milestones", len(rows) >= 2, f"Found {len(rows)} milestone-like rows."),
    ]
    if rows:
        criteria_rows = [row for row in rows if "criteria" not in row.lower() and len([cell.strip() for cell in row.split("|") if cell.strip()]) >= 4]
        checks.append(Check("acceptance_criteria", len(criteria_rows) >= 2, f"Found {len(criteria_rows)} rows with enough columns."))

    if available_minutes is not None:
        budget = extract_budget(text)
        limit = max_planning_budget(available_minutes)
        checks.append(
            Check(
                "planning_budget_limit",
                budget is not None and budget <= limit,
                f"Budget={budget}, limit={limit} for {available_minutes} available minutes.",
            )
        )
    return checks


def render_markdown(checks: list[Check]) -> str:
    lines = ["# Plan Validation", "", "| Check | Result | Detail |", "|---|---|---|"]
    for check in checks:
        result = "PASS" if check.passed else "FAIL"
        lines.append(f"| {check.name} | {result} | {check.detail} |")
    passed = sum(1 for check in checks if check.passed)
    lines.extend(["", f"Score: {passed}/{len(checks)} checks passed."])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Daily Work Planner plan.")
    parser.add_argument("--plan", help="Markdown plan path. Reads stdin when omitted.")
    parser.add_argument("--available-minutes", type=int)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any check fails.")
    args = parser.parse_args()

    text = Path(args.plan).read_text(encoding="utf-8") if args.plan else input()
    checks = validate_plan(text, args.available_minutes)
    if args.format == "json":
        print(json.dumps([asdict(check) for check in checks], ensure_ascii=False, indent=2))
    else:
        print(render_markdown(checks), end="")
    if args.strict and not all(check.passed for check in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
