# Example: Complete Session Package

User prompt:

```text
Use $daily-work-planner to create a complete work-session package.
Goal: revise my report and prepare a final submission version.
Available time: 14:00-17:00.
Hard deadline: 17:00.
Files: report.docx, rubric.pdf, notes.md.
```

Useful command:

```powershell
python -m daily_work_planner start --goal "Revise my report and prepare final submission" --start 14:00 --minutes 180 --hard-deadline 17:00 .\report.docx .\rubric.pdf .\notes.md --output-dir .\work-session
```

Expected files:

- `session.ics`
- `session.json`
- `work_session.txt`
- `work_session.docx`

Add `--split-files` if separate Markdown helper files are also needed.
