#!/usr/bin/env python3
"""Create a complete Daily Work Planner session package."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from classify_work_mode import classify_work_mode
from estimate_profile import build_profile
from extract_file_context import expand_inputs, extract_context, render_markdown as render_context_markdown
from feasibility_score import assess_feasibility, render_markdown as render_feasibility_markdown
from inspect_tasks import estimate_goal_minutes, inspect_tasks, render_markdown as render_task_inspection_markdown
from make_ics import build_ics
from make_todo import parse_milestones, render_todo
from plan_day import PlanConfig, generate_plan, parse_optional_time, parse_time
from rank_files import rank_files, render_markdown as render_rank_markdown
from report_writer import write_docx, write_txt
from session_state import create_session, save_session
from validate_plan import render_markdown as render_validation_markdown, validate_plan


def today_iso() -> str:
    return datetime.now().date().isoformat()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def section(title: str, body: str) -> str:
    body = body.strip()
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        body = "\n".join(lines[1:]).strip()
    return "\n".join([f"# {title}", "", body.strip(), ""])


def adaptive_buffer_from_logs(mode: str, log_paths: list[str]) -> dict:
    if not log_paths:
        return {"extra_percent": 0, "reason": "no profile logs supplied"}
    stats = build_profile(log_paths)
    normalized = mode.lower().replace(" mode", "").replace(" ", "-")
    for item in stats:
        if item.mode == normalized:
            ratio = item.average_delta_ratio
            if ratio > 0.20:
                return {
                    "extra_percent": 10,
                    "reason": f"history shows {mode} sessions run {ratio:.0%} over plan",
                }
            if ratio > 0.05:
                return {
                    "extra_percent": 5,
                    "reason": f"history shows {mode} sessions run {ratio:.0%} over plan",
                }
            return {"extra_percent": 0, "reason": f"history for {mode} is close to plan"}
    return {"extra_percent": 0, "reason": f"no matching history for {mode}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a complete work-session package.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--start", required=True, help="Start time in HH:MM.")
    parser.add_argument("--minutes", type=int, help="Available work minutes. If omitted, estimate from goal, files, repo tasks, and history.")
    parser.add_argument("--hard-deadline", help="Hard deadline in HH:MM. Defaults to start + minutes.")
    parser.add_argument("--mode", default="auto")
    parser.add_argument("--risk", default="normal", choices=["normal", "high"])
    parser.add_argument("--speed", default="normal", choices=["fast", "normal", "slow"], help="User speed profile used when estimating missing minutes.")
    parser.add_argument("--date", default=today_iso(), help="Date for ICS events: YYYY-MM-DD.")
    parser.add_argument("--alarm-minutes", type=int, default=10)
    parser.add_argument("--output-dir", default="work-session")
    parser.add_argument("--repo", default=".", help="Repository path to inspect when --scan-repo is used.")
    parser.add_argument("--scan-repo", action="store_true", help="Inspect local repo tasks from git status, TODO/FIXME markers, and Markdown checkboxes.")
    parser.add_argument("--window-note", default="", help="Text copied from the current work window or current user task.")
    parser.add_argument("--memory-dir", default=".daily-work-planner", help="Local task memory directory for timing habits.")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--max-files", type=int, default=30)
    parser.add_argument("--profile-log", action="append", default=[], help="Review log used to adapt buffer. Repeatable.")
    parser.add_argument("--split-files", action="store_true", help="Also write separate Markdown/todo helper files.")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    source_files = expand_inputs(args.files, args.recursive, args.max_files) if args.files else []
    mode = args.mode
    if mode == "auto":
        mode = classify_work_mode(args.goal, [str(path) for path in source_files]).mode
    adaptive_buffer = adaptive_buffer_from_logs(mode, args.profile_log)
    task_inspection = None
    if args.scan_repo or args.window_note:
        task_inspection = inspect_tasks(
            repo=args.repo,
            window_note=args.window_note,
            goal=args.goal,
            speed=args.speed,
            profile_logs=args.profile_log,
            memory_dir=args.memory_dir,
            max_files=max(args.max_files, 50),
        )

    minutes_were_estimated = args.minutes is None
    estimated_source = "user supplied --minutes"
    if args.minutes is None:
        if task_inspection and task_inspection.estimated_total_minutes:
            minutes = task_inspection.estimated_total_minutes
            estimated_source = "task inspection"
        else:
            minutes = estimate_goal_minutes(
                args.goal,
                mode=mode,
                file_count=len(source_files),
                speed=args.speed,
                profile_logs=args.profile_log,
                memory_dir=args.memory_dir,
            )
            estimated_source = "goal/files/history heuristic"
    else:
        minutes = args.minutes

    start = parse_time(args.start)
    hard_deadline = parse_optional_time(args.hard_deadline, start)
    hard_deadline_text = args.hard_deadline or (start + timedelta(minutes=minutes)).strftime("%H:%M")
    plan = generate_plan(
        PlanConfig(
            start=start,
            minutes=minutes,
            goal=args.goal,
            mode=mode,
            hard_deadline=hard_deadline,
            risk=args.risk,
            buffer_extra_percent=adaptive_buffer["extra_percent"],
            buffer_reason=adaptive_buffer["reason"],
        )
    )
    outputs: dict[str, str] = {}

    todo = render_todo(parse_milestones(plan))
    validation = render_validation_markdown(validate_plan(plan, minutes))
    feasibility_estimate = task_inspection.estimated_total_minutes if task_inspection and task_inspection.estimated_total_minutes else estimate_goal_minutes(
        args.goal,
        mode=mode,
        file_count=len(source_files),
        speed=args.speed,
        profile_logs=args.profile_log,
        memory_dir=args.memory_dir,
    )
    feasibility = assess_feasibility(
        goal=args.goal,
        available_minutes=minutes,
        estimated_minutes=feasibility_estimate,
        mode=mode,
        file_count=len(source_files),
        task_count=len(task_inspection.tasks) if task_inspection else 0,
        speed=args.speed,
        risk=args.risk,
    )
    file_context = ""
    file_priority = ""
    task_inspection_markdown = render_task_inspection_markdown(task_inspection) if task_inspection else ""
    review_template = "\n".join(
        [
            "# Work Session Review Log",
            "",
            f"## {args.date}",
            "",
            f"- Goal: {args.goal}",
            f"- Work mode: {mode}",
            f"- Planned minutes: {minutes}",
            "- Actual minutes:",
            "- Soft deadline met: yes/no",
            "- Hard deadline met: yes/no",
            "- Minimum deliverable completed: yes/no",
            "- Main delay reason:",
            "- Estimate adjustment for next time:",
            "",
        ]
    )

    if source_files:
        contexts = [extract_context(path, max_chars=1000) for path in source_files]
        file_context = render_context_markdown(contexts)
        ranked = rank_files(args.goal, [str(path) for path in source_files], mode=mode, recursive=False, max_files=args.max_files)
        file_priority = render_rank_markdown(ranked)

    report = "\n".join(
        [
            section("Session Summary", "\n".join([
                f"- Goal: {args.goal}",
                f"- Mode: {mode}",
                f"- Start: {args.start}",
                f"- Planned minutes: {minutes}" + (" (estimated)" if minutes_were_estimated else ""),
                f"- Estimation source: {estimated_source}",
                f"- Speed profile: {args.speed}",
                f"- Hard deadline: {hard_deadline_text}",
                f"- Adaptive buffer: +{adaptive_buffer['extra_percent']}% ({adaptive_buffer['reason']})",
            ])),
            section("Task Inspection", task_inspection_markdown or "Task inspection was not requested."),
            section("Feasibility", render_feasibility_markdown(feasibility)),
            section("Work Session Plan", plan),
            section("File Context", file_context or "No source files were provided."),
            section("File Priority", file_priority or "No source files were ranked."),
            section("Todo Checklist", todo),
            section("Plan Validation", validation),
            section("Review Template", review_template),
        ]
    )
    write_txt(output_dir / "work_session.txt", report)
    write_docx(output_dir / "work_session.docx", report, "Daily Work Planner Session")
    outputs["report_txt"] = "work_session.txt"
    outputs["report_docx"] = "work_session.docx"

    if args.split_files:
        write(output_dir / "session_plan.md", plan)
        outputs["session_plan"] = "session_plan.md"
        write(output_dir / "todo.txt", todo)
        outputs["todo"] = "todo.txt"
        write(output_dir / "plan_validation.md", validation)
        outputs["plan_validation"] = "plan_validation.md"
        if file_context:
            write(output_dir / "file_context.md", file_context)
            outputs["file_context"] = "file_context.md"
        if file_priority:
            write(output_dir / "file_priority.md", file_priority)
            outputs["file_priority"] = "file_priority.md"

    start_dt = datetime.strptime(f"{args.date}T{args.start}", "%Y-%m-%dT%H:%M")
    end_dt = start_dt + timedelta(minutes=minutes)
    if hard_deadline:
        end_dt = datetime.strptime(f"{args.date}T{hard_deadline.strftime('%H:%M')}", "%Y-%m-%dT%H:%M")
    ics = build_ics(
        title=f"Work session: {args.goal[:60]}",
        start=start_dt,
        end=end_dt,
        description="Generated by Daily Work Planner. See session_plan.md for milestones.",
        alarm_minutes=args.alarm_minutes,
    )
    write(output_dir / "session.ics", ics)
    outputs["ics"] = "session.ics"
    session = create_session(
        goal=args.goal,
        mode=mode,
        start=args.start,
        hard_deadline=hard_deadline_text,
        planned_minutes=minutes,
        files=[str(path) for path in source_files],
        outputs=outputs,
        adaptive_buffer=adaptive_buffer,
        estimation={
            "estimated": minutes_were_estimated,
            "source": estimated_source,
            "speed": args.speed,
        },
        task_inspection={
            "open_tasks": len(task_inspection.tasks) if task_inspection else 0,
            "estimated_total_minutes": task_inspection.estimated_total_minutes if task_inspection else 0,
        },
        feasibility={
            "score": feasibility.score,
            "level": feasibility.level,
            "recommended_scope": feasibility.recommended_scope,
            "estimated_minutes": feasibility.estimated_minutes,
        },
    )
    save_session(output_dir / "session.json", session)
    print(str(output_dir))


if __name__ == "__main__":
    main()
