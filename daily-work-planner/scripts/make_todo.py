#!/usr/bin/env python3
"""Create a todo.txt style list from a Markdown milestone table."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_milestones(text: str) -> list[tuple[str, str, str]]:
    items: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0].lower() == "time":
            continue
        if re.search(r"\d{1,2}:\d{2}", cells[0]):
            items.append((cells[0], cells[1], cells[2]))
    return items


def render_todo(items: list[tuple[str, str, str]]) -> str:
    if not items:
        return "[ ] Review the plan and define the first concrete action.\n"
    return "".join(f"[ ] {time_range} {task} -> {deliverable}\n" for time_range, task, deliverable in items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate todo.txt entries from a plan.")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    text = Path(args.plan).read_text(encoding="utf-8")
    todo = render_todo(parse_milestones(text))
    if args.output:
        Path(args.output).write_text(todo, encoding="utf-8")
    else:
        print(todo, end="")


if __name__ == "__main__":
    main()
