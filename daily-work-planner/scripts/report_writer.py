#!/usr/bin/env python3
"""Write consolidated Daily Work Planner reports as TXT and DOCX."""

from __future__ import annotations

import argparse
import html
import re
import zipfile
from pathlib import Path


def markdown_to_plain_text(sections: list[tuple[str, str]]) -> str:
    parts: list[str] = ["Daily Work Planner Report", ""]
    for title, body in sections:
        parts.extend([title, "=" * len(title), "", body.strip(), ""])
    return "\n".join(parts).rstrip() + "\n"


def paragraph_style(line: str) -> tuple[str, str]:
    if line.startswith("# "):
        return "Heading1", line[2:].strip()
    if line.startswith("## "):
        return "Heading2", line[3:].strip()
    if line.startswith("### "):
        return "Heading3", line[4:].strip()
    return "Normal", line


def strip_markdown_table_separator(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and set(stripped.replace("|", "").strip()) <= {"-", ":"}


def clean_line(line: str) -> str:
    line = line.replace("`", "")
    return line.rstrip()


def docx_paragraph(text: str, style: str = "Normal") -> str:
    safe = html.escape(text)
    style_xml = "" if style == "Normal" else f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
    return f"<w:p>{style_xml}<w:r><w:t xml:space=\"preserve\">{safe}</w:t></w:r></w:p>"


def markdown_to_docx_body(markdown: str) -> str:
    paragraphs: list[str] = []
    in_fence = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if strip_markdown_table_separator(line):
            continue
        if not line.strip():
            paragraphs.append("<w:p/>")
            continue
        if in_fence:
            paragraphs.append(docx_paragraph(clean_line(line), "Code"))
            continue
        style, text = paragraph_style(clean_line(line))
        if line.strip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            text = " | ".join(cells)
        text = re.sub(r"^\s*[-*]\s+", "- ", text)
        paragraphs.append(docx_paragraph(text, style))
    return "".join(paragraphs)


def content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="160"/></w:pPr><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="120"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>
"""


def core_xml(title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>{html.escape(title)}</dc:title>
  <dc:creator>Daily Work Planner</dc:creator>
</cp:coreProperties>
"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>Daily Work Planner</Application>
</Properties>
"""


def document_xml(markdown: str) -> str:
    body = markdown_to_docx_body(markdown)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
  </w:body>
</w:document>
"""


def write_docx(path: str | Path, markdown: str, title: str = "Daily Work Planner Report") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml())
        archive.writestr("_rels/.rels", rels_xml())
        archive.writestr("word/_rels/document.xml.rels", document_rels_xml())
        archive.writestr("word/document.xml", document_xml(markdown))
        archive.writestr("word/styles.xml", styles_xml())
        archive.writestr("docProps/core.xml", core_xml(title))
        archive.writestr("docProps/app.xml", app_xml())


def write_txt(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write TXT and DOCX reports from Markdown.")
    parser.add_argument("--input", required=True, help="Markdown input file.")
    parser.add_argument("--txt-output")
    parser.add_argument("--docx-output")
    parser.add_argument("--title", default="Daily Work Planner Report")
    args = parser.parse_args()

    markdown = Path(args.input).read_text(encoding="utf-8")
    if args.txt_output:
        write_txt(args.txt_output, markdown)
    if args.docx_output:
        write_docx(args.docx_output, markdown, args.title)


if __name__ == "__main__":
    main()
