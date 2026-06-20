# Daily Work Planner

<div align="center">

[简体中文](README.zh-CN.md) | English

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=for-the-badge)
![Agent Portable](https://img.shields.io/badge/Agent-Portable-DB2777?style=for-the-badge)
![Local First](https://img.shields.io/badge/Local--First-Privacy-0F766E?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.2.0-7C3AED?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-2563EB?style=for-the-badge)

**A portable work-session preflight system for Codex and other local agents.**

Turn scattered files, vague tasks, current-window notes, repo TODOs, and deadlines into a focused work session with milestones, acceptance criteria, buffers, checkpoints, handoff notes, and local memory.

</div>

## Why This Exists

Most work does not start cleanly. You may know that you need to read papers, revise a Word document, finish a report, debug code, prepare slides, or clean up a repository, but not know what to do first, how long it will take, or what to protect if time runs out.

Daily Work Planner is built for that exact moment before execution begins.

It is not a calendar app and it is not a generic daily todo list. It answers three practical questions:

| Question | Planner answer |
|---|---|
| What should I do first? | A first action based on the goal, files, current tasks, and available time. |
| What counts as done? | Milestones with acceptance criteria, not vague steps like "continue working". |
| What if time is not enough? | A minimum deliverable, fallback scope, buffer, and checkpoint response. |

## Core Rule

Planning should accelerate execution. Daily Work Planner limits the planning step to at most 5% of the available work time, with a hard cap:

| Total work time | Planning cap |
|---|---:|
| <= 60 min | 3 min |
| 61-240 min | 8 min |
| 241-480 min | 15 min |
| > 480 min or multi-day | 20 min |

If the budget is small, the skill creates a minimal plan instead of asking many questions.

## Quick Start Case

Suppose you are about to prepare a 5-minute paper-sharing talk and only know the current tasks:

```text
Read two paper abstracts
Draft a 6-slide outline
Create a 5-minute talk checklist
```

Run the planner without giving a duration:

```powershell
python -m daily_work_planner start --goal "Prepare a 5-minute paper-sharing talk from two papers" --start 09:00 --window-note "Read two paper abstracts`nDraft a 6-slide outline`nCreate a 5-minute talk checklist" --speed normal --output-dir .\work-session
```

Daily Work Planner estimates the session and turns that into a concrete plan:

| Decision | Result |
|---|---|
| Detected tasks | 3 current-window tasks |
| Estimated duration | 190 min |
| Feasibility | 77/100, high, complete scope |
| Soft / hard deadline | 11:42 / 12:10 |
| Buffer | 28 min |
| First action | Scan source material |

During the session:

```powershell
python -m daily_work_planner checkpoint --session .\work-session\session.json --now 10:15 --done "Read two paper abstracts" --remaining "Draft a 6-slide outline" --remaining "Create a 5-minute talk checklist"
```

The checkpoint reports whether the delay is light, medium, or severe, then recommends whether to compress buffer, drop optional scope, or switch to the minimum deliverable. Later, `resume` tells the user where to continue, and `handoff --remember` records planned-vs-actual timing for future estimates.

See the full walkthrough: [examples/quick-start-case.md](examples/quick-start-case.md).

## How It Works

```mermaid
flowchart LR
    A["Goal, files, repo tasks, window notes"] --> B["Task inspection"]
    B --> C["Duration estimate"]
    C --> D["Feasibility score"]
    D --> E["Session plan"]
    E --> F["Checkpoint"]
    F --> G["Resume or reschedule"]
    G --> H["Handoff"]
    H --> I["Local memory"]
```

## Feature Map

| Phase | What it can do |
|---|---|
| Intake | Accept goals, files, deadlines, current-window notes, local repo state, review logs, and local memory. |
| Inspection | Extract lightweight context from PDF, DOCX, Markdown, text, and code files. |
| Task triage | Detect open work from `git status`, TODO/FIXME markers, Markdown checkboxes, and pasted task notes. |
| Estimation | Estimate missing duration from task type, files, speed profile, detected work, review history, and memory. |
| Planning | Create soft/hard deadlines, milestone tables, acceptance criteria, buffer, and minimum deliverable scope. |
| Validation | Check that the plan has deadlines, milestones, acceptance criteria, buffer, fallback, and budget compliance. |
| Execution | Record checkpoints, classify delay severity, reschedule remaining work, and generate resume cards. |
| Finish | Create handoff summaries, planned-vs-actual review logs, and private local task memory. |

## Work Modes

| Mode | Typical output |
|---|---|
| Deep writing | Section structure, argument milestones, citation gaps, revision acceptance criteria. |
| Fast reading | Must-read sections, skim/skip boundaries, structured notes, next-use summary. |
| Code development | Minimum runnable version, changed files, tests, debugging order, risk checkpoints. |
| Document revision | Main document, format rules, references, figures, export checklist. |
| PPT production | Slide count, story flow, figure priority, speaker-note checkpoint, minimum deck. |
| Exam review | Topic priority, weak points, recall checks, problem practice, last-hour fallback. |
| Data organization | Source files, table structure, naming, chart outputs, anomaly checks. |
| Research planning | Source triage, reading path, synthesis output, evidence map. |
| Admin paperwork | Required fields, attachments, submission checklist, deadline buffer. |
| Repository cleanup | Dirty files, TODOs, tests, commit-ready scope, handoff state. |

## Use Cases

| Scenario | Why it helps |
|---|---|
| Reading PDFs, papers, textbooks, or technical documents | Prioritizes what to read first and turns reading into structured notes. |
| Revising Word documents, reports, manuscripts, or applications | Separates content work, formatting work, final checks, and submission buffer. |
| Preparing presentations, defenses, or project summaries | Converts loose material into slide milestones and a minimum usable deck. |
| Developing, debugging, or refactoring code | Defines a minimum runnable version, test checkpoints, and commit-ready scope. |
| Reviewing for exams | Prioritizes high-frequency topics, weak points, recall checks, and last-hour fallback. |
| Organizing data, spreadsheets, images, references, or folders | Creates a traceable cleanup plan with naming, table, and output checks. |
| Cleaning up a local repository | Inspects dirty files, TODO/FIXME markers, Markdown checkboxes, and unfinished work. |

## Output Package

By default, one `start` command writes a compact package:

| File | Purpose |
|---|---|
| `work_session.txt` | Human-readable session plan with tasks, deadlines, milestones, and fallback scope. |
| `work_session.docx` | Word version of the same plan for sharing, printing, or archiving. |
| `session.ics` | Calendar event with reminder alarm. |
| `session.json` | Durable state for checkpoint, resume, reschedule, handoff, and memory. |

The plan itself can include:

| Planning element | Included when useful |
|---|---|
| Planning budget | Keeps planning under the 5% rule. |
| Soft and hard deadlines | Separates internal target time from final delivery time. |
| File priority | Marks primary, reference, optional, and ignore-for-now files. |
| Milestones | Adds acceptance criteria for each stage. |
| Buffer and fallback | Protects the minimum deliverable when time slips. |
| Checkpoint response | Classifies delay severity and compresses the plan if needed. |
| Review and memory | Records planned-vs-actual time without storing sensitive source text. |

Use `--split-files` when you also want separate helper files such as `session_plan.md`, `file_context.md`, `file_priority.md`, `todo.txt`, and `plan_validation.md`.

## Agent Compatibility

This repository now has two agent entrypoints:

| Agent type | Entrypoint | Notes |
|---|---|---|
| Codex / OpenAI-compatible skill loaders | `daily-work-planner/SKILL.md` | Uses the standard Codex skill frontmatter and `agents/openai.yaml`. |
| Generic local agents | `daily-work-planner/AGENTS.md` | Contains the same workflow as portable agent instructions. |
| Agents working from the whole repository | `AGENTS.md` | Points the agent to the installable skill folder and test commands. |
| CLI-only use | `python -m daily_work_planner --help` | Works without a skill loader after Python package setup. |

For agents that do not have a formal skill system, install this repository as a portable folder and point the agent to `daily-work-planner/AGENTS.md`. If the agent supports local tools, allow it to run Python scripts from `daily-work-planner/scripts/`.

## Repository Structure

```text
daily-work-planner/
  AGENTS.md
  README.md
  README.zh-CN.md
  install.ps1
  install.sh
  LICENSE
  .gitignore
  pyproject.toml
  .github/
    workflows/
      tests.yml
  examples/
  daily-work-planner/
    AGENTS.md
    SKILL.md
    agents/
      openai.yaml
    scripts/
      plan_day.py
      inspect_tasks.py
      feasibility_score.py
      extract_file_context.py
      classify_work_mode.py
      rank_files.py
      validate_plan.py
      start_session.py
      report_writer.py
      make_todo.py
      make_ics.py
      update_review_log.py
      reschedule_session.py
      checkpoint_session.py
      resume_session.py
      handoff_session.py
      estimate_profile.py
      session_state.py
      task_memory.py
    schemas/
      session.schema.json
    references/
      planning_rules.md
      work_modes.md
      reschedule_rules.md
      privacy_rules.md
      memory_rules.md
    assets/
      daily_plan_template.md
      review_log_template.md
  daily_work_planner/
    __main__.py
  tests/
```

The inner `daily-work-planner/` folder is the installable skill folder. Codex reads `SKILL.md`; generic agents can read `AGENTS.md`. The outer repository contains documentation, examples, installers, tests, and the CLI wrapper.

## Installation

### Option 1: Ask Codex To Install From GitHub

In Codex, ask:

```text
Install this skill: https://github.com/Stephen-studying/daily-work-planner/tree/main/daily-work-planner
```

Restart Codex after installation.

### Option 2: Clone And Install For Codex

Windows PowerShell:

```powershell
git clone https://github.com/Stephen-studying/daily-work-planner.git
cd daily-work-planner
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Agent codex -Force
```

macOS / Linux:

```bash
git clone https://github.com/Stephen-studying/daily-work-planner.git
cd daily-work-planner
sh ./install.sh --agent codex --force
```

The installer copies the inner skill folder to:

- Windows default: `%USERPROFILE%\.codex\skills\daily-work-planner`
- macOS/Linux default: `~/.codex/skills/daily-work-planner`
- If `CODEX_HOME` is set: `$CODEX_HOME/skills/daily-work-planner`

### Option 3: Install For Another Agent

Use `generic` mode when your agent has its own skill folder or instruction-library folder.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Agent generic -Destination "$env:USERPROFILE\.agent-skills" -Force
```

macOS / Linux:

```bash
sh ./install.sh --agent generic --dest "$HOME/.agent-skills" --force
```

Then configure your agent to read one of these files:

| File | Use it when |
|---|---|
| `.agent-skills/daily-work-planner/AGENTS.md` | The agent supports generic instruction files. |
| `.agent-skills/daily-work-planner/SKILL.md` | The agent understands OpenAI/Codex-style skills. |

You can also set `AGENT_SKILLS_HOME` and omit `-Destination` / `--dest`.

### Verify Installation

Windows PowerShell:

```powershell
Test-Path "$env:USERPROFILE\.codex\skills\daily-work-planner\SKILL.md"
```

Then restart Codex and try:

```text
Use $daily-work-planner to plan my next 2-hour work session.
```

### Optional CLI Setup

From the cloned repository, you can also install the helper CLI in editable mode:

```powershell
python -m pip install -e .
python -m daily_work_planner --help
```

## Example Prompt

```text
Use $daily-work-planner to plan my 14:00-18:00 work session.
Goal: read two PDFs and create a 1500-word Chinese presentation outline.
Hard deadline: 18:00.
Soft deadline: 17:00.
Files: paper1.pdf, paper2.pdf, notes.docx.
```

## Script Usage

Use the unified CLI:

```powershell
python -m daily_work_planner --help
python -m daily_work_planner start --goal "Read two papers and draft an outline" --start 14:00 --minutes 240 --hard-deadline 18:00 .\paper1.pdf .\notes.docx --output-dir .\work-session
python -m daily_work_planner session status --session .\work-session\session.json
```

Inspect open tasks and estimate required time:

```powershell
python -m daily_work_planner inspect --repo . --goal "Finish the current repo cleanup" --speed normal
python -m daily_work_planner inspect --window-note "Fix login bug`nUpdate README`nRun tests" --goal "Finish current coding task"
```

Start a session without providing `--minutes`; the planner estimates the duration:

```powershell
python -m daily_work_planner start --goal "Finish current coding task" --start 09:00 --scan-repo --repo . --speed normal --output-dir .\work-session
```

Score feasibility before committing to a time box:

```powershell
python -m daily_work_planner feasibility --goal "Finish the final report" --available-minutes 90 --estimated-minutes 150 --mode writing
```

The default `start` package writes:

- `work_session.txt`
- `work_session.docx`
- `session.ics`
- `session.json`

Use `--split-files` when you also want separate helper files such as `session_plan.md`, `file_context.md`, `file_priority.md`, `todo.txt`, and `plan_validation.md`.

Use review history to adapt buffer:

```powershell
python -m daily_work_planner start --goal "Build final deck" --start 09:00 --minutes 180 --hard-deadline 12:00 --profile-log .\review-log.md --output-dir .\work-session
```

Record a checkpoint during execution:

```powershell
python -m daily_work_planner checkpoint --session .\work-session\session.json --now 10:30 --done "Updated README" --remaining "Run tests" --remaining "Commit changes"
```

Resume a previous unfinished session:

```powershell
python -m daily_work_planner resume --session .\work-session\session.json
```

Create an end-of-session handoff:

```powershell
python -m daily_work_planner handoff --session .\work-session\session.json --completed "Updated task inspection" --remaining "Publish v1.2 tag" --actual-minutes 145 --remember
```

Record local task memory after finishing:

```powershell
python -m daily_work_planner remember --session .\work-session\session.json --actual-minutes 145 --completed "Generated consolidated session report" --habit "Coding cleanup usually needs an extra test pass"
```

By default this writes `.daily-work-planner/memory.jsonl` and `.daily-work-planner/MEMORY.md`. The folder is ignored by Git because it may contain personal work habits.

Extract lightweight context from local files:

```powershell
python .\daily-work-planner\scripts\extract_file_context.py .\paper1.pdf .\notes.docx .\src --recursive --max-files 20 --max-chars 1200 --format markdown
```

Classify work mode:

```powershell
python .\daily-work-planner\scripts\classify_work_mode.py --goal "Fix the login bug and run tests" .\src\auth.py .\tests\test_auth.py
```

Rank files:

```powershell
python .\daily-work-planner\scripts\rank_files.py --goal "Revise final report before submission" .\report.docx .\rubric.pdf .\notes.md
```

Generate a Markdown plan:

```powershell
python .\daily-work-planner\scripts\plan_day.py --start 14:00 --minutes 240 --goal "Read two papers and draft an outline" --mode reading --hard-deadline 18:00
```

Validate a plan:

```powershell
python .\daily-work-planner\scripts\validate_plan.py --plan .\work-session\session_plan.md --available-minutes 240
```

Create todo entries from a plan:

```powershell
python .\daily-work-planner\scripts\make_todo.py --plan .\work-session\session_plan.md --output .\work-session\todo.txt
```

Create an `.ics` calendar event:

```powershell
python .\daily-work-planner\scripts\make_ics.py --title "Paper reading session" --start 2026-06-13T14:00 --end 2026-06-13T18:00 --description "Read papers and draft outline" --alarm-minutes 10 --output session.ics
```

Reschedule after checkpoint slippage:

```powershell
python .\daily-work-planner\scripts\reschedule_session.py --goal "Finish the presentation outline" --now 15:40 --hard-deadline 18:00 --minutes-late 25 --mode reading
python .\daily-work-planner\scripts\reschedule_session.py --session .\work-session\session.json --now 15:40 --minutes-late 25 --output .\work-session\rescheduled_plan.md
```

Append a review-log entry:

```powershell
python .\daily-work-planner\scripts\update_review_log.py --log review-log.md --goal "Read papers" --planned-minutes 240 --actual-minutes 260 --delay-reason "PDF reading took longer than expected" --next-adjustment "Add 10 percent buffer for dense PDFs"
```

Build an estimation profile:

```powershell
python .\daily-work-planner\scripts\estimate_profile.py .\review-log.md
```

## Privacy Model

Daily Work Planner is local-first by default:

- It does not upload user files by itself.
- It does not store full documents, papers, code, or current-window raw text in memory.
- Local memory stores task type, mode, planned minutes, actual minutes, summary, filenames, and habit signals.
- `.daily-work-planner/` is ignored by Git because it may contain personal working patterns.

## Roadmap Ideas

- Richer file readers for more office, research, and course-material formats.
- Optional GUI wrapper for non-terminal users.
- Better task-duration calibration from repeated sessions.
- More work-mode templates for lab work, literature review, grant writing, and interview prep.
- Export options for more task managers and calendar systems.

## Non-Goals

This skill does not try to:

- Replace calendar software
- Replace long-term project management tools
- Fully summarize every source file during planning
- Read large files deeply before the user begins work
- Produce a plan so detailed that it delays execution

## License

MIT License.
