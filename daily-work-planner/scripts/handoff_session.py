#!/usr/bin/env python3
"""Create an end-of-session handoff and optionally record local memory."""

from __future__ import annotations

import argparse
from pathlib import Path

from session_state import load_session, save_session, transition
from task_memory import entry_from_session, remember


def render_handoff(
    session: dict,
    completed: list[str],
    remaining: list[str],
    actual_minutes: int | None,
    notes: list[str],
) -> str:
    lines = [
        "# Work Session Handoff",
        "",
        f"- Goal: {session.get('goal', '')}",
        f"- State: {session.get('state', '')}",
        f"- Mode: {session.get('mode', '')}",
        f"- Planned minutes: {session.get('planned_minutes', '')}",
        f"- Actual minutes: {actual_minutes if actual_minutes is not None else 'not recorded'}",
        f"- Hard deadline: {session.get('hard_deadline', '')}",
        "",
        "## Completed",
        "",
    ]
    lines.extend([f"- {item}" for item in completed] or ["- No completed items were provided."])
    lines.extend(["", "## Remaining", ""])
    lines.extend([f"- {item}" for item in remaining] or ["- No remaining items were provided."])
    lines.extend(["", "## Next Session Start", ""])
    if remaining:
        lines.append(f"Start with: {remaining[0]}")
    else:
        lines.append("Start by reviewing this handoff and confirming whether a new task should begin.")
    lines.extend(["", "## Notes", ""])
    lines.extend([f"- {item}" for item in notes] or ["- No notes recorded."])
    return "\n".join(lines) + "\n"


def create_handoff(
    session_path: str | Path,
    completed: list[str],
    remaining: list[str],
    actual_minutes: int | None = None,
    notes: list[str] | None = None,
    output: str | Path | None = None,
    write_memory: bool = False,
    memory_dir: str | Path = ".daily-work-planner",
    habits: list[str] | None = None,
) -> Path:
    session = load_session(session_path)
    text = render_handoff(session, completed, remaining, actual_minutes, notes or [])
    output_path = Path(output) if output else Path(session_path).with_name("handoff.md")
    output_path.write_text(text, encoding="utf-8")
    try:
        updated = transition(
            session,
            "finished",
            "Handoff created.",
            {"output": str(output_path), "completed": completed, "remaining": remaining},
        )
        save_session(session_path, updated)
    except ValueError:
        pass
    if write_memory:
        entry = entry_from_session(
            session_path,
            completed=completed,
            actual_minutes=actual_minutes,
            habit=habits or [],
            note="Handoff memory entry.",
        )
        remember(memory_dir, entry)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a work-session handoff.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--completed", action="append", default=[])
    parser.add_argument("--remaining", action="append", default=[])
    parser.add_argument("--actual-minutes", type=int)
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--habit", action="append", default=[])
    parser.add_argument("--output")
    parser.add_argument("--remember", action="store_true")
    parser.add_argument("--memory-dir", default=".daily-work-planner")
    args = parser.parse_args()

    path = create_handoff(
        session_path=args.session,
        completed=args.completed,
        remaining=args.remaining,
        actual_minutes=args.actual_minutes,
        notes=args.note,
        output=args.output,
        write_memory=args.remember,
        memory_dir=args.memory_dir,
        habits=args.habit,
    )
    print(str(path))


if __name__ == "__main__":
    main()
