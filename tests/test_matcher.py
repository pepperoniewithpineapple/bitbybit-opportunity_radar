"""Unit tests for Opportunity Radar matcher scoring and filters."""

import datetime
import unittest

import matcher
from models import Opportunity
from models import Student


class TestMatcher(unittest.TestCase):
    """Check the MVP-1 matcher formula, ordering, and hard filters."""

    def make_opportunity(self, opp_id, deadline, level="JC", cost="free",
                         beginner_friendly=True, interests=None):
        """Create a small opportunity fixture for matcher tests."""
        if interests is None:
            interests = ["AI"]

        return Opportunity(
            opp_id,
            "Test Opportunity " + opp_id,
            "competition",
            interests,
            [level],
            cost,
            beginner_friendly,
            deadline,
            "https://example.com/" + opp_id,
            "Test Organizer",
        )

    def test_scoring_math_is_exact(self):
        """Verify interest, urgency, equity, and total score math."""
        student = Student("Ari", "JC", ["AI", "coding"])
        opportunity = self.make_opportunity(
            "math",
            "2026-06-28",
            interests=["AI", "science"],
            cost="free",
            beginner_friendly=True,
        )

        result = matcher.score_opportunity(
            opportunity,
            student,
            datetime.date(2026, 6, 13),
        )

        self.assertAlmostEqual(result["breakdown"]["interest_score"], 0.25)
        self.assertAlmostEqual(result["breakdown"]["urgency_score"], 0.15)
        self.assertAlmostEqual(result["breakdown"]["equity_boost"], 0.15)
        self.assertAlmostEqual(result["score"], 0.55)

    def test_filter_drops_ineligible_and_expired(self):
        """Verify level mismatch and expired deadlines are hard-filtered."""
        student = Student("Bea", "JC", ["AI"])
        open_match = self.make_opportunity("open", "2026-06-20", level="JC")
        ineligible = self.make_opportunity("poly", "2026-06-20", level="Poly")
        expired = self.make_opportunity("old", "2026-06-01", level="JC")

        results = matcher.rank_opportunities(
            [open_match, ineligible, expired],
            student,
            datetime.date(2026, 6, 13),
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["opportunity"].id, "open")

    def test_ordering_uses_total_descending(self):
        """Verify stronger matches rank above weaker matches."""
        student = Student("Cal", "JC", ["AI", "coding"])
        strong = self.make_opportunity(
            "strong",
            "2026-06-20",
            interests=["AI", "coding"],
            cost="free",
            beginner_friendly=True,
        )
        weak = self.make_opportunity(
            "weak",
            "2026-06-20",
            interests=["history"],
            cost="paid",
            beginner_friendly=False,
        )

        results = matcher.rank_opportunities(
            [weak, strong],
            student,
            datetime.date(2026, 6, 13),
        )

        self.assertEqual(results[0]["opportunity"].id, "strong")
        self.assertEqual(results[1]["opportunity"].id, "weak")

    def test_fuzzy_matching_catches_near_synonyms(self):
        """Verify fuzzy matching counts a near-spelling that exact matching misses."""
        student = Student("Fuzz", "JC", ["cybersecurity"])
        opportunity = self.make_opportunity(
            "fuzzy",
            "2026-06-20",
            interests=["cybersecurty"],  # deliberate typo, no exact match
        )

        exact = matcher.find_shared_interests(student, opportunity, use_fuzzy=False)
        fuzzy = matcher.find_shared_interests(student, opportunity, use_fuzzy=True)

        self.assertEqual(len(exact), 0)
        self.assertEqual(len(fuzzy), 1)

    def test_equity_boost_changes_order_between_otherwise_equal_items(self):
        """Verify free and beginner-friendly boosts can move an item up."""
        student = Student("Dee", "JC", ["AI"])
        paid = self.make_opportunity(
            "paid",
            "2026-07-01",
            interests=["AI"],
            cost="paid",
            beginner_friendly=False,
        )
        accessible = self.make_opportunity(
            "accessible",
            "2026-07-01",
            interests=["AI"],
            cost="free",
            beginner_friendly=True,
        )

        results = matcher.rank_opportunities(
            [paid, accessible],
            student,
            datetime.date(2026, 6, 13),
        )

        self.assertEqual(results[0]["opportunity"].id, "accessible")
        self.assertGreater(results[0]["score"], results[1]["score"])


if __name__ == "__main__":
    unittest.main()
