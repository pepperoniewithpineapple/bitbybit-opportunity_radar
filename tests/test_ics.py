"""Unit tests for the MVP-2 ICS calendar export."""

import unittest

import ics_export
from models import Application
from models import Opportunity


class TestIcsExport(unittest.TestCase):
    """Check generated ICS calendar structure and event content."""

    def make_opportunity(self, opp_id, title, deadline):
        """Create a small opportunity fixture for ICS tests."""
        return Opportunity(
            opp_id,
            title,
            "competition",
            ["AI"],
            ["JC"],
            "free",
            True,
            deadline,
            "https://example.com/" + opp_id,
            "Test Organizer",
        )

    def test_calendar_has_wrapper_and_events(self):
        """Verify the calendar wrapper and one event per tracked item."""
        opportunities = [
            self.make_opportunity("opp-1", "First Deadline", "2026-06-20"),
            self.make_opportunity("opp-2", "Second Deadline", "2026-06-21"),
        ]
        applications = [
            Application("opp-1", "interested", ""),
            Application("opp-2", "applied", ""),
        ]

        ics_text = ics_export.generate_ics_text(applications, opportunities)

        self.assertIn("BEGIN:VCALENDAR", ics_text)
        self.assertIn("END:VCALENDAR", ics_text)
        self.assertEqual(ics_text.count("BEGIN:VEVENT"), 2)

    def test_calendar_contains_correct_summary(self):
        """Verify each event summary names the opportunity deadline."""
        opportunities = [
            self.make_opportunity("opp-1", "AI Challenge", "2026-06-20"),
        ]
        applications = [Application("opp-1", "interested", "")]

        ics_text = ics_export.generate_ics_text(applications, opportunities)

        self.assertIn("SUMMARY:Deadline: AI Challenge", ics_text)


if __name__ == "__main__":
    unittest.main()
