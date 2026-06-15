# Quick Start Case: Plan A Paper-Sharing Talk

This example shows the full Daily Work Planner loop:

```text
current tasks -> estimated time -> feasibility score -> session plan
-> checkpoint -> resume card -> handoff -> local memory
```

## Situation

The user is about to prepare a short paper-sharing talk, but they have not decided how long it will take.

Current task notes:

```text
Read two paper abstracts
Draft a 6-slide outline
Create a 5-minute talk checklist
```

## 1. Start Without Supplying Duration

```powershell
python -m daily_work_planner start `
  --goal "Prepare a 5-minute paper-sharing talk from two papers" `
  --start 09:00 `
  --window-note "Read two paper abstracts`nDraft a 6-slide outline`nCreate a 5-minute talk checklist" `
  --speed normal `
  --output-dir .\work-session
```

Daily Work Planner estimates the session length and creates:

```text
work-session/
  work_session.txt
  work_session.docx
  session.ics
  session.json
```

## 2. What The Planner Decides

```text
Goal: Prepare a 5-minute paper-sharing talk from two papers
Mode: reading
Planned minutes: 190 (estimated)
Estimation source: task inspection
Hard deadline: 12:10
```

Detected tasks:

| Priority | Task | Mode | Estimate |
|---|---|---|---:|
| A | Read two paper abstracts | reading | 45 |
| A | Draft a 6-slide outline | writing | 70 |
| A | Create a 5-minute talk checklist | ppt | 65 |

Feasibility:

```text
Score: 77/100
Level: high
Recommended scope: complete
```

Plan:

| Time | Task | Deliverable | Acceptance criteria |
|---|---|---|---|
| 09:08-09:59 | Scan source material | priority map | must-read and skip sections are identified |
| 09:59-10:50 | Read priority sections | structured notes | core claims and evidence are captured |
| 10:50-11:42 | Extract next-use output | actionable summary | notes can directly support the next task |

The plan keeps a buffer from `11:42` to `12:10`.

## 3. Check Progress Mid-Session

```powershell
python -m daily_work_planner checkpoint `
  --session .\work-session\session.json `
  --now 10:15 `
  --done "Read two paper abstracts" `
  --remaining "Draft a 6-slide outline" `
  --remaining "Create a 5-minute talk checklist"
```

Output:

```text
Delay level: light
Minutes late: 12
Action: Compress buffer and keep the core target.
```

## 4. Resume Later

```powershell
python -m daily_work_planner resume --session .\work-session\session.json
```

Output:

```text
Estimated remaining: 127 min
Next Action: Continue with: Draft a 6-slide outline
```

## 5. End With A Handoff And Memory

```powershell
python -m daily_work_planner handoff `
  --session .\work-session\session.json `
  --completed "Read two paper abstracts" `
  --completed "Drafted a 6-slide outline" `
  --remaining "Polish speaker notes before presenting" `
  --actual-minutes 185 `
  --remember
```

Handoff summary:

```text
Completed:
- Read two paper abstracts
- Drafted a 6-slide outline

Remaining:
- Polish speaker notes before presenting

Next Session Start:
Start with: Polish speaker notes before presenting
```

Local memory records:

```text
Mode: reading
Planned: 190
Actual: 185
Signal: close to plan
```

The next estimate for similar reading/presentation work can use this local memory.
