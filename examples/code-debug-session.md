# Example: Code Debug Session

User prompt:

```text
Use $daily-work-planner to plan a 90-minute debugging session.
Goal: fix the login form validation bug and verify the fix.
Files: src/auth, tests/auth, package.json.
```

Expected plan shape:

- Planning budget no more than 5 minutes
- File priority: failing area, tests, package scripts
- Milestones for reproduction, source inspection, fix, focused verification
- Minimum deliverable: bug reproduced, fix applied, verification command run or documented
- Delay response: preserve main-path fix and defer edge-case cleanup
