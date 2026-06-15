#!/usr/bin/env python3
"""Assess whether a work-session plan fits the available time."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from classify_work_mode import classify_work_mode
from inspect_tasks import estimate_goal_minutes


@dataclass
class FeasibilityResult:
    goal: str
    mode: str
    available_minutes: int
    estimated_minutes: int
    score: int
    level: str
    recommended_scope: str
    risks: list[str]
    scope_options: dict[str, int]
    first_action: str


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def scope_options(estimated_minutes: int) -> dict[str, int]:
    return {
        "complete": max(15, round(estimated_minutes)),
        "deliverable": max(15, round(estimated_minutes * 0.75)),
        "minimum": max(10, round(estimated_minutes * 0.45)),
    }


def assess_feasibility(
    goal: str,
    available_minutes: int,
    estimated_minutes: int | None = None,
    mode: str = "auto",
    file_count: int = 0,
    task_count: int = 0,
    speed: str = "normal",
    risk: str = "normal",
) -> FeasibilityResult:
    if mode == "auto":
        mode = classify_work_mode(goal, []).mode
    estimate = estimated_minutes or estimate_goal_minutes(
        goal,
        mode=mode,
        file_count=file_count,
        task_count=task_count,
        speed=speed,
    )
    estimate = max(1, estimate)
    ratio = available_minutes / estimate
    score = round(clamp(ratio, 0.0, 1.3) / 1.3 * 100)
    if risk == "high":
        score = max(0, score - 10)

    options = scope_options(estimate)
    risks: list[str] = []
    if available_minutes < options["minimum"]:
        level = "low"
        recommended = "defer-or-redefine"
        risks.append("Available time is below the minimum deliverable estimate.")
    elif available_minutes < options["deliverable"]:
        level = "low"
        recommended = "minimum"
        risks.append("Only the minimum deliverable is realistic.")
    elif available_minutes < options["complete"]:
        level = "medium"
        recommended = "deliverable"
        risks.append("The complete version is likely too large for the time box.")
    else:
        level = "high"
        recommended = "complete"

    if file_count >= 6:
        risks.append("Many files are involved; rank files before deep work.")
    if task_count >= 8:
        risks.append("Many open tasks are present; keep only the highest-impact subset.")
    if risk == "high":
        risks.append("Risk is marked high; keep extra buffer and reduce optional work.")
    if not risks:
        risks.append("No major feasibility risk detected.")

    first_action = {
        "complete": "Start with the first planned milestone.",
        "deliverable": "Drop optional polish and define the usable deliverable first.",
        "minimum": "Define the smallest complete output before opening extra files.",
        "defer-or-redefine": "Clarify scope or extend time before starting.",
    }[recommended]
    return FeasibilityResult(
        goal=goal,
        mode=mode,
        available_minutes=available_minutes,
        estimated_minutes=estimate,
        score=score,
        level=level,
        recommended_scope=recommended,
        risks=risks,
        scope_options=options,
        first_action=first_action,
    )


def render_markdown(result: FeasibilityResult) -> str:
    lines = [
        "# Feasibility Score",
        "",
        f"- Goal: {result.goal}",
        f"- Mode: {result.mode}",
        f"- Available minutes: {result.available_minutes}",
        f"- Estimated minutes: {result.estimated_minutes}",
        f"- Score: {result.score}/100",
        f"- Level: {result.level}",
        f"- Recommended scope: {result.recommended_scope}",
        "",
        "## Scope Options",
        "",
        "| Scope | Estimated minutes | Use when |",
        "|---|---:|---|",
        f"| complete | {result.scope_options['complete']} | Time is enough for full output and polish. |",
        f"| deliverable | {result.scope_options['deliverable']} | Time is tight but a usable version is realistic. |",
        f"| minimum | {result.scope_options['minimum']} | Time is short; protect only the core output. |",
        "",
        "## Risks",
        "",
    ]
    for risk in result.risks:
        lines.append(f"- {risk}")
    lines.extend(["", "## First Action", "", result.first_action, ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess whether a task fits the available time.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--available-minutes", type=int, required=True)
    parser.add_argument("--estimated-minutes", type=int)
    parser.add_argument("--mode", default="auto")
    parser.add_argument("--file-count", type=int, default=0)
    parser.add_argument("--task-count", type=int, default=0)
    parser.add_argument("--speed", choices=["fast", "normal", "slow"], default="normal")
    parser.add_argument("--risk", choices=["normal", "high"], default="normal")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    result = assess_feasibility(
        goal=args.goal,
        available_minutes=args.available_minutes,
        estimated_minutes=args.estimated_minutes,
        mode=args.mode,
        file_count=args.file_count,
        task_count=args.task_count,
        speed=args.speed,
        risk=args.risk,
    )
    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result), end="")


if __name__ == "__main__":
    main()
