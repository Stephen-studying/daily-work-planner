#!/usr/bin/env python3
"""Reschedule the remaining part of a work session after checkpoint slippage."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from classify_work_mode import classify_work_mode
from plan_day import PlanConfig, generate_plan, parse_time
from session_state import load_session, save_session, transition


def minutes_between(now: datetime, deadline: datetime) -> int:
    if deadline < now:
        deadline += timedelta(days=1)
    return max(0, round((deadline - now).total_seconds() / 60))


def delay_level(minutes_late: int, total_minutes: int) -> str:
    if total_minutes <= 0:
        return "severe"
    ratio = minutes_late / total_minutes
    if ratio <= 0.10:
        return "light"
    if ratio <= 0.25:
        return "moderate"
    return "severe"


def reschedule(goal: str, now: str, hard_deadline: str, minutes_late: int, mode: str, total_minutes: int | None) -> str:
    now_dt = parse_time(now)
    deadline_dt = parse_time(hard_deadline)
    remaining = minutes_between(now_dt, deadline_dt)
    baseline = total_minutes or remaining + minutes_late
    level = delay_level(minutes_late, baseline)
    if mode == "auto":
        mode = classify_work_mode(goal, []).mode
    risk = "high" if level in {"moderate", "severe"} else "normal"
    plan = generate_plan(
        PlanConfig(
            start=now_dt,
            minutes=remaining,
            goal=f"Recover plan: {goal}",
            mode=mode,
            hard_deadline=deadline_dt,
            risk=risk,
        )
    )
    response = {
        "light": "Compress buffer, keep the core target, and skip only minor polish.",
        "moderate": "Drop optional files and polish. Move directly toward the minimum deliverable.",
        "severe": "Stop broad exploration. Finish the smallest complete artifact that can be submitted, shown, or continued from.",
    }[level]
    return "\n".join(
        [
            "# Rescheduled Work Session",
            "",
            f"- Delay level: {level}",
            f"- Minutes late: {minutes_late}",
            f"- Remaining minutes: {remaining}",
            f"- Response: {response}",
            "",
            plan,
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Reschedule a delayed work session.")
    parser.add_argument("--goal")
    parser.add_argument("--now", required=True, help="Current time in HH:MM.")
    parser.add_argument("--hard-deadline", help="Hard deadline in HH:MM.")
    parser.add_argument("--minutes-late", required=True, type=int)
    parser.add_argument("--total-minutes", type=int)
    parser.add_argument("--mode", default="auto")
    parser.add_argument("--output")
    parser.add_argument("--session", help="Optional session.json to update.")
    args = parser.parse_args()

    goal = args.goal
    hard_deadline = args.hard_deadline
    mode = args.mode
    total_minutes = args.total_minutes
    if args.session:
        session = load_session(args.session)
        goal = goal or session.get("goal", "")
        hard_deadline = hard_deadline or session.get("hard_deadline", "")
        mode = mode if mode != "auto" else session.get("mode", "auto")
        total_minutes = total_minutes or session.get("planned_minutes")
    if not goal:
        raise SystemExit("--goal is required unless --session contains a goal.")
    if not hard_deadline:
        raise SystemExit("--hard-deadline is required unless --session contains one.")

    text = reschedule(goal, args.now, hard_deadline, args.minutes_late, mode, total_minutes)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    if args.session:
        session = load_session(args.session)
        updated = transition(
            transition(session, "delayed", f"{args.minutes_late} minutes late at {args.now}."),
            "rescheduled",
            "Remaining plan regenerated.",
            {"now": args.now, "minutes_late": args.minutes_late, "output": args.output or ""},
        )
        save_session(args.session, updated)


if __name__ == "__main__":
    main()
