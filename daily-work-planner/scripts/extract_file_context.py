#!/usr/bin/env python3
"""Extract lightweight planning context from local files.

The script is designed for work-session preflight. It intentionally avoids
deep summarization and returns only enough context to help decide priority,
scope, and first actions.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".csv",
    ".tsv",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".rst",
}

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".sh",
    ".ps1",
}

SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | CODE_EXTENSIONS | {".pdf", ".docx"}


@dataclass
class FileContext:
    path: str
    file_type: str
    size_bytes: int
    modified: str
    title: str | None = None
    page_count: int | None = None
    paragraph_count: int | None = None
    table_count: int | None = None
    headings: list[str] = field(default_factory=list)
    code_symbols: list[str] = field(default_factory=list)
    sample: str = ""
    extraction_method: str = "metadata"
    warnings: list[str] = field(default_factory=list)


def normalize_text(value: str, limit: int | None = None) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    value = value.strip()
    if limit is not None and len(value) > limit:
        return value[:limit].rstrip() + "..."
    return value


def read_text_best_effort(path: Path, max_chars: int) -> tuple[str, str]:
    encodings = ["utf-8-sig", "utf-8", "gb18030", "latin-1"]
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding, errors="strict")[:max_chars], encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")[:max_chars], "utf-8-replace"


def base_context(path: Path) -> FileContext:
    stat = path.stat()
    return FileContext(
        path=str(path),
        file_type=path.suffix.lower().lstrip(".") or "unknown",
        size_bytes=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
    )


def extract_markdown_headings(text: str, limit: int = 12) -> list[str]:
    headings = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(f"{match.group(1)} {match.group(2)}")
        if len(headings) >= limit:
            break
    return headings


def extract_code_symbols(text: str, suffix: str, limit: int = 20) -> list[str]:
    patterns = [
        r"^\s*(?:async\s+)?def\s+([A-Za-z_][\w]*)\s*\(",
        r"^\s*class\s+([A-Za-z_][\w]*)\b",
        r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(",
        r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(",
        r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:class|interface|enum)\s+([A-Za-z_][\w]*)\b",
        r"^\s*func\s+([A-Za-z_][\w]*)\s*\(",
        r"^\s*fn\s+([A-Za-z_][\w]*)\s*\(",
        r"^\s*CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW|FUNCTION|PROCEDURE)\s+([^\s(]+)",
    ]
    symbols = []
    for line in text.splitlines():
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                symbols.append(match.group(1))
                break
        if len(symbols) >= limit:
            break
    return symbols


def extract_text_file(path: Path, max_chars: int) -> FileContext:
    context = base_context(path)
    text, encoding = read_text_best_effort(path, max_chars * 3)
    context.extraction_method = f"text:{encoding}"
    context.title = path.stem
    if path.suffix.lower() in {".md", ".markdown"}:
        context.headings = extract_markdown_headings(text)
    if path.suffix.lower() in CODE_EXTENSIONS:
        context.code_symbols = extract_code_symbols(text, path.suffix.lower())
    context.sample = normalize_text(text, max_chars)
    return context


def xml_text(element: ElementTree.Element) -> str:
    return "".join(element.itertext()).strip()


def extract_docx(path: Path, max_chars: int) -> FileContext:
    context = base_context(path)
    context.extraction_method = "docx:zip-xml"
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "dc": "http://purl.org/dc/elements/1.1/",
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    }
    paragraphs: list[str] = []
    headings: list[str] = []

    try:
        with zipfile.ZipFile(path) as archive:
            if "docProps/core.xml" in archive.namelist():
                root = ElementTree.fromstring(archive.read("docProps/core.xml"))
                title = root.find("dc:title", ns)
                if title is not None and title.text:
                    context.title = title.text.strip()

            root = ElementTree.fromstring(archive.read("word/document.xml"))
            context.table_count = len(root.findall(".//w:tbl", ns))
            for paragraph in root.findall(".//w:p", ns):
                text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
                if not text:
                    continue
                paragraphs.append(text)
                style_node = paragraph.find(".//w:pStyle", ns)
                style = style_node.attrib.get(f"{{{ns['w']}}}val", "") if style_node is not None else ""
                if style.lower().startswith("heading") and len(headings) < 12:
                    headings.append(text)
    except (KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        context.warnings.append(f"Could not parse DOCX XML: {exc}")

    context.paragraph_count = len(paragraphs)
    context.headings = headings
    context.sample = normalize_text("\n".join(paragraphs[:80]), max_chars)
    if context.title is None:
        context.title = path.stem
    return context


def try_extract_pdf_with_library(path: Path, max_chars: int, context: FileContext) -> bool:
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
        except ImportError:
            continue
        try:
            reader = module.PdfReader(str(path))
            context.page_count = len(reader.pages)
            metadata = getattr(reader, "metadata", None) or {}
            title = getattr(metadata, "title", None) or metadata.get("/Title") if hasattr(metadata, "get") else None
            if title:
                context.title = str(title).strip()
            chunks = []
            for page in reader.pages[:5]:
                try:
                    chunks.append(page.extract_text() or "")
                except Exception as exc:  # pragma: no cover - defensive around PDF backends
                    context.warnings.append(f"Page text extraction failed: {exc}")
            context.sample = normalize_text("\n".join(chunks), max_chars)
            context.extraction_method = f"pdf:{module_name}"
            return True
        except Exception as exc:  # pragma: no cover - defensive around PDF backends
            context.warnings.append(f"{module_name} failed: {exc}")
    return False


def pdf_literal_to_text(value: bytes) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError:
        text = value.decode("latin-1", errors="replace")
    return text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")


def extract_pdf_fallback(path: Path, max_chars: int, context: FileContext) -> None:
    data = path.read_bytes()
    context.page_count = len(re.findall(rb"/Type\s*/Page\b", data))
    title_match = re.search(rb"/Title\s*\((.*?)\)", data, re.DOTALL)
    if title_match:
        context.title = normalize_text(pdf_literal_to_text(title_match.group(1)), 200)
    text_matches = re.findall(rb"\(([^()]{3,200})\)\s*Tj", data)
    text_matches.extend(re.findall(rb"\(([^()]{3,200})\)", data[: min(len(data), 300_000)]))
    sample = "\n".join(pdf_literal_to_text(item) for item in text_matches[:80])
    context.sample = normalize_text(sample, max_chars)
    context.extraction_method = "pdf:fallback-metadata"
    if not context.sample:
        context.warnings.append("No PDF text extracted without pypdf/PyPDF2; only metadata is reliable.")


def extract_pdf(path: Path, max_chars: int) -> FileContext:
    context = base_context(path)
    if not try_extract_pdf_with_library(path, max_chars, context):
        extract_pdf_fallback(path, max_chars, context)
    if context.title is None:
        context.title = path.stem
    return context


def extract_context(path: Path, max_chars: int) -> FileContext:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path, max_chars)
    if suffix == ".docx":
        return extract_docx(path, max_chars)
    if suffix in TEXT_EXTENSIONS or suffix in CODE_EXTENSIONS:
        return extract_text_file(path, max_chars)
    context = base_context(path)
    context.title = path.stem
    context.warnings.append("Unsupported extension; metadata only.")
    return context


def expand_inputs(values: list[str], recursive: bool, max_files: int) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        expanded = glob.glob(value)
        candidates = expanded if expanded else [value]
        for candidate in candidates:
            path = Path(candidate)
            if path.is_dir():
                iterator: Iterable[Path] = path.rglob("*") if recursive else path.iterdir()
                for child in iterator:
                    if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
                        paths.append(child)
            elif path.is_file():
                paths.append(path)
    unique = []
    seen = set()
    for path in paths:
        resolved = str(path.resolve())
        if resolved not in seen:
            unique.append(path)
            seen.add(resolved)
        if len(unique) >= max_files:
            break
    return unique


def render_markdown(contexts: list[FileContext]) -> str:
    lines = ["# File Context", ""]
    if not contexts:
        lines.append("No supported files found.")
        return "\n".join(lines)

    for index, context in enumerate(contexts, start=1):
        lines.extend(
            [
                f"## {index}. {Path(context.path).name}",
                "",
                f"- Path: `{context.path}`",
                f"- Type: {context.file_type}",
                f"- Size: {context.size_bytes} bytes",
                f"- Modified: {context.modified}",
                f"- Extraction: {context.extraction_method}",
            ]
        )
        if context.title:
            lines.append(f"- Title: {context.title}")
        if context.page_count is not None:
            lines.append(f"- Pages: {context.page_count}")
        if context.paragraph_count is not None:
            lines.append(f"- Paragraphs: {context.paragraph_count}")
        if context.table_count is not None:
            lines.append(f"- Tables: {context.table_count}")
        if context.headings:
            lines.append("- Headings:")
            for heading in context.headings:
                lines.append(f"  - {heading}")
        if context.code_symbols:
            lines.append("- Code symbols:")
            for symbol in context.code_symbols:
                lines.append(f"  - {symbol}")
        if context.sample:
            lines.extend(["", "Sample:", "", "```text", context.sample, "```"])
        if context.warnings:
            lines.append("- Warnings:")
            for warning in context.warnings:
                lines.append(f"  - {warning}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract lightweight planning context from files.")
    parser.add_argument("paths", nargs="+", help="Files, directories, or glob patterns.")
    parser.add_argument("--recursive", action="store_true", help="Scan directories recursively.")
    parser.add_argument("--max-files", type=int, default=30, help="Maximum files to inspect.")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximum sample characters per file.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="Optional output file path.")
    args = parser.parse_args()

    files = expand_inputs(args.paths, args.recursive, args.max_files)
    contexts = [extract_context(path, args.max_chars) for path in files]
    if args.format == "json":
        output = json.dumps([asdict(context) for context in contexts], ensure_ascii=False, indent=2)
    else:
        output = render_markdown(contexts)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
