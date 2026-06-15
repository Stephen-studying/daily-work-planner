# Example: File Context Extraction

User prompt:

```text
Use $daily-work-planner to inspect these files before planning:
paper-a.pdf, draft.docx, notes.md, and src/.
Keep inspection lightweight because I only have 2 hours.
```

Useful script command:

```powershell
python .\daily-work-planner\scripts\extract_file_context.py .\paper-a.pdf .\draft.docx .\notes.md .\src --recursive --max-files 20 --max-chars 1000 --format markdown
```

Expected output shape:

- PDF page count, title metadata when available, and short sample text when extraction is available
- DOCX title, paragraph count, table count, headings, and short sample text
- Markdown headings and text sample
- Code symbols such as classes, functions, and exported components
- Warnings when a file can only be inspected by metadata
