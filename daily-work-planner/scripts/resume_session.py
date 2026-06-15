#!/usr/bin/env python3
"""Create a concise resume card for a previous work session."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from session_state import load_session
from task_memory import load_entries


@dataclass
class ResumeCard:
    goal: str
    state: str
    mode: str
    planned_minutes: int
    last_event: str
    done: list[str]
    remaining: list[str]
    next_action: str
    estimated_remaining_minutes: int
    memory_hint: str


def latest_checkpoint_data(session: dict) -> dict:
    for event in reversed(session.get("events", [])):
        data = event.get("data") or {}
        if "remaining" in data or "done" in data:
            return data
    return {}


def estimate_remaining(session: dict, data: dict) -> int:
    remaining = data.get("remaining") or []
    progress = data.get("actual_progress")
    planned = int(session.get("planned_minutes") or 60)
    if isinstance(progress, (int, float)):
        return max(10, round(planned * (1 - float(progress))))
    if remaining:
        return min(planned, max(15, len(remaining) * 30))
    if session.get("state") in {"finished", "reviewed"}:
        return 0
    return max(15, round(planned * 0.5))


def next_action_for(session: dict, remaining: list[str]) -> str:
    state = session.get("state", "planned")
    if remaining:
        return f"Continue with: {remaining[0]}"
    if state == "planned":
        return "Open the session plan and start the first milestone."
    if state == "delayed":
        return "Run reschedule or switch to the minimum deliverable."
    if state == "rescheduled":
        return "Continue the rescheduled plan from its first remaining milestone."
    if state in {"finished", "reviewed"}:
        return "Review the handoff or start a new session."
    return "Continue the next planned milestone."


def memory_hint(memory_dir: str | Path, mode: str) -> str:
    entries = load_entries(memory_dir)
    matching = [entry for entry in entries if entry.get("mode") == mode]
    if not matching:
        return "No matching local memory yet."
    recent = matching[-1]
    signal = recent.get("speed_signal", "unknown")
    habit = "; ".join(recent.get("habit", []))
    if habit:
        return f"Recent memory: {signal}; {habit}"
    return f"Recent memory: {signal}"


def build_resume_card(session_path: str | Path, memory_dir: str | Path = ".daily-work-planner") -> ResumeCard:
    session = load_session(session_path)
    events = session.get("events", [])
    last = events[-1] if events else {}
    data = latest_checkpoint_data(session)
    done = data.get("done") or []
    remaining = data.get("remaining") or []
    return ResumeCard(
        goal=session.get("goal", ""),
        state=session.get("state", "planned"),
        mode=session.get("mode", "mixed"),
        planned_minutes=int(session.get("planned_minutes") or 0),
        last_event=f"{last.get('at', '')} [{last.get('state', '')}] {last.get('note', '')}".strip(),
        done=done,
        remaining=remaining,
        next_action=next_action_for(session, remaining),
        estimated_remaining_minutes=estimate_remaining(session, data),
        memory_hint=memory_hint(memory_dir, session.get("mode", "mixed")),
    )


def render_markdown(card: ResumeCard) -> str:
    lines = [
        "# Resume Card",
        "",
        f"- Goal: {card.goal}",
        f"- State: {card.state}",
        f"- Mode: {card.mode}",
        f"- Planned minutes: {card.planned_minutes}",
        f"- Estimated remaining: {card.estimated_remaining_minutes} min",
        f"- Last event: {card.last_event or 'none'}",
        f"- Memory hint: {card.memory_hint}",
        "",
        "## Done",
        "",
    ]
    lines.extend([f"- {item}" for item in card.done] or ["- None recorded."])
    lines.extend(["", "## Remaining", ""])
    lines.extend([f"- {item}" for item in card.remaining] or ["- No explicit remaining list recorded."])
    lines.extend(["", "## Next Action", "", card.next_action, ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a resume card from session.json.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--memory-dir", default=".daily-work-planner")
    parser.add_argument("--output")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    card = build_resume_card(args.session, args.memory_dir)
    text = json.dumps(asdict(card), ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(card)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
