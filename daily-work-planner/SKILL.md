---
name: daily-work-planner
description: Plan a focused work session before execution begins. Use when the user provides a goal, files, available time, deadlines, or asks for a realistic daily or session plan with soft and hard deadlines, milestones, acceptance criteria, buffers, fallback scope, rescheduling checkpoints, Markdown/todo/ICS outputs, or review logs for work involving PDFs, Word documents, spreadsheets, notes, code, papers, exams, writing, presentations, or project work.
---

# Daily Work Planner

## Core Rule

Optimize for execution, not planning. Convert uncertainty into a usable first plan quickly, then use checkpoints to correct the plan during work.

Before planning, calculate the planning budget:

```text
planning_budget = min(available_work_time * 5%, absolute_cap)
```

Use these caps:

- <= 60 minutes total work: max 3 minutes planning
- 61-240 minutes total work: max 8 minutes planning
- 241-480 minutes total work: max 15 minutes planning
- Multi-day or > 480 minutes: max 20 minutes for the first planning pass

If the planning budget is small, produce a minimal plan instead of asking many questions.

## Workflow

1. Identify the task goal, available time, hard deadline, expected output, and provided files.
2. Calculate planning budget and choose output depth: quick, standard, or full.
3. Inspect only enough source material to determine scope and priority. Use `scripts/extract_file_context.py` for local PDFs, DOCX files, Markdown, text, and code when deterministic file context is useful.
4. Choose or classify the work mode. Use `scripts/classify_work_mode.py` when the mode is unclear.
5. Classify files as primary, reference, optional, or ignore-for-now. Use `scripts/rank_files.py` when multiple files are provided.
6. Set hard deadline, soft deadline, buffers, and checkpoint times.
7. Split the work into milestones with acceptance criteria.
8. Define the minimum deliverable version.
9. Add a delay-response plan for checkpoint slippage.
10. Validate the plan with `scripts/validate_plan.py` when a durable plan is being saved or shared.
11. For complete work-session packages, persist `session.json` and update it through `scripts/session_state.py`.
12. Output the plan in a compact form the user can execute immediately.

## Source Handling

Respect the planning budget when reading files.

- For large PDFs or documents, inspect titles, headings, tables of contents, abstracts, filenames, metadata, and representative pages first.
- Avoid deep summarization unless the user's task is explicitly reading or analysis.
- Prefer local file inspection. Do not upload sensitive files.
- If files are too many, prioritize by filename, modified time, user-stated relevance, and relationship to the final deliverable.

## Output Depth

Use Quick Plan for short or unclear tasks:

- Goal
- Planning budget
- First action
- 2-4 steps
- Soft and hard deadline
- Minimum deliverable

Use Standard Plan for most same-day work:

- Task summary
- Planning budget
- File priority
- Soft and hard deadline
- Milestone table
- Buffer
- Minimum deliverable
- Delay response

Use Full Plan only for complex full-day or multi-day work:

- Scope decision
- File priority table
- Milestones and acceptance criteria
- Checkpoints
- Buffer and fallback paths
- Todo list
- Review log template
- Optional ICS event instructions
- Consolidated TXT/DOCX report for human reading

## References

Load these only when needed:

- `references/planning_rules.md`: budget, soft deadline, buffer, and output-depth rules.
- `references/work_modes.md`: work-mode-specific planning rules.
- `references/reschedule_rules.md`: checkpoint delay handling and minimum deliverable rules.
- `references/privacy_rules.md`: local-first and sensitive-content handling.

## Scripts

Use scripts when deterministic output is helpful:

- `scripts/plan_day.py`: create a Markdown work-session plan from start time, total minutes, mode, goal, and optional deadline.
- `scripts/extract_file_context.py`: extract lightweight local context from PDF, DOCX, Markdown, text, and code files for priority decisions.
- `scripts/classify_work_mode.py`: infer the most likely work mode from the goal and file names.
- `scripts/rank_files.py`: rank files as primary, reference, optional, or ignore-for-now.
- `scripts/validate_plan.py`: check that a plan includes deadlines, milestones, acceptance criteria, buffer, fallback, and budget compliance.
- `scripts/start_session.py`: generate a full work-session package with consolidated `work_session.txt`, `work_session.docx`, `session.ics`, and `session.json`; use `--split-files` to also write separate helper files.
- `scripts/make_todo.py`: convert a milestone table into a todo.txt style checklist.
- `scripts/make_ics.py`: create a simple calendar `.ics` file from a planned session or milestone, optionally with a display reminder.
- `scripts/report_writer.py`: write consolidated planning reports as TXT and DOCX without third-party dependencies.
- `scripts/update_review_log.py`: append planned-vs-actual records to a Markdown review log.
- `scripts/reschedule_session.py`: rebuild the remaining work plan after checkpoint slippage.
- `scripts/estimate_profile.py`: summarize review logs to calibrate future time estimates.
- `scripts/session_state.py`: create, inspect, transition, and review durable `session.json` state.

## Output Requirements

Every plan must answer:

1. What should the user do first?
2. What counts as done for each milestone?
3. What should be protected if time runs out?

Keep the final plan compact. Never let planning consume more value than it saves.
