"""Unit tests for the MVP-2 application tracker."""

import datetime
import os
import unittest

import storage
import tracker
from models import Application
from models import Opportunity


class TestTracker(unittest.TestCase):
    """Check tracker updates, persistence, and deadline countdowns."""

    def make_opportunity(self, opp_id, deadline):
        """Create a small opportunity fixture for tracker tests."""
        return Opportunity(
            opp_id,
            "Test Opportunity " + opp_id,
            "competition",
            ["AI"],
            ["JC"],
            "free",
            True,
            deadline,
            "https://example.com/" + opp_id,
            "Test Organizer",
        )

    def test_status_transition_updates_application(self):
        """Verify an application can move between valid statuses."""
        applications = [Application("opp-1", "interested", "")]

        updated = tracker.update_application_status(
            applications,
            "opp-1",
            "applied",
        )

        self.assertTrue(updated)
        self.assertEqual(applications[0].status, "applied")

    def test_invalid_status_is_rejected(self):
        """Verify invalid statuses do not change the application."""
        applications = [Application("opp-1", "interested", "")]

        updated = tracker.update_application_status(
            applications,
            "opp-1",
            "maybe",
        )

        self.assertFalse(updated)
        self.assertEqual(applications[0].status, "interested")

    def test_persistence_round_trip(self):
        """Verify applications save to and load from a temporary JSON file."""
        path = os.path.join(os.path.dirname(__file__), "tmp_applications.json")
        applications = [
            Application("opp-1", "applied", "Need transcript."),
            Application("opp-2", "accepted", "Interview went well."),
        ]

        try:
            storage.save_applications(path, applications)
            loaded = storage.load_applications(path)
        finally:
            if os.path.exists(path):
                os.remove(path)

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].opp_id, "opp-1")
        self.assertEqual(loaded[0].status, "applied")
        self.assertEqual(loaded[0].notes, "Need transcript.")
        self.assertEqual(loaded[1].opp_id, "opp-2")
        self.assertEqual(loaded[1].status, "accepted")

    def test_deadline_countdown_warns_and_expires(self):
        """Verify countdown text uses warning and expired badges."""
        soon = self.make_opportunity("soon", "2026-06-18")
        expired = self.make_opportunity("expired", "2026-06-01")
        today = datetime.date(2026, 6, 13)

        self.assertEqual(
            tracker.get_deadline_countdown(soon, today),
            "5 days left [WARNING]",
        )
        self.assertEqual(
            tracker.get_deadline_countdown(expired, today),
            "EXPIRED",
        )


if __name__ == "__main__":
    unittest.main()
