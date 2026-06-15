#!/usr/bin/env python3
"""Record a work-session checkpoint and detect slippage."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import timedelta

from plan_day import parse_time
from session_state import load_session, save_session, transition


@dataclass
class CheckpointResult:
    state: str
    expected_progress: float
    actual_progress: float
    minutes_late: int
    delay_level: str
    action: str
    done: list[str]
    remaining: list[str]


def minutes_between(start_text: str, end_text: str) -> int:
    start = parse_time(start_text)
    end = parse_time(end_text)
    if end < start:
        end += timedelta(days=1)
    return max(0, round((end - start).total_seconds() / 60))


def delay_level(minutes_late: int, planned_minutes: int) -> str:
    if minutes_late <= 0:
        return "on-track"
    ratio = minutes_late / max(1, planned_minutes)
    if ratio <= 0.10:
        return "light"
    if ratio <= 0.25:
        return "moderate"
    return "severe"


def action_for(level: str) -> str:
    return {
        "on-track": "Keep the current plan and continue the next milestone.",
        "light": "Compress buffer and keep the core target.",
        "moderate": "Drop optional work and move toward the deliverable version.",
        "severe": "Switch to the minimum deliverable and stop broad exploration.",
    }[level]


def infer_actual_progress(done: list[str], remaining: list[str], percent_complete: int | None) -> float:
    if percent_complete is not None:
        return max(0.0, min(1.0, percent_complete / 100))
    total = len(done) + len(remaining)
    if total:
        return len(done) / total
    return 0.0


def evaluate_checkpoint(
    session: dict,
    now: str,
    done: list[str] | None = None,
    remaining: list[str] | None = None,
    percent_complete: int | None = None,
    minutes_late: int | None = None,
) -> CheckpointResult:
    done = done or []
    remaining = remaining or []
    planned = int(session.get("planned_minutes") or 1)
    elapsed = minutes_between(session.get("start", now), now)
    expected = min(1.0, elapsed / max(1, planned))
    actual = infer_actual_progress(done, remaining, percent_complete)
    if minutes_late is None:
        minutes_late = max(0, round((expected - actual) * planned))
    level = delay_level(minutes_late, planned)
    return CheckpointResult(
        state="delayed" if level in {"moderate", "severe"} else "checkpoint",
        expected_progress=expected,
        actual_progress=actual,
        minutes_late=minutes_late,
        delay_level=level,
        action=action_for(level),
        done=done,
        remaining=remaining,
    )


def render_markdown(result: CheckpointResult) -> str:
    lines = [
        "# Checkpoint",
        "",
        f"- State: {result.state}",
        f"- Expected progress: {result.expected_progress:.0%}",
        f"- Actual progress: {result.actual_progress:.0%}",
        f"- Minutes late: {result.minutes_late}",
        f"- Delay level: {result.delay_level}",
        f"- Action: {result.action}",
        "",
        "## Done",
        "",
    ]
    lines.extend([f"- {item}" for item in result.done] or ["- None recorded."])
    lines.extend(["", "## Remaining", ""])
    lines.extend([f"- {item}" for item in result.remaining] or ["- None recorded."])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a checkpoint in session.json.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--now", required=True, help="Current time in HH:MM.")
    parser.add_argument("--done", action="append", default=[])
    parser.add_argument("--remaining", action="append", default=[])
    parser.add_argument("--percent-complete", type=int)
    parser.add_argument("--minutes-late", type=int)
    parser.add_argument("--output")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    session = load_session(args.session)
    result = evaluate_checkpoint(
        session,
        now=args.now,
        done=args.done,
        remaining=args.remaining,
        percent_complete=args.percent_complete,
        minutes_late=args.minutes_late,
    )
    updated = transition(
        session,
        result.state,
        f"Checkpoint at {args.now}: {result.delay_level}.",
        asdict(result),
    )
    save_session(args.session, updated)
    text = json.dumps(asdict(result), ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(result)
    if args.output:
        from pathlib import Path

        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
