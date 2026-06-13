"""Tests for the bias self-audit module."""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fairness
from models import Opportunity, Student


def make_opp(opp_id, cost, beginner, interests):
    """Create an opportunity open to JC with a future deadline for audit tests."""
    future = (datetime.date.today() + datetime.timedelta(days=20)).isoformat()
    return Opportunity(
        opp_id, "Opp " + opp_id, "competition",
        interests, ["JC"], cost, beginner, future,
        "http://example.com", "Org"
    )


class TestFairness(unittest.TestCase):
    """Test cases for free_share_in_top and audit."""

    def test_free_share_in_top_counts_correctly(self):
        """free_share_in_top returns the fraction of free opportunities in the top N."""
        opps = [
            make_opp("a", "free", True, ["AI"]),
            make_opp("b", "paid", False, ["AI"]),
            make_opp("c", "free", True, ["AI"]),
            make_opp("d", "paid", False, ["AI"]),
        ]
        share = fairness.free_share_in_top(opps, 4)
        self.assertAlmostEqual(share, 0.5)

    def test_audit_reports_nonnegative_lift_when_free_are_accessible(self):
        """When free opportunities share interests, the equity weighting should not reduce their reach."""
        opps = [
            make_opp("free1", "free", True, ["AI"]),
            make_opp("free2", "free", True, ["AI"]),
            make_opp("paid1", "paid", False, ["AI"]),
            make_opp("paid2", "paid", False, ["AI"]),
        ]
        students = [Student("s1", "JC", ["AI"])]
        report = fairness.audit(opps, students, today=datetime.date.today(), top_n=2)
        self.assertGreaterEqual(report["equity_free_share"], report["neutral_free_share"])

    def test_audit_counts_students_tested(self):
        """audit reports how many students were actually evaluated."""
        opps = [make_opp("a", "free", True, ["AI"])]
        students = [Student("s1", "JC", ["AI"]), Student("s2", "JC", ["AI"])]
        report = fairness.audit(opps, students, today=datetime.date.today())
        self.assertEqual(report["students_tested"], 2)


if __name__ == "__main__":
    unittest.main()
