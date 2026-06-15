# Planning Rules

## Planning Budget

Always calculate a planning budget before doing detailed work.

```text
planning_budget = min(total_work_minutes * 0.05, absolute_cap)
```

Absolute caps:

| Total work time | Planning cap |
|---|---:|
| <= 60 min | 3 min |
| 61-240 min | 8 min |
| 241-480 min | 15 min |
| > 480 min or multi-day | 20 min |

If the user gives no total work time, ask once. If they do not answer, assume 120 minutes and say so.

## Output Depth

| Total work time | Planning mode | Expected output |
|---|---|---|
| <= 60 min | quick | 3-8 lines |
| 61-240 min | standard | one compact table plus fallback |
| 241-480 min | full | file priority, milestones, buffers, fallback |
| > 480 min | staged | high-level stages, not minute-by-minute detail |

## Deadline Rules

Hard deadline:

- The actual latest finish or submission time.
- If absent, use the end of the available work window.

Soft deadline:

- The time by which a usable version should exist.
- Default to hard deadline minus buffer time.
- For risky tasks, move the soft deadline earlier.

## Buffer Rules

Default buffer:

| Task length | Buffer |
|---|---:|
| <= 60 min | 10% |
| 61-240 min | 15% |
| 241-480 min | 20% |
| > 480 min | 25% |

Add 5 percentage points when the task includes unfamiliar files, code debugging, formatting-heavy Word/PPT work, data cleanup, or unclear requirements.

## Milestone Rules

Each milestone must include:

- Time range
- Action
- Deliverable
- Acceptance criteria

Avoid vague actions such as "continue working" or "improve document." Replace them with checkable outputs.

## Default Assumptions

If input is incomplete:

- Missing work mode: use Mixed Work Mode.
- Missing soft deadline: set it before the buffer.
- Too many files: scan filenames, headings, abstracts, tables of contents, and modified times.
- Vague goal: define a minimum deliverable first.
- Unclear effort: use conservative estimates and include a fallback.
