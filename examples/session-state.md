# Example: Session State

Create a complete work-session package:

```powershell
python -m daily_work_planner start --goal "Revise report and prepare final submission" --start 14:00 --minutes 180 --hard-deadline 17:00 .\report.docx .\rubric.pdf --output-dir .\work-session
```

Inspect the durable session state:

```powershell
python -m daily_work_planner session status --session .\work-session\session.json
```

Mark the session as started:

```powershell
python -m daily_work_planner session transition --session .\work-session\session.json --state started --note "Started first milestone."
```

Reschedule after a checkpoint delay:

```powershell
python -m daily_work_planner reschedule --session .\work-session\session.json --now 15:40 --minutes-late 25 --output .\work-session\rescheduled_plan.md
```
