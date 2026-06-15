# Memory Rules

Use memory to improve future estimates and preserve task-level lessons, not to archive source content.

## Storage

- Store local task memory in `.daily-work-planner/` by default.
- Keep `.daily-work-planner/` out of Git unless the user explicitly wants to share anonymized examples.
- Write `memory.jsonl` for structured history and `MEMORY.md` for a compact human-readable summary.

## What To Record

- Goal, work mode, planned minutes, actual minutes, and completion summary.
- File names or file roles, not full file contents.
- User habit notes such as "PPT polishing usually runs long" or "code debugging needs extra verification time."
- Estimate signals: faster than plan, close to plan, or slower than plan.

## What Not To Record

- Full manuscript paragraphs, private code, datasets, personal IDs, credentials, or confidential documents.
- Raw current-window text if it contains sensitive source content.
- Temporary speculation that is not useful for future planning.

## Estimate Learning

- If actual time is at least 25% over plan, treat that mode as slower-than-plan and increase future estimates or buffer.
- If actual time is at least 20% under plan, treat that mode as faster-than-plan and allow shorter future blocks.
- If repeated habit notes point to the same issue, summarize the stable lesson in `MEMORY.md` instead of accumulating long logs.

## End-of-Session Workflow

1. Mark the session finished or reviewed in `session.json`.
2. Record a concise completion summary with `scripts/task_memory.py`.
3. Keep memory local and private by default.
4. Use the memory profile during later `inspect` or `start` runs.
