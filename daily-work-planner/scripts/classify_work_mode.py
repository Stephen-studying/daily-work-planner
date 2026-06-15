#!/usr/bin/env python3
"""Classify a work-session goal into a Daily Work Planner mode."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


MODE_KEYWORDS = {
    "reading": {
        "read", "reading", "pdf", "paper", "papers", "article", "articles",
        "book", "textbook", "document", "literature", "skim", "scan",
    },
    "writing": {
        "write", "writing", "draft", "essay", "report", "proposal",
        "manuscript", "abstract", "introduction", "discussion", "outline",
    },
    "revision": {
        "revise", "revision", "edit", "polish", "proofread", "format",
        "word", "docx", "submission", "finalize", "comments",
    },
    "code": {
        "code", "debug", "bug", "fix", "feature", "test", "refactor",
        "implement", "compile", "run", "script", "api",
    },
    "ppt": {
        "ppt", "slides", "presentation", "deck", "talk", "defense",
        "seminar", "speaker", "group meeting",
    },
    "exam": {
        "exam", "review", "memorize", "practice", "quiz", "test",
        "course", "problem set", "flashcard",
    },
    "data": {
        "data", "excel", "spreadsheet", "csv", "table", "dataset",
        "organize", "clean", "chart", "figure", "analysis",
    },
    "research": {
        "research", "hypothesis", "method", "methods", "experiment", "protocol",
        "result", "results", "lab", "survey", "dataset", "evidence",
    },
    "literature": {
        "literature", "review", "citation", "citations", "references",
        "bibliography", "related", "doi", "pubmed", "zotero", "endnote",
    },
    "application": {
        "application", "resume", "cv", "personal", "statement", "sop",
        "portfolio", "cover", "recommendation", "scholarship",
    },
    "translation": {
        "translate", "translation", "bilingual", "english", "chinese",
        "polish", "localize", "rewrite",
    },
    "meeting": {
        "meeting", "agenda", "minutes", "standup", "sync", "interview",
        "discussion", "briefing", "follow-up", "followup",
    },
    "lab": {
        "lab", "experiment", "sample", "protocol", "instrument", "measurement",
        "assay", "reagent", "record", "notebook",
    },
    "admin": {
        "admin", "email", "emails", "form", "forms", "submit", "submission",
        "invoice", "receipt", "schedule", "appointment", "paperwork",
    },
    "design": {
        "design", "prototype", "wireframe", "mockup", "figma", "ui", "ux",
        "layout", "visual", "brand", "creative",
    },
}


EXTENSION_HINTS = {
    ".pdf": "reading",
    ".docx": "revision",
    ".doc": "revision",
    ".ppt": "ppt",
    ".pptx": "ppt",
    ".xlsx": "data",
    ".xls": "data",
    ".csv": "data",
    ".tsv": "data",
    ".bib": "literature",
    ".ris": "literature",
    ".nbib": "literature",
    ".py": "code",
    ".js": "code",
    ".jsx": "code",
    ".ts": "code",
    ".tsx": "code",
    ".java": "code",
    ".cpp": "code",
    ".c": "code",
    ".go": "code",
    ".rs": "code",
}


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
class ModeResult:
    mode: str
    label: str
    confidence: float
    scores: dict[str, int]
    reasons: list[str]


def tokenize(value: str) -> set[str]:
    normalized = value.lower().replace("_", " ").replace("-", " ")
    return {token.strip(".,;:!?()[]{}\"'") for token in normalized.split() if token.strip()}


def classify_work_mode(goal: str, paths: list[str] | None = None) -> ModeResult:
    paths = paths or []
    text = " ".join([goal] + [Path(path).name for path in paths]).lower()
    tokens = tokenize(text)
    scores = {mode: 0 for mode in MODE_KEYWORDS}
    reasons: list[str] = []

    for mode, keywords in MODE_KEYWORDS.items():
        for keyword in keywords:
            if " " in keyword:
                if keyword in text:
                    scores[mode] += 3
                    reasons.append(f"{mode}: phrase '{keyword}' matched")
            elif keyword in tokens:
                scores[mode] += 2
                reasons.append(f"{mode}: keyword '{keyword}' matched")

    for raw_path in paths:
        suffix = Path(raw_path).suffix.lower()
        hinted_mode = EXTENSION_HINTS.get(suffix)
        if hinted_mode:
            scores[hinted_mode] += 2
            reasons.append(f"{hinted_mode}: extension '{suffix}' matched")

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_mode, top_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else 0
    if top_score == 0:
        return ModeResult("mixed", MODE_LABELS["mixed"], 0.35, scores, ["No strong mode signal found."])
    if second_score and top_score - second_score <= 1:
        return ModeResult("mixed", MODE_LABELS["mixed"], 0.55, scores, ["Multiple modes are close; using mixed mode."] + reasons[:8])
    confidence = min(0.95, 0.55 + (top_score - second_score) * 0.08)
    return ModeResult(top_mode, MODE_LABELS[top_mode], confidence, scores, reasons[:10])


def render_markdown(result: ModeResult) -> str:
    lines = [
        "# Work Mode Classification",
        "",
        f"- Mode: {result.mode}",
        f"- Label: {result.label}",
        f"- Confidence: {result.confidence:.2f}",
        "",
        "## Scores",
        "",
        "| Mode | Score |",
        "|---|---:|",
    ]
    for mode, score in sorted(result.scores.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {mode} | {score} |")
    lines.extend(["", "## Reasons", ""])
    for reason in result.reasons:
        lines.append(f"- {reason}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify a Daily Work Planner work mode.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    result = classify_work_mode(args.goal, args.paths)
    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result), end="")


if __name__ == "__main__":
    main()
