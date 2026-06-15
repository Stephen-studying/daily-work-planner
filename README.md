# Daily Work Planner

[简体中文](README.zh-CN.md) | English

Daily Work Planner is a Codex Skill for work-session preflight planning. It turns a messy goal, available time, source files, and deadlines into an executable work-session plan before the user starts working.

It is not a calendar replacement and it is not a generic daily todo generator. Its purpose is to help a user answer three questions quickly:

1. What should I do first?
2. What counts as done at each milestone?
3. What should I protect if time runs out?

## Core Idea

Planning should accelerate execution. Daily Work Planner limits the planning step to at most 5% of the available work time, with an absolute cap:

| Total work time | Planning cap |
|---|---:|
| <= 60 min | 3 min |
| 61-240 min | 8 min |
| 241-480 min | 15 min |
| > 480 min or multi-day | 20 min |

If the budget is small, the skill creates a minimal plan instead of asking many questions.

## Use Cases

- Reading PDFs, papers, textbooks, or technical documents
- Revising Word documents, reports, manuscripts, or application materials
- Preparing papers, presentations, defenses, or project summaries
- Developing, debugging, or refactoring code
- Reviewing for exams
- Producing slides and speaker notes
- Organizing data, spreadsheets, images, references, or folders
- Deciding which files matter when there are too many inputs
- Defining a minimum deliverable when time is limited

## What It Produces

Depending on task length and uncertainty, the skill can produce:

- Planning budget
- Soft deadline and hard deadline
- File priority
- Milestone table
- Acceptance criteria
- Buffer time
- Checkpoint delay response
- Minimum deliverable version
- Todo list
- Optional `.ics` calendar event with reminder alarm
- Review log entry
- Lightweight context extracted from local PDF, DOCX, Markdown, text, and code files
- Automatic work-mode classification
- File priority ranking
- Plan validation
- One-command work-session package generation
- Checkpoint rescheduling
- Personal estimation profile from review logs
- Durable `session.json` state machine
- Adaptive buffer from review-log history
- Consolidated `work_session.txt` and `work_session.docx` reports

## Repository Structure

```text
daily-work-planner/
  README.md
  README.zh-CN.md
  LICENSE
  .gitignore
  pyproject.toml
  .github/
    workflows/
      tests.yml
  examples/
  daily-work-planner/
    SKILL.md
    agents/
      openai.yaml
    scripts/
      plan_day.py
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
      estimate_profile.py
      session_state.py
    schemas/
      session.schema.json
    references/
      planning_rules.md
      work_modes.md
      reschedule_rules.md
      privacy_rules.md
    assets/
      daily_plan_template.md
      review_log_template.md
  daily_work_planner/
    __main__.py
  tests/
```

The inner `daily-work-planner/` folder is the actual Codex Skill folder. The outer repository contains documentation and examples for GitHub.

## Installation

Copy or clone the inner skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\daily-work-planner "$env:USERPROFILE\.codex\skills\"
```

Restart Codex so the skill can be discovered.

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

## Non-Goals

This skill does not try to:

- Replace calendar software
- Replace long-term project management tools
- Fully summarize every source file during planning
- Read large files deeply before the user begins work
- Produce a plan so detailed that it delays execution

## License

MIT License.
