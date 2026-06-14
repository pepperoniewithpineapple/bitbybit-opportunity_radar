"""Tests for the sender submission review queue."""

import os
import tempfile
import unittest

import demand
import review_queue
from models import Opportunity


def make_opportunity(opp_id="draft-001", title="AI Sprint",
                     deadline="2099-12-31", url="https://example.com"):
    """Build a reusable opportunity fixture."""
    return Opportunity(
        opp_id,
        title,
        "workshop",
        ["AI", "coding"],
        ["JC"],
        "free",
        True,
        deadline,
        url,
        "Example Org",
    )


class TestReviewQueue(unittest.TestCase):
    """Check queue storage, review states, and approval behavior."""

    def test_create_submission_assigns_pending_id(self):
        submissions = []
        opportunity = make_opportunity()

        submission = review_queue.create_submission(
            submissions,
            opportunity,
            "2026-06-14T10:00:00",
        )

        self.assertEqual(submission["submission_id"], "sub-001")
        self.assertEqual(submission["status"], review_queue.PENDING)
        self.assertEqual(submissions, [submission])

    def test_save_and_load_submissions_round_trip(self):
        submissions = [
            review_queue.build_submission(
                "sub-001",
                make_opportunity(),
                "2026-06-14T10:00:00",
            )
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "submissions.json")
            review_queue.save_submissions(path, submissions)

            loaded = review_queue.load_submissions(path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["submission_id"], "sub-001")
        self.assertEqual(loaded[0]["opportunity"].title, "AI Sprint")

    def test_pending_submissions_filters_reviewed_items(self):
        pending = review_queue.build_submission("sub-001", make_opportunity())
        approved = review_queue.build_submission("sub-002", make_opportunity())
        approved["status"] = review_queue.APPROVED

        result = review_queue.pending_submissions([pending, approved])

        self.assertEqual(result, [pending])

    def test_approve_submission_adds_to_live_store(self):
        submission = review_queue.build_submission("sub-001", make_opportunity())
        opportunities = []

        approved = review_queue.approve_submission(
            submission,
            opportunities,
            "opp-009",
            "2026-06-14T11:00:00",
            "Looks good",
        )

        self.assertTrue(approved)
        self.assertEqual(submission["status"], review_queue.APPROVED)
        self.assertEqual(submission["review_note"], "Looks good")
        self.assertEqual(opportunities[0].id, "opp-009")
        self.assertEqual(opportunities[0].title, "AI Sprint")

    def test_approve_submission_rejects_duplicate_live_title(self):
        live = [make_opportunity("opp-001", "AI Sprint")]
        submission = review_queue.build_submission("sub-001", make_opportunity())

        approved = review_queue.approve_submission(
            submission,
            live,
            "opp-002",
            "2026-06-14T11:00:00",
        )

        self.assertFalse(approved)
        self.assertEqual(submission["status"], review_queue.PENDING)
        self.assertEqual(len(live), 1)

    def test_reject_submission_saves_note(self):
        submission = review_queue.build_submission("sub-001", make_opportunity())

        rejected = review_queue.reject_submission(
            submission,
            "Please add an official link.",
            "2026-06-14T11:00:00",
        )

        self.assertTrue(rejected)
        self.assertEqual(submission["status"], review_queue.REJECTED)
        self.assertEqual(submission["review_note"], "Please add an official link.")

    def test_review_flags_show_blockers_and_demand_notes(self):
        live = [make_opportunity("opp-001", "AI Sprint")]
        submission = review_queue.build_submission(
            "sub-001",
            make_opportunity("draft-001", "AI Sprint", url="example.com"),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            searches_path = os.path.join(tmp_dir, "searches.json")
            flags = review_queue.review_flags(submission, live, searches_path)

        labels = [flag["label"] for flag in flags]

        self.assertIn("Duplicate title", labels)
        self.assertIn("URL format", labels)
        self.assertIn("No current demand match", labels)
        self.assertTrue(review_queue.has_blocker(flags))

    def test_review_flags_clear_when_demand_and_link_are_good(self):
        submission = review_queue.build_submission("sub-001", make_opportunity())

        with tempfile.TemporaryDirectory() as tmp_dir:
            searches_path = os.path.join(tmp_dir, "searches.json")
            demand.log_search(searches_path, "JC", ["AI"])
            flags = review_queue.review_flags(submission, [], searches_path)

        self.assertEqual(flags, [])


if __name__ == "__main__":
    unittest.main()
