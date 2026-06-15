#!/usr/bin/env python3
"""Run Daily Work Planner scripts through one module entrypoint."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


COMMANDS = {
    "start": "start_session.py",
    "extract": "extract_file_context.py",
    "plan": "plan_day.py",
    "ics": "make_ics.py",
    "review": "update_review_log.py",
    "classify": "classify_work_mode.py",
    "rank": "rank_files.py",
    "validate": "validate_plan.py",
    "todo": "make_todo.py",
    "reschedule": "reschedule_session.py",
    "profile": "estimate_profile.py",
    "session": "session_state.py",
    "inspect": "inspect_tasks.py",
    "remember": "task_memory.py",
    "feasibility": "feasibility_score.py",
    "checkpoint": "checkpoint_session.py",
    "resume": "resume_session.py",
    "handoff": "handoff_session.py",
}


def scripts_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "daily-work-planner" / "scripts"


def print_help() -> None:
    names = ", ".join(sorted(COMMANDS))
    print("Daily Work Planner")
    print("")
    print("Usage:")
    print("  python -m daily_work_planner <command> [args]")
    print("")
    print(f"Commands: {names}")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print_help()
        return
    command = sys.argv[1]
    script_name = COMMANDS.get(command)
    if not script_name:
        print(f"Unknown command: {command}", file=sys.stderr)
        print_help()
        raise SystemExit(2)

    script_path = scripts_dir() / script_name
    sys.path.insert(0, str(scripts_dir()))
    sys.argv = [str(script_path)] + sys.argv[2:]
    runpy.run_path(str(script_path), run_name="__main__")


if __name__ == "__main__":
    main()
