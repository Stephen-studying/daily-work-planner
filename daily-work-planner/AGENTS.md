# Daily Work Planner

Use these instructions when this folder is installed in a non-Codex agent or any agent that reads `AGENTS.md`.

Daily Work Planner is a work-session preflight skill. Use it when the user wants to plan a focused work session, inspect current or local tasks, estimate required time, score feasibility, create milestones, define acceptance criteria, reserve buffer, checkpoint progress, resume unfinished work, create handoff notes, or remember task timing habits.

## Core Rule

Optimize for execution, not planning.

Before planning, calculate:

```text
planning_budget = min(available_work_time * 5%, absolute_cap)
```

Use these caps:

- <= 60 minutes total work: max 3 minutes planning
- 61-240 minutes total work: max 8 minutes planning
- 241-480 minutes total work: max 15 minutes planning
- Multi-day or > 480 minutes: max 20 minutes for the first planning pass

If the budget is small, produce a minimal plan instead of asking many questions.

## Workflow

1. Identify the goal, available time, hard deadline, expected output, current-window task text, local repo, and provided files.
2. If available time is missing, estimate required minutes from the goal, files, detected tasks, work mode, speed profile, review logs, and local memory.
3. Score feasibility before committing to the plan: complete, deliverable, minimum, or redefine scope.
4. Inspect only enough source material to determine scope and priority.
5. Classify files as primary, reference, optional, or ignore-for-now.
6. Set hard deadline, soft deadline, buffer, and checkpoint times.
7. Split work into milestones with acceptance criteria.
8. Define the minimum deliverable version.
9. During execution, record checkpoints and compress or rescope the plan when progress slips.
10. At the end, create a handoff summary and optionally write local memory.

## Local Scripts

If the agent can run local Python, prefer the bundled scripts for deterministic work:

- `scripts/inspect_tasks.py`: inspect current-window notes and local repositories for open tasks.
- `scripts/feasibility_score.py`: score whether the work fits the time box.
- `scripts/start_session.py`: generate `work_session.txt`, `work_session.docx`, `session.ics`, and `session.json`.
- `scripts/checkpoint_session.py`: record done/remaining work and classify delay severity.
- `scripts/resume_session.py`: create a concise resume card.
- `scripts/handoff_session.py`: create a handoff and optionally update local memory.
- `scripts/extract_file_context.py`: extract lightweight context from PDF, DOCX, Markdown, text, and code files.
- `scripts/classify_work_mode.py`: infer the work mode.
- `scripts/rank_files.py`: rank files as primary, reference, optional, or ignore-for-now.
- `scripts/validate_plan.py`: verify deadlines, milestones, acceptance criteria, buffer, fallback, and budget compliance.

## Output Requirements

Every plan must answer:

1. What should the user do first?
2. What counts as done for each milestone?
3. What should be protected if time runs out?

Prefer compact output. A useful plan is better than a perfect plan that delays execution.

## Privacy

Prefer local file inspection. Do not upload sensitive user files unless the user explicitly asks and the environment supports that safely. Do not store full documents, papers, source code, or raw current-window text in memory. Local memory should contain only task type, mode, planned minutes, actual minutes, completion summary, filenames, and habit signals.

