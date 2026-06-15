#!/usr/bin/env python3
"""Manage Daily Work Planner session state files."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from uuid import uuid4


VALID_STATES = {"planned", "started", "checkpoint", "delayed", "rescheduled", "finished", "reviewed"}
TRANSITIONS = {
    "planned": {"started", "checkpoint", "delayed", "finished"},
    "started": {"checkpoint", "delayed", "finished"},
    "checkpoint": {"checkpoint", "delayed", "finished"},
    "delayed": {"rescheduled", "finished"},
    "rescheduled": {"checkpoint", "delayed", "finished"},
    "finished": {"reviewed"},
    "reviewed": set(),
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def create_session(
    goal: str,
    mode: str,
    start: str,
    hard_deadline: str,
    planned_minutes: int,
    files: list[str],
    outputs: dict[str, str] | None = None,
    adaptive_buffer: dict | None = None,
) -> dict:
    timestamp = now_iso()
    return {
        "schema_version": "1.0",
        "id": str(uuid4()),
        "state": "planned",
        "created_at": timestamp,
        "updated_at": timestamp,
        "goal": goal,
        "mode": mode,
        "start": start,
        "hard_deadline": hard_deadline,
        "planned_minutes": planned_minutes,
        "files": files,
        "outputs": outputs or {},
        "adaptive_buffer": adaptive_buffer or {"extra_percent": 0, "reason": "none"},
        "events": [
            {
                "at": timestamp,
                "state": "planned",
                "note": "Session package created.",
            }
        ],
        "review": {},
    }


def load_session(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_session(path: str | Path, session: dict) -> None:
    session["updated_at"] = now_iso()
    Path(path).write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def transition(session: dict, new_state: str, note: str = "", data: dict | None = None) -> dict:
    if new_state not in VALID_STATES:
        raise ValueError(f"Unknown session state: {new_state}")
    current = session.get("state", "planned")
    if new_state != current and new_state not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Invalid transition: {current} -> {new_state}")
    updated = deepcopy(session)
    updated["state"] = new_state
    event = {"at": now_iso(), "state": new_state, "note": note}
    if data:
        event["data"] = data
    updated.setdefault("events", []).append(event)
    return updated


def update_outputs(session: dict, outputs: dict[str, str]) -> dict:
    updated = deepcopy(session)
    updated.setdefault("outputs", {}).update(outputs)
    return updated


def apply_review(
    session: dict,
    actual_minutes: int,
    soft_deadline_met: str = "",
    hard_deadline_met: str = "",
    minimum_deliverable_completed: str = "",
    delay_reason: str = "",
    next_adjustment: str = "",
) -> dict:
    updated = deepcopy(session)
    updated["review"] = {
        "actual_minutes": actual_minutes,
        "soft_deadline_met": soft_deadline_met,
        "hard_deadline_met": hard_deadline_met,
        "minimum_deliverable_completed": minimum_deliverable_completed,
        "delay_reason": delay_reason,
        "next_adjustment": next_adjustment,
    }
    updated = transition(updated, "reviewed", "Review recorded.")
    return updated


def render_markdown(session: dict) -> str:
    lines = [
        "# Session State",
        "",
        f"- ID: {session.get('id')}",
        f"- State: {session.get('state')}",
        f"- Goal: {session.get('goal')}",
        f"- Mode: {session.get('mode')}",
        f"- Planned minutes: {session.get('planned_minutes')}",
        f"- Hard deadline: {session.get('hard_deadline')}",
        "",
        "## Events",
        "",
    ]
    for event in session.get("events", []):
        lines.append(f"- {event.get('at')} [{event.get('state')}] {event.get('note', '')}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Daily Work Planner session.json files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--goal", required=True)
    create.add_argument("--mode", required=True)
    create.add_argument("--start", required=True)
    create.add_argument("--hard-deadline", required=True)
    create.add_argument("--planned-minutes", type=int, required=True)
    create.add_argument("--output", required=True)
    create.add_argument("files", nargs="*")

    status = subparsers.add_parser("status")
    status.add_argument("--session", required=True)
    status.add_argument("--format", choices=["markdown", "json"], default="markdown")

    move = subparsers.add_parser("transition")
    move.add_argument("--session", required=True)
    move.add_argument("--state", required=True, choices=sorted(VALID_STATES))
    move.add_argument("--note", default="")

    review = subparsers.add_parser("review")
    review.add_argument("--session", required=True)
    review.add_argument("--actual-minutes", type=int, required=True)
    review.add_argument("--soft-deadline-met", default="")
    review.add_argument("--hard-deadline-met", default="")
    review.add_argument("--minimum-deliverable-completed", default="")
    review.add_argument("--delay-reason", default="")
    review.add_argument("--next-adjustment", default="")

    args = parser.parse_args()

    if args.command == "create":
        session = create_session(args.goal, args.mode, args.start, args.hard_deadline, args.planned_minutes, args.files)
        save_session(args.output, session)
        print(args.output)
        return

    session = load_session(args.session)
    if args.command == "status":
        if args.format == "json":
            print(json.dumps(session, ensure_ascii=False, indent=2))
        else:
            print(render_markdown(session), end="")
    elif args.command == "transition":
        save_session(args.session, transition(session, args.state, args.note))
        print(args.session)
    elif args.command == "review":
        reviewed = apply_review(
            session,
            actual_minutes=args.actual_minutes,
            soft_deadline_met=args.soft_deadline_met,
            hard_deadline_met=args.hard_deadline_met,
            minimum_deliverable_completed=args.minimum_deliverable_completed,
            delay_reason=args.delay_reason,
            next_adjustment=args.next_adjustment,
        )
        save_session(args.session, reviewed)
        print(args.session)


if __name__ == "__main__":
    main()
