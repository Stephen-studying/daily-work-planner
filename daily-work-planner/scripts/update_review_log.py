#!/usr/bin/env python3
"""Append a work-session review entry to a Markdown log."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def build_entry(
    goal: str,
    planned_minutes: int,
    actual_minutes: int,
    delay_reason: str,
    next_adjustment: str,
) -> str:
    delta = actual_minutes - planned_minutes
    status = "over" if delta > 0 else "under" if delta < 0 else "on target"
    return "\n".join(
        [
            f"## {date.today().isoformat()}",
            "",
            f"- Goal: {goal}",
            f"- Planned minutes: {planned_minutes}",
            f"- Actual minutes: {actual_minutes}",
            f"- Estimate result: {status} by {abs(delta)} min",
            f"- Main delay reason: {delay_reason or 'none recorded'}",
            f"- Next estimate adjustment: {next_adjustment or 'none recorded'}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a Markdown review-log entry.")
    parser.add_argument("--log", required=True, help="Path to the Markdown review log.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--planned-minutes", required=True, type=int)
    parser.add_argument("--actual-minutes", required=True, type=int)
    parser.add_argument("--delay-reason", default="")
    parser.add_argument("--next-adjustment", default="")
    args = parser.parse_args()

    path = Path(args.log)
    if not path.exists():
        path.write_text("# Work Session Review Log\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(build_entry(
            args.goal,
            args.planned_minutes,
            args.actual_minutes,
            args.delay_reason,
            args.next_adjustment,
        ))
    print(str(path))


if __name__ == "__main__":
    main()
