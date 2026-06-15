#!/usr/bin/env python3
"""Generate a compact Markdown work-session plan.

This script is intentionally dependency-free so the skill works after a simple
clone or skill install.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta


MODE_LABELS = {
    "writing": "Deep Writing Mode",
    "reading": "Fast Reading Mode",
    "exam": "Exam Review Mode",
    "code": "Code Development Mode",
    "ppt": "PPT Production Mode",
    "revision": "Document Revision Mode",
    "data": "Data Organization Mode",
    "research": "Research Planning Mode",
    "literature": "Literature Review Mode",
    "application": "Application Materials Mode",
    "translation": "Translation and Polishing Mode",
    "meeting": "Meeting Preparation Mode",
    "lab": "Lab Work Mode",
    "admin": "Admin Task Mode",
    "design": "Design and Creative Mode",
    "mixed": "Mixed Work Mode",
}


@dataclass
class PlanConfig:
    start: datetime
    minutes: int
    goal: str
    mode: str
    hard_deadline: datetime | None = None
    risk: str = "normal"
    buffer_extra_percent: float = 0.0
    buffer_reason: str = ""


def parse_time(value: str) -> datetime:
    today = datetime.now().date()
    hour, minute = [int(part) for part in value.split(":", 1)]
    return datetime.combine(today, datetime.min.time()).replace(hour=hour, minute=minute)


def parse_optional_time(value: str | None, start: datetime) -> datetime | None:
    if not value:
        return None
    parsed = parse_time(value)
    if parsed < start:
        parsed += timedelta(days=1)
    return parsed


def planning_cap(minutes: int) -> int:
    if minutes <= 60:
        return 3
    if minutes <= 240:
        return 8
    if minutes <= 480:
        return 15
    return 20


def planning_budget(minutes: int) -> int:
    return max(1, min(round(minutes * 0.05), planning_cap(minutes)))


def buffer_minutes(minutes: int, risk: str, extra_percent: float = 0.0) -> int:
    if minutes <= 60:
        ratio = 0.10
    elif minutes <= 240:
        ratio = 0.15
    elif minutes <= 480:
        ratio = 0.20
    else:
        ratio = 0.25
    if risk == "high":
        ratio += 0.05
    ratio += max(0.0, extra_percent / 100.0)
    ratio = min(ratio, 0.45)
    return max(5, round(minutes * ratio))


def output_depth(minutes: int) -> str:
    if minutes <= 60:
        return "quick"
    if minutes <= 240:
        return "standard"
    return "full"


def mode_tasks(mode: str) -> list[tuple[str, str, str]]:
    common = {
        "writing": [
            ("Scope and outline", "section plan", "main claim and sections are clear"),
            ("Draft core content", "usable draft", "all required sections have content"),
            ("Revise and check", "clean version", "logic gaps and obvious wording issues are fixed"),
        ],
        "reading": [
            ("Scan source material", "priority map", "must-read and skip sections are identified"),
            ("Read priority sections", "structured notes", "core claims and evidence are captured"),
            ("Extract next-use output", "actionable summary", "notes can directly support the next task"),
        ],
        "exam": [
            ("Triage topics", "topic priority list", "high-frequency and weak topics are identified"),
            ("Review and practice", "checked answers", "key problems are attempted and corrected"),
            ("Memory check", "recall sheet", "answers can be recalled without looking"),
        ],
        "code": [
            ("Locate relevant files", "implementation map", "entry points and tests are known"),
            ("Build minimum path", "runnable change", "main behavior works on the primary path"),
            ("Verify", "test result", "focused verification command has been run or specified"),
        ],
        "ppt": [
            ("Define storyline", "slide outline", "talk flow fits the time limit"),
            ("Build core slides", "rough deck", "main evidence and conclusion slides exist"),
            ("Polish and export", "presentable deck", "format and export checks are complete"),
        ],
        "revision": [
            ("Inspect main document", "issue list", "high-risk sections and formatting issues are known"),
            ("Revise priority sections", "corrected draft", "critical content and structure issues are fixed"),
            ("Final check", "submission file", "filename, format, references, and export are checked"),
        ],
        "data": [
            ("Inventory sources", "source map", "primary data and optional files are separated"),
            ("Clean and structure", "clean table", "columns, names, and missing values are handled"),
            ("Summarize output", "usable summary", "final table or chart supports the goal"),
        ],
        "research": [
            ("Define research question", "decision frame", "question, evidence need, and constraints are clear"),
            ("Map evidence and methods", "research worklist", "sources, data, or experiments are prioritized"),
            ("Produce next research artifact", "usable research output", "next claim, protocol, or analysis step is ready"),
        ],
        "literature": [
            ("Set review scope", "search and screening criteria", "topic, inclusion criteria, and target output are clear"),
            ("Screen priority sources", "source shortlist", "must-read and optional references are separated"),
            ("Synthesize evidence", "literature synthesis note", "claims are linked to key references"),
        ],
        "application": [
            ("Clarify target and requirements", "application checklist", "required materials and constraints are known"),
            ("Draft or revise core material", "usable application draft", "main story and required sections are complete"),
            ("Submission check", "submission-ready package", "files, names, formatting, and requirements are checked"),
        ],
        "translation": [
            ("Identify translation scope", "segment map", "source sections and target style are clear"),
            ("Translate or polish core text", "usable target text", "meaning is preserved and wording is coherent"),
            ("Terminology and consistency check", "clean bilingual/polished version", "terms, names, and formatting are consistent"),
        ],
        "meeting": [
            ("Define meeting objective", "agenda", "decision points and required inputs are clear"),
            ("Prepare materials", "briefing notes", "talking points, files, and questions are ready"),
            ("Close with actions", "follow-up list", "owners, deadlines, and next actions are captured"),
        ],
        "lab": [
            ("Confirm protocol and materials", "lab checklist", "samples, instruments, and steps are verified"),
            ("Run or prepare core work", "experiment record", "critical measurements or setup steps are complete"),
            ("Record and backup results", "traceable lab note", "data location, anomalies, and next step are recorded"),
        ],
        "admin": [
            ("Collect requirements", "admin checklist", "forms, recipients, and deadlines are clear"),
            ("Complete core paperwork", "ready-to-submit item", "required fields and attachments are complete"),
            ("Submit or queue follow-up", "submission record", "confirmation, next action, or reminder is saved"),
        ],
        "design": [
            ("Define design brief", "brief and constraints", "audience, goal, and format are clear"),
            ("Create core concept", "draft mockup or asset", "main layout, message, or prototype exists"),
            ("Review and export", "shareable design output", "format, naming, and handoff checks are complete"),
        ],
        "mixed": [
            ("Define scope", "priority plan", "final deliverable and file priority are clear"),
            ("Produce core artifact", "minimum deliverable", "the protected output exists"),
            ("Check and package", "usable version", "final check and save/export steps are complete"),
        ],
    }
    return common.get(mode, common["mixed"])


def allocate_milestones(start: datetime, end: datetime, planning: int, buffer: int, mode: str):
    work_start = start + timedelta(minutes=planning)
    buffer_start = end - timedelta(minutes=buffer)
    usable = max(15, round((buffer_start - work_start).total_seconds() / 60))
    tasks = mode_tasks(mode)
    slice_minutes = max(5, usable // len(tasks))
    milestones = []
    cursor = work_start
    for index, (task, deliverable, criteria) in enumerate(tasks):
        next_time = buffer_start if index == len(tasks) - 1 else cursor + timedelta(minutes=slice_minutes)
        milestones.append((cursor, next_time, task, deliverable, criteria))
        cursor = next_time
    return milestones, buffer_start


def fmt_time(value: datetime) -> str:
    return value.strftime("%H:%M")


def generate_plan(config: PlanConfig) -> str:
    hard = config.hard_deadline or (config.start + timedelta(minutes=config.minutes))
    planning = planning_budget(config.minutes)
    buffer = buffer_minutes(config.minutes, config.risk, config.buffer_extra_percent)
    soft = hard - timedelta(minutes=buffer)
    mode_label = MODE_LABELS.get(config.mode, MODE_LABELS["mixed"])
    milestones, buffer_start = allocate_milestones(config.start, hard, planning, buffer, config.mode)
    depth = output_depth(config.minutes)

    lines = [
        "# Work Session Plan",
        "",
        f"- Goal: {config.goal}",
        f"- Mode: {mode_label}",
        f"- Output depth: {depth}",
        f"- Planning budget: {planning} min (<= 5% with cap)",
        f"- Soft deadline: {fmt_time(soft)}",
        f"- Hard deadline: {fmt_time(hard)}",
        f"- Buffer: {buffer} min ({fmt_time(buffer_start)}-{fmt_time(hard)})",
        f"- Minimum deliverable: a usable version of the core goal before {fmt_time(soft)}",
        "",
        "## Milestones",
        "",
        "| Time | Task | Deliverable | Acceptance criteria |",
        "|---|---|---|---|",
    ]
    if config.buffer_extra_percent > 0:
        reason = f" ({config.buffer_reason})" if config.buffer_reason else ""
        lines.insert(9, f"- Adaptive buffer adjustment: +{config.buffer_extra_percent:.0f}%{reason}")
    for start, end, task, deliverable, criteria in milestones:
        lines.append(f"| {fmt_time(start)}-{fmt_time(end)} | {task} | {deliverable} | {criteria} |")

    lines.extend(
        [
            "",
            "## Delay Response",
            "",
            "- Light delay: compress buffer, keep the core goal.",
            "- Moderate delay: drop optional material and move to the minimum deliverable.",
            "- Severe delay: stop exploration and finish the smallest complete artifact.",
            "",
            "## First Action",
            "",
            f"Start with: {milestones[0][2].lower()} for the first planned block.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a work-session plan.")
    parser.add_argument("--start", required=True, help="Start time in HH:MM.")
    parser.add_argument("--minutes", required=True, type=int, help="Available work minutes.")
    parser.add_argument("--goal", required=True, help="Work-session goal.")
    parser.add_argument(
        "--mode",
        default="mixed",
        choices=sorted(MODE_LABELS),
        help="Work mode.",
    )
    parser.add_argument("--hard-deadline", help="Hard deadline in HH:MM. Defaults to start + minutes.")
    parser.add_argument("--risk", default="normal", choices=["normal", "high"], help="Task risk level.")
    parser.add_argument("--buffer-extra-percent", default=0.0, type=float, help="Additional buffer percentage points.")
    parser.add_argument("--buffer-reason", default="", help="Reason shown when adaptive buffer is applied.")
    args = parser.parse_args()

    start = parse_time(args.start)
    config = PlanConfig(
        start=start,
        minutes=args.minutes,
        goal=args.goal,
        mode=args.mode,
        hard_deadline=parse_optional_time(args.hard_deadline, start),
        risk=args.risk,
        buffer_extra_percent=args.buffer_extra_percent,
        buffer_reason=args.buffer_reason,
    )
    print(generate_plan(config))


if __name__ == "__main__":
    main()
