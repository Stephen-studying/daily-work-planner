# Privacy Rules

Use local-first handling by default.

## Defaults

- Do not upload user files to external services.
- Do not copy full sensitive source text into logs.
- Do not store private documents in review logs.
- Record task state, timing, and process lessons instead of source content.
- Prefer summaries of file roles over full file contents.
- Keep `.daily-work-planner/` local by default because it can contain personal timing habits and task history.

## Sensitive Inputs

Treat these as sensitive unless the user says otherwise:

- Unpublished papers
- Personal statements
- Resumes
- Grades
- Contracts
- IDs
- Medical or financial records
- Private code
- Research data
- Internal reports

## Review Logs

Review logs may contain:

- Date
- Goal
- Planned minutes
- Actual minutes
- Delay reason
- Future estimate adjustment

Review logs should not contain:

- Full manuscript paragraphs
- Private IDs
- Full source code
- Confidential datasets
- Unredacted personal information

## Local Memory

Local memory may contain:

- Goal summaries
- Planned and actual minutes
- Completion summaries
- File names or file roles
- Habit notes that improve future estimates

Local memory should not contain full current-window text, private document content, source code blocks, credentials, or confidential data.
