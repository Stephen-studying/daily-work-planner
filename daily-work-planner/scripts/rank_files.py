#!/usr/bin/env python3
"""Rank local files for a work session."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from classify_work_mode import classify_work_mode
from extract_file_context import expand_inputs, extract_context


MODE_EXTENSION_WEIGHTS = {
    "reading": {".pdf": 8, ".md": 4, ".txt": 4, ".docx": 4},
    "writing": {".docx": 8, ".md": 7, ".txt": 5, ".pdf": 3},
    "revision": {".docx": 9, ".doc": 8, ".md": 5, ".pdf": 4},
    "code": {".py": 8, ".js": 8, ".jsx": 8, ".ts": 8, ".tsx": 8, ".java": 7, ".go": 7, ".rs": 7},
    "ppt": {".pptx": 9, ".ppt": 8, ".pdf": 5, ".docx": 4, ".md": 4},
    "exam": {".pdf": 7, ".docx": 5, ".md": 5, ".txt": 5},
    "data": {".xlsx": 9, ".xls": 8, ".csv": 8, ".tsv": 8, ".json": 5},
    "research": {".pdf": 7, ".docx": 5, ".md": 5, ".csv": 5, ".xlsx": 5},
    "literature": {".pdf": 8, ".bib": 8, ".ris": 8, ".nbib": 8, ".md": 5, ".docx": 4},
    "application": {".docx": 8, ".pdf": 5, ".md": 5, ".txt": 4},
    "translation": {".docx": 7, ".md": 7, ".txt": 6, ".pdf": 4},
    "meeting": {".pptx": 7, ".docx": 6, ".md": 6, ".txt": 5, ".pdf": 4},
    "lab": {".xlsx": 7, ".csv": 7, ".docx": 6, ".pdf": 5, ".md": 5},
    "admin": {".pdf": 7, ".docx": 7, ".xlsx": 5, ".txt": 4, ".md": 4},
    "design": {".pptx": 6, ".pdf": 5, ".md": 5, ".html": 5, ".css": 5},
    "mixed": {},
}


@dataclass
class RankedFile:
    path: str
    priority: str
    score: int
    role: str
    reasons: list[str]
    title: str | None
    file_type: str
    modified: str


def goal_terms(goal: str) -> set[str]:
    return {token.strip(".,;:!?()[]{}\"'").lower() for token in goal.split() if len(token.strip()) >= 3}


def priority_from_score(score: int) -> str:
    if score >= 14:
        return "A"
    if score >= 8:
        return "B"
    if score >= 4:
        return "C"
    return "D"


def role_from_priority(priority: str) -> str:
    return {
        "A": "primary",
        "B": "reference",
        "C": "optional",
        "D": "ignore-for-now",
    }[priority]


def rank_files(goal: str, paths: list[str], mode: str = "auto", recursive: bool = False, max_files: int = 30) -> list[RankedFile]:
    files = expand_inputs(paths, recursive=recursive, max_files=max_files)
    if mode == "auto":
        mode = classify_work_mode(goal, [str(path) for path in files]).mode
    terms = goal_terms(goal)
    now = time.time()
    ranked: list[RankedFile] = []

    for path in files:
        context = extract_context(path, max_chars=700)
        suffix = path.suffix.lower()
        text = " ".join(
            [
                path.name,
                context.title or "",
                " ".join(context.headings),
                " ".join(context.code_symbols),
                context.sample[:1000],
            ]
        ).lower()
        score = 0
        reasons: list[str] = []

        extension_score = MODE_EXTENSION_WEIGHTS.get(mode, {}).get(suffix, 0)
        if extension_score:
            score += extension_score
            reasons.append(f"extension fits {mode} mode (+{extension_score})")

        matches = sorted(term for term in terms if term and term in text)
        if matches:
            points = min(8, len(matches) * 2)
            score += points
            reasons.append(f"goal terms matched: {', '.join(matches[:5])} (+{points})")

        age_days = max(0, (now - path.stat().st_mtime) / 86400)
        if age_days <= 2:
            score += 3
            reasons.append("recently modified (+3)")
        elif age_days <= 14:
            score += 1
            reasons.append("modified within 14 days (+1)")

        if context.headings or context.code_symbols:
            score += 2
            reasons.append("structured content detected (+2)")
        if context.page_count is not None and context.page_count > 80:
            score -= 1
            reasons.append("large PDF, avoid deep planning read (-1)")
        if not reasons:
            reasons.append("weak direct signal")

        priority = priority_from_score(score)
        ranked.append(
            RankedFile(
                path=str(path),
                priority=priority,
                score=score,
                role=role_from_priority(priority),
                reasons=reasons,
                title=context.title,
                file_type=context.file_type,
                modified=context.modified,
            )
        )
    return sorted(ranked, key=lambda item: (item.priority, -item.score, item.path))


def render_markdown(items: list[RankedFile]) -> str:
    lines = [
        "# File Priority",
        "",
        "| Priority | Score | Role | File | Reason |",
        "|---|---:|---|---|---|",
    ]
    for item in items:
        reason = "; ".join(item.reasons[:3])
        lines.append(f"| {item.priority} | {item.score} | {item.role} | `{item.path}` | {reason} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank files for a work session.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--mode", default="auto")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--max-files", type=int, default=30)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    ranked = rank_files(args.goal, args.paths, args.mode, args.recursive, args.max_files)
    if args.format == "json":
        print(json.dumps([asdict(item) for item in ranked], ensure_ascii=False, indent=2))
    else:
        print(render_markdown(ranked), end="")


if __name__ == "__main__":
    main()
