#!/usr/bin/env python3
"""Inspect local context for open tasks and estimate work time."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from classify_work_mode import classify_work_mode
from estimate_profile import build_profile


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".daily-work-planner",
}
TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".go",
    ".rs",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".html",
    ".css",
}
BASE_MODE_MINUTES = {
    "reading": 75,
    "writing": 120,
    "revision": 90,
    "code": 110,
    "ppt": 120,
    "exam": 150,
    "data": 105,
    "research": 150,
    "literature": 150,
    "application": 120,
    "translation": 90,
    "meeting": 60,
    "lab": 120,
    "admin": 45,
    "design": 120,
    "mixed": 90,
}
SPEED_MULTIPLIERS = {"fast": 0.80, "normal": 1.00, "slow": 1.25}


@dataclass
class TaskCandidate:
    title: str
    source: str
    mode: str
    priority: str
    estimate_minutes: int
    confidence: float
    evidence: str
    path: str = ""
    line: int | None = None


@dataclass
class TaskInspection:
    repo: str
    tasks: list[TaskCandidate]
    estimated_total_minutes: int
    speed: str
    timing_multiplier: float
    notes: list[str]


def round_to_five(minutes: float) -> int:
    return max(5, int(round(minutes / 5.0) * 5))


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def read_memory_ratios(memory_dir: str | Path | None) -> dict[str, list[float]]:
    if not memory_dir:
        return {}
    path = Path(memory_dir) / "memory.jsonl"
    if not path.exists():
        return {}
    ratios: dict[str, list[float]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        planned = entry.get("planned_minutes")
        actual = entry.get("actual_minutes")
        mode = str(entry.get("mode") or "mixed").lower()
        if isinstance(planned, int) and isinstance(actual, int) and planned > 0:
            ratios.setdefault(mode, []).append((actual - planned) / planned)
    return ratios


def timing_multiplier_for(mode: str, profile_logs: list[str] | None, memory_dir: str | Path | None) -> float:
    ratios: list[float] = []
    if profile_logs:
        for item in build_profile(profile_logs):
            if item.mode == mode:
                ratios.append(item.average_delta_ratio)
    ratios.extend(read_memory_ratios(memory_dir).get(mode, []))
    if not ratios:
        return 1.0
    average = sum(ratios) / len(ratios)
    return 1.0 + clamp(average, -0.25, 0.50)


def estimate_goal_minutes(
    goal: str,
    mode: str = "mixed",
    file_count: int = 0,
    task_count: int = 0,
    speed: str = "normal",
    profile_logs: list[str] | None = None,
    memory_dir: str | Path | None = None,
) -> int:
    text = goal.lower()
    estimate = BASE_MODE_MINUTES.get(mode, BASE_MODE_MINUTES["mixed"])
    if any(word in text for word in ("quick", "brief", "small", "minor", "简单", "快速", "小")):
        estimate *= 0.65
    if any(word in text for word in ("full", "complete", "final", "deep", "完整", "最终", "深入")):
        estimate *= 1.35
    if any(word in text for word in ("debug", "bug", "fix", "test", "报错", "修复")):
        estimate += 30
    if any(word in text for word in ("论文", "paper", "manuscript", "report", "报告")):
        estimate += 35
    estimate += min(file_count, 8) * 10
    estimate += min(task_count, 10) * 15
    estimate *= SPEED_MULTIPLIERS.get(speed, 1.0)
    estimate *= timing_multiplier_for(mode, profile_logs, memory_dir)
    return round_to_five(clamp(estimate, 20, 480))


def estimate_candidate(title: str, source: str, mode: str, speed: str, timing_multiplier: float) -> int:
    base = {
        "current-window": 45,
        "git-status": 35,
        "todo-marker": 30,
        "markdown-checkbox": 25,
    }.get(source, 30)
    if mode in {"code", "data", "research", "literature", "ppt", "design"}:
        base += 20
    if any(word in title.lower() for word in ("fix", "debug", "bug", "fail", "error", "修复", "报错")):
        base += 25
    if any(word in title.lower() for word in ("write", "draft", "full", "complete", "最终", "完整")):
        base += 25
    return round_to_five(base * SPEED_MULTIPLIERS.get(speed, 1.0) * timing_multiplier)


def iter_text_files(root: Path, max_files: int) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if len(paths) >= max_files:
            break
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            paths.append(path)
    return paths


def safe_read(path: Path, max_bytes: int = 120_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_bytes]
    except OSError:
        return ""


def git_status_tasks(root: Path, speed: str, profile_logs: list[str] | None, memory_dir: str | Path | None) -> list[TaskCandidate]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    tasks: list[TaskCandidate] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or "changed"
        raw_path = line[3:].strip()
        path_name = raw_path.split(" -> ")[-1]
        mode = classify_work_mode(f"Resolve {status} changes", [path_name]).mode
        multiplier = timing_multiplier_for(mode, profile_logs, memory_dir)
        title = f"Resolve {status} changes in {path_name}"
        tasks.append(
            TaskCandidate(
                title=title,
                source="git-status",
                mode=mode,
                priority="A" if status in {"M", "A", "D", "??"} else "B",
                estimate_minutes=estimate_candidate(title, "git-status", mode, speed, multiplier),
                confidence=0.75,
                evidence=f"git status: {line}",
                path=path_name,
            )
        )
    return tasks


def window_note_tasks(
    note: str,
    speed: str,
    profile_logs: list[str] | None,
    memory_dir: str | Path | None,
) -> list[TaskCandidate]:
    tasks: list[TaskCandidate] = []
    for raw in note.splitlines():
        line = raw.strip(" -\t")
        if not line:
            continue
        if line.lower().startswith(("[x]", "done:", "completed:")):
            continue
        mode = classify_work_mode(line, []).mode
        multiplier = timing_multiplier_for(mode, profile_logs, memory_dir)
        tasks.append(
            TaskCandidate(
                title=line[:120],
                source="current-window",
                mode=mode,
                priority="A",
                estimate_minutes=estimate_candidate(line, "current-window", mode, speed, multiplier),
                confidence=0.70,
                evidence="provided current-window note",
            )
        )
    return tasks


def marker_tasks(
    root: Path,
    speed: str,
    profile_logs: list[str] | None,
    memory_dir: str | Path | None,
    max_files: int,
    max_markers: int,
) -> list[TaskCandidate]:
    tasks: list[TaskCandidate] = []
    marker_pattern = re.compile(r"^\s*(?:[#/;*]+\s*)?(TODO|FIXME|HACK|XXX)(?:\s*[:\-]\s*|\s+)(.*)")
    checkbox_pattern = re.compile(r"^\s*[-*]\s+\[\s\]\s+(.+)")
    for path in iter_text_files(root, max_files):
        rel = str(path.relative_to(root))
        text = safe_read(path)
        for index, line in enumerate(text.splitlines(), start=1):
            if len(tasks) >= max_markers:
                return tasks
            marker = marker_pattern.search(line)
            checkbox = checkbox_pattern.search(line)
            if not marker and not checkbox:
                continue
            title = (checkbox.group(1) if checkbox else marker.group(2)).strip() or line.strip()
            source = "markdown-checkbox" if checkbox else "todo-marker"
            mode = classify_work_mode(title, [rel]).mode
            multiplier = timing_multiplier_for(mode, profile_logs, memory_dir)
            priority = "A" if any(word in title.lower() for word in ("must", "urgent", "fix", "block", "必须", "紧急")) else "B"
            tasks.append(
                TaskCandidate(
                    title=title[:120],
                    source=source,
                    mode=mode,
                    priority=priority,
                    estimate_minutes=estimate_candidate(title, source, mode, speed, multiplier),
                    confidence=0.65 if source == "todo-marker" else 0.70,
                    evidence=line.strip()[:180],
                    path=rel,
                    line=index,
                )
            )
    return tasks


def dedupe_tasks(tasks: list[TaskCandidate]) -> list[TaskCandidate]:
    seen: set[tuple[str, str, int | None]] = set()
    result: list[TaskCandidate] = []
    for task in tasks:
        key = (task.title.lower(), task.path, task.line)
        if key in seen:
            continue
        seen.add(key)
        result.append(task)
    priority_order = {"A": 0, "B": 1, "C": 2}
    return sorted(result, key=lambda item: (priority_order.get(item.priority, 9), -item.confidence, item.estimate_minutes))


def estimate_total(tasks: list[TaskCandidate], fallback_goal: str, speed: str, profile_logs: list[str] | None, memory_dir: str | Path | None) -> int:
    if tasks:
        selected = tasks[:12]
        total = sum(task.estimate_minutes for task in selected)
        if len(selected) > 1:
            total += 10
        return round_to_five(clamp(total, 15, 480))
    if fallback_goal:
        mode = classify_work_mode(fallback_goal, []).mode
        return estimate_goal_minutes(fallback_goal, mode=mode, speed=speed, profile_logs=profile_logs, memory_dir=memory_dir)
    return 0


def inspect_tasks(
    repo: str | Path = ".",
    window_note: str = "",
    goal: str = "",
    speed: str = "normal",
    profile_logs: list[str] | None = None,
    memory_dir: str | Path | None = ".daily-work-planner",
    max_files: int = 200,
    max_markers: int = 50,
) -> TaskInspection:
    root = Path(repo).resolve()
    profile_logs = profile_logs or []
    tasks = []
    tasks.extend(window_note_tasks(window_note, speed, profile_logs, memory_dir))
    if root.exists():
        tasks.extend(git_status_tasks(root, speed, profile_logs, memory_dir))
        tasks.extend(marker_tasks(root, speed, profile_logs, memory_dir, max_files, max_markers))
    tasks = dedupe_tasks(tasks)
    dominant_mode = tasks[0].mode if tasks else classify_work_mode(goal, []).mode
    return TaskInspection(
        repo=str(root),
        tasks=tasks,
        estimated_total_minutes=estimate_total(tasks, goal, speed, profile_logs, memory_dir),
        speed=speed,
        timing_multiplier=timing_multiplier_for(dominant_mode, profile_logs, memory_dir),
        notes=[
            "Current-window access is represented by --window-note; scripts do not read private OS windows by themselves.",
            "Estimates are heuristic and become more accurate after review logs or local memory accumulate.",
        ],
    )


def render_markdown(inspection: TaskInspection) -> str:
    lines = [
        "# Task Inspection",
        "",
        f"- Repo: {inspection.repo}",
        f"- Open tasks found: {len(inspection.tasks)}",
        f"- Estimated total: {inspection.estimated_total_minutes} min" if inspection.estimated_total_minutes else "- Estimated total: none",
        f"- Speed profile: {inspection.speed}",
        f"- Timing multiplier: {inspection.timing_multiplier:.2f}",
        "",
    ]
    if not inspection.tasks:
        lines.extend(
            [
                "No open tasks were found from the current-window note, git status, unchecked Markdown tasks, or TODO/FIXME markers.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "| Priority | Task | Mode | Source | Estimate | Evidence |",
                "|---|---|---|---|---:|---|",
            ]
        )
        for task in inspection.tasks:
            location = f"{task.path}:{task.line}" if task.line else task.path
            evidence = task.evidence.replace("|", "/")
            source = f"{task.source} {location}".strip()
            lines.append(f"| {task.priority} | {task.title} | {task.mode} | {source} | {task.estimate_minutes} | {evidence} |")
        lines.append("")
    lines.extend(["## Notes", ""])
    for note in inspection.notes:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect current/local tasks and estimate required time.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--goal", default="")
    parser.add_argument("--window-note", default="", help="Text copied from the current work window or prompt.")
    parser.add_argument("--speed", choices=sorted(SPEED_MULTIPLIERS), default="normal")
    parser.add_argument("--profile-log", action="append", default=[])
    parser.add_argument("--memory-dir", default=".daily-work-planner")
    parser.add_argument("--max-files", type=int, default=200)
    parser.add_argument("--max-markers", type=int, default=50)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    result = inspect_tasks(
        repo=args.repo,
        window_note=args.window_note,
        goal=args.goal,
        speed=args.speed,
        profile_logs=args.profile_log,
        memory_dir=args.memory_dir,
        max_files=args.max_files,
        max_markers=args.max_markers,
    )
    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result), end="")


if __name__ == "__main__":
    main()
