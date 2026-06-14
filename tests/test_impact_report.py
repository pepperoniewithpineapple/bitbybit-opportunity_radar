"""Tests for the Python-only judge impact report."""

import os
import tempfile
import unittest

import demand
import impact_report
from models import Opportunity, Student


def make_opp(title):
    """Build a simple opportunity fixture."""
    return Opportunity(
        "opp-001",
        title,
        "workshop",
        ["coding"],
        ["JC"],
        "free",
        True,
        "2099-12-31",
        "https://example.com",
        "Demo Org",
    )


class TestImpactReport(unittest.TestCase):
    """Check plain-text impact report generation and file output."""

    def test_report_is_plain_text_and_mentions_python_only(self):
        opportunity = make_opp("Coding Sprint")
        student = Student("Wei Ming", "JC", ["coding"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            searches_path = os.path.join(tmp_dir, "searches.json")
            text = impact_report.build_report_text(
                [opportunity],
                searches_path,
                student,
            )

        self.assertIn("JUDGE IMPACT REPORT", text)
        self.assertIn("Python-only evidence", text)
        self.assertNotIn("<html", text.lower())

    def test_report_includes_demand_signal_count(self):
        opportunity = make_opp("Coding Sprint")
        student = Student("Wei Ming", "JC", ["coding"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            searches_path = os.path.join(tmp_dir, "searches.json")
            demand.log_search(searches_path, "JC", ["coding"])
            text = impact_report.build_report_text(
                [opportunity],
                searches_path,
                student,
            )

        self.assertIn("Anonymous demand signals: 1", text)

    def test_save_report_writes_file(self):
        opportunity = make_opp("Coding Sprint")

        with tempfile.TemporaryDirectory() as tmp_dir:
            searches_path = os.path.join(tmp_dir, "searches.json")
            path = os.path.join(tmp_dir, "report.txt")
            written = impact_report.save_report(path, [opportunity], searches_path)

            with open(written, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()

        self.assertIn("OPPORTUNITY RADAR - JUDGE IMPACT REPORT", content)
        self.assertIn("Standard library only", content)


if __name__ == "__main__":
    unittest.main()
