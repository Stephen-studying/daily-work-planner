# Daily Work Planner Repository Instructions

This repository contains a portable work-session planning skill. The installable skill folder is `daily-work-planner/`.

When using this repository as an agent skill source:

- For Codex or OpenAI-compatible skill loaders, use `daily-work-planner/SKILL.md`.
- For generic agents that read `AGENTS.md`, use `daily-work-planner/AGENTS.md`.
- For command-line use, run `python -m daily_work_planner --help` from the repository root after installing the package in editable mode.

When modifying the repository:

- Keep `daily-work-planner/SKILL.md` as the Codex/OpenAI skill entrypoint.
- Keep `daily-work-planner/AGENTS.md` as the generic agent entrypoint.
- Keep scripts dependency-light and runnable with the Python standard library when possible.
- Run `python -B -m unittest discover -s tests` before committing.
- Do not commit generated `outputs/`, `.daily-work-planner/`, `work-session/`, `.ics`, logs, or review logs.

