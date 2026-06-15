#!/usr/bin/env python3
"""Create a simple ICS calendar event without external dependencies."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def parse_local(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")


def ics_datetime(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M%S")


def escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def alarm_block(minutes_before: int | None) -> list[str]:
    if minutes_before is None:
        return []
    return [
        "BEGIN:VALARM",
        "ACTION:DISPLAY",
        f"DESCRIPTION:Reminder: {minutes_before} minutes before",
        f"TRIGGER:-PT{minutes_before}M",
        "END:VALARM",
    ]


def build_ics(
    title: str,
    start: datetime,
    end: datetime,
    description: str,
    alarm_minutes: int | None = None,
) -> str:
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    uid = f"{uuid4()}@daily-work-planner"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Daily Work Planner//EN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now}",
        f"DTSTART:{ics_datetime(start)}",
        f"DTEND:{ics_datetime(end)}",
        f"SUMMARY:{escape_ics(title)}",
        f"DESCRIPTION:{escape_ics(description)}",
    ]
    lines.extend(alarm_block(alarm_minutes))
    lines.extend(["END:VEVENT", "END:VCALENDAR", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a simple .ics event.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--start", required=True, help="Local start time: YYYY-MM-DDTHH:MM")
    parser.add_argument("--end", required=True, help="Local end time: YYYY-MM-DDTHH:MM")
    parser.add_argument("--description", default="")
    parser.add_argument("--alarm-minutes", type=int, help="Add a display reminder before the event.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    start = parse_local(args.start)
    end = parse_local(args.end)
    content = build_ics(args.title, start, end, args.description, args.alarm_minutes)
    Path(args.output).write_text(content, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
