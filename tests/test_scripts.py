from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "daily-work-planner" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from classify_work_mode import classify_work_mode
from estimate_profile import build_profile
from extract_file_context import extract_context
from make_ics import build_ics
from make_todo import parse_milestones, render_todo
from plan_day import PlanConfig, generate_plan, parse_time
from rank_files import rank_files
from report_writer import write_docx
from session_state import create_session, transition
from start_session import adaptive_buffer_from_logs
from validate_plan import validate_plan


class DailyWorkPlannerScriptTests(unittest.TestCase):
    def test_classify_code_mode(self) -> None:
        result = classify_work_mode("Fix the login bug and run tests", ["src/auth.py"])
        self.assertEqual(result.mode, "code")
        self.assertGreater(result.confidence, 0.5)

    def test_classify_additional_modes(self) -> None:
        self.assertEqual(classify_work_mode("Prepare meeting agenda and follow-up list", []).mode, "meeting")
        self.assertEqual(classify_work_mode("Screen citations for literature review", ["refs.bib"]).mode, "literature")
        self.assertEqual(classify_work_mode("Translate and polish this Chinese abstract", []).mode, "translation")

    def test_plan_validates_core_requirements(self) -> None:
        plan = generate_plan(
            PlanConfig(
                start=parse_time("14:00"),
                minutes=240,
                goal="Read two papers and draft an outline",
                mode="reading",
            )
        )
        checks = validate_plan(plan, available_minutes=240)
        self.assertTrue(all(check.passed for check in checks), checks)

    def test_ics_alarm_block(self) -> None:
        ics = build_ics(
            "Test",
            datetime(2026, 6, 15, 9, 0),
            datetime(2026, 6, 15, 10, 0),
            "Description",
            alarm_minutes=10,
        )
        self.assertIn("BEGIN:VALARM", ics)
        self.assertIn("TRIGGER:-PT10M", ics)

    def test_todo_from_plan_table(self) -> None:
        plan = "\n".join(
            [
                "| Time | Task | Deliverable | Acceptance criteria |",
                "|---|---|---|---|",
                "| 09:00-09:30 | Scan files | priority map | main files known |",
            ]
        )
        todo = render_todo(parse_milestones(plan))
        self.assertIn("[ ] 09:00-09:30 Scan files -> priority map", todo)

    def test_extract_text_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "notes.md"
            path.write_text("# Heading\n\nImportant planning notes.", encoding="utf-8")
            context = extract_context(path, max_chars=200)
            self.assertEqual(context.title, "notes")
            self.assertIn("# Heading", context.headings)
            self.assertIn("Important planning notes", context.sample)

    def test_rank_files_prioritizes_goal_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "final-report.docx"
            notes = Path(tmp) / "random.txt"
            report.write_text("report placeholder", encoding="utf-8")
            notes.write_text("unrelated", encoding="utf-8")
            ranked = rank_files("Revise final report", [str(report), str(notes)], mode="revision")
            self.assertEqual(Path(ranked[0].path).name, "final-report.docx")
            self.assertIn(ranked[0].priority, {"A", "B"})

    def test_estimate_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "review.md"
            log.write_text(
                "\n".join(
                    [
                        "# Work Session Review Log",
                        "",
                        "## 2026-06-15",
                        "",
                        "- Goal: Read papers",
                        "- Work mode: reading",
                        "- Planned minutes: 100",
                        "- Actual minutes: 130",
                    ]
                ),
                encoding="utf-8",
            )
            stats = build_profile([str(log)])
            self.assertEqual(stats[0].mode, "reading")
            self.assertEqual(stats[0].average_delta_minutes, 30)

    def test_adaptive_buffer_from_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "review.md"
            log.write_text(
                "\n".join(
                    [
                        "# Work Session Review Log",
                        "",
                        "## 2026-06-15",
                        "",
                        "- Goal: Build slides",
                        "- Work mode: ppt",
                        "- Planned minutes: 100",
                        "- Actual minutes: 140",
                    ]
                ),
                encoding="utf-8",
            )
            result = adaptive_buffer_from_logs("ppt", [str(log)])
            self.assertEqual(result["extra_percent"], 10)
            self.assertIn("over plan", result["reason"])

    def test_session_state_transition(self) -> None:
        session = create_session(
            goal="Draft outline",
            mode="writing",
            start="09:00",
            hard_deadline="11:00",
            planned_minutes=120,
            files=["draft.docx"],
        )
        updated = transition(session, "started", "Started work.")
        self.assertEqual(updated["state"], "started")
        self.assertEqual(updated["events"][-1]["note"], "Started work.")

    def test_write_docx_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.docx"
            write_docx(path, "# Title\n\nBody text", "Test Report")
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 500)


if __name__ == "__main__":
    unittest.main()
