"""Tests for Opportunity Sender mode helpers."""

import os
import tempfile
import unittest

import demand
import sender
from models import Opportunity


def make_opportunity(opp_id, title="Coding Camp", interests=None):
    """Build a minimal open Opportunity fixture."""
    if interests is None:
        interests = ["coding"]

    return Opportunity(
        opp_id,
        title,
        "workshop",
        interests,
        ["JC"],
        "free",
        True,
        "2099-12-31",
        "https://example.com",
        "Example Org",
    )


class TestSenderHelpers(unittest.TestCase):
    """Check sender-mode pure helpers and file output."""

    def test_title_exists_is_case_insensitive(self):
        """Duplicate title checks should ignore case and whitespace."""
        opportunities = [make_opportunity("opp-001", "AI Challenge")]

        self.assertTrue(sender.title_exists(opportunities, "  ai challenge  "))
        self.assertFalse(sender.title_exists(opportunities, "Robotics Camp"))

    def test_add_opportunity_rejects_duplicate_title(self):
        """Adding should fail when a matching title already exists."""
        opportunities = [make_opportunity("opp-001", "AI Challenge")]
        duplicate = make_opportunity("opp-002", "ai challenge")
        fresh = make_opportunity("opp-003", "Robotics Camp")

        self.assertFalse(sender.add_opportunity(opportunities, duplicate))
        self.assertTrue(sender.add_opportunity(opportunities, fresh))
        self.assertEqual(len(opportunities), 2)

    def test_gap_rows_use_anonymous_demand_against_supply(self):
        """Sender gap rows should rank demand with thin supply first."""
        opportunities = [make_opportunity("opp-001", interests=["coding"])]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "searches.json")
            demand.log_search(path, "JC", ["AI"])
            demand.log_search(path, "JC", ["AI"])

            rows = sender.build_gap_rows(opportunities, path)

        self.assertEqual(rows[0]["interest"], "ai")
        self.assertEqual(rows[0]["demand"], 2)
        self.assertEqual(rows[0]["supply"], 0)

    def test_sender_preview_counts_matching_demand(self):
        """Impact preview should count demand matching opportunity interests."""
        opportunity = make_opportunity("opp-001", interests=["AI", "coding"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "searches.json")
            demand.log_search(path, "JC", ["AI"])
            demand.log_search(path, "JC", ["design"])

            preview = sender.build_sender_preview(opportunity, [], path)

        self.assertEqual(preview["demand_matches"], 1)
        self.assertEqual(preview["access_score"], 90)
        self.assertFalse(preview["duplicate_title"])

    def test_priority_label_marks_unmet_and_thin_rows(self):
        """Priority labels should make sender gap rows easy to read."""
        unmet = {"demand": 4, "supply": 1, "gap_score": 3}
        thin = {"demand": 1, "supply": 2, "gap_score": -1}
        covered = {"demand": 1, "supply": 5, "gap_score": -4}
        fallback = {"demand": 0, "supply": 1, "gap_score": -1}

        self.assertEqual(sender.priority_label(unmet), "UNMET")
        self.assertEqual(sender.priority_label(thin), "THIN")
        self.assertEqual(sender.priority_label(covered), "COVERED")
        self.assertEqual(sender.priority_label(fallback), "LOW SUPPLY")

    def test_announcement_file_is_written(self):
        """Sender announcement should be saved as a reusable text artifact."""
        opportunity = make_opportunity("opp-001", "Research Sprint")

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "packet.txt")
            written = sender.save_announcement(path, opportunity)

            with open(written, "r", encoding="utf-8") as file_handle:
                content = file_handle.read()

        self.assertIn("Research Sprint", content)
        self.assertIn("Sent through Opportunity Radar", content)


if __name__ == "__main__":
    unittest.main()
