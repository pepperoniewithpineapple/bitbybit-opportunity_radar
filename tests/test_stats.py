"""Tests for the opportunity-gap statistics module."""

import datetime
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import stats
from models import Opportunity


def make_opp(opp_id, interests, cost, deadline, eligible_levels=None, beginner=True):
    """Create a minimal Opportunity object for testing."""
    if eligible_levels is None:
        eligible_levels = ["JC"]
    return Opportunity(
        opp_id, "Title " + opp_id, "competition",
        interests, eligible_levels,
        cost, beginner, deadline, "http://example.com", "Organizer"
    )


class TestStats(unittest.TestCase):
    """Test cases for stats.supply_by_interest, free_vs_paid_ratio, unmet_interests."""

    def setUp(self):
        """Set up a small set of opportunities for all tests."""
        future = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        past = "2020-01-01"

        self.opportunities = [
            make_opp("a", ["coding", "AI"], "free", future),
            make_opp("b", ["coding", "design"], "paid", future),
            make_opp("c", ["AI"], "free", future),
            make_opp("d", ["coding"], "paid", past),    # expired — should be excluded
        ]

    def test_supply_count_excludes_expired(self):
        """supply_by_interest should not count expired opportunities."""
        supply = stats.supply_by_interest(self.opportunities)
        # opp-d is expired so coding should be 2 (a and b), not 3
        self.assertEqual(supply.get("coding", 0), 2)

    def test_supply_count_is_correct(self):
        """supply_by_interest counts each open opportunity per interest tag."""
        supply = stats.supply_by_interest(self.opportunities)
        self.assertEqual(supply.get("ai", 0), 2)
        self.assertEqual(supply.get("design", 0), 1)

    def test_free_vs_paid_ratio_correct(self):
        """free_vs_paid_ratio returns correct counts for open opportunities."""
        ratio = stats.free_vs_paid_ratio(self.opportunities)
        # a and c are free and open; b is paid and open; d is expired
        self.assertEqual(ratio["free"], 2)
        self.assertEqual(ratio["paid"], 1)
        self.assertEqual(ratio["total"], 3)

    def test_free_pct_is_approximate(self):
        """Free percentage is approximately 67 percent for 2 free out of 3."""
        ratio = stats.free_vs_paid_ratio(self.opportunities)
        self.assertAlmostEqual(ratio["free_pct"], 67, delta=1)

    def test_unmet_interests_detects_gap(self):
        """unmet_interests flags interests with zero or below-threshold supply."""
        supply = {"coding": 2, "AI": 2}
        student_interests = ["coding", "marine biology", "AI"]
        unmet = stats.unmet_interests(student_interests, supply)
        unmet_names = [name for name, count in unmet]
        self.assertIn("marine biology", unmet_names)
        self.assertNotIn("coding", unmet_names)

    def test_unmet_interests_empty_when_all_covered(self):
        """unmet_interests returns empty list when every interest has supply."""
        # supply keys must be lowercase because supply_by_interest normalises them
        supply = {"coding": 3, "ai": 1}
        unmet = stats.unmet_interests(["coding", "AI"], supply)
        self.assertEqual(unmet, [])


if __name__ == "__main__":
    unittest.main()
