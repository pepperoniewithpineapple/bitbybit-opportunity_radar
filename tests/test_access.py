"""Tests for the invisible starting-line simulation."""

import datetime
import unittest

import access
from models import Opportunity
from models import Student


TODAY = datetime.date(2026, 6, 13)


def make_opportunity(opp_id, cost="free", beginner=True, opp_type="workshop"):
    """Build a small Opportunity fixture for access simulation tests."""
    return Opportunity(
        opp_id,
        "Opportunity " + opp_id,
        opp_type,
        ["coding"],
        ["JC"],
        cost,
        beginner,
        "2026-06-20",
        "https://example.com/" + opp_id,
        "Test Organizer",
    )


class TestAccessSimulation(unittest.TestCase):
    """Check that the access simulation is bounded, transparent, and useful."""

    def test_awareness_probability_stays_in_bounds(self):
        """Probability should always stay inside the 0..1 range."""
        student = Student("Ari", "JC", ["coding"])
        opportunity = make_opportunity("free")

        probability = access.awareness_probability(
            opportunity,
            student,
            "quiet",
            TODAY,
        )

        self.assertGreaterEqual(probability, 0)
        self.assertLessEqual(probability, 1)

    def test_free_beginner_opportunity_is_easier_to_discover(self):
        """A free beginner workshop should beat a paid specialist item."""
        student = Student("Bea", "JC", ["coding"])
        friendly = make_opportunity("friendly", "free", True, "workshop")
        hidden = make_opportunity("hidden", "paid", False, "olympiad")

        friendly_probability = access.awareness_probability(
            friendly,
            student,
            "quiet",
            TODAY,
        )
        hidden_probability = access.awareness_probability(
            hidden,
            student,
            "quiet",
            TODAY,
        )

        self.assertGreater(friendly_probability, hidden_probability)

    def test_access_report_shows_radar_recovers_opportunities(self):
        """Radar access should be higher than estimated pre-Radar awareness."""
        student = Student("Cal", "JC", ["coding"])
        opportunities = [
            make_opportunity("free", "free", True, "workshop"),
            make_opportunity("paid", "paid", False, "olympiad"),
        ]

        report = access.build_access_report(opportunities, student, TODAY)
        quiet_summary = report["personas"][0]

        self.assertEqual(report["eligible_count"], 2)
        self.assertEqual(quiet_summary["after_radar"], 2)
        self.assertGreater(quiet_summary["recovered"], 0)

    def test_hidden_high_fit_finds_strong_match_with_low_visibility(self):
        """A strong match can still be hidden when its information channel is narrow."""
        student = Student("Dee", "JC", ["coding"])
        opportunity = make_opportunity("narrow", "paid", False, "olympiad")

        report = access.build_access_report([opportunity], student, TODAY)
        hidden = access.find_hidden_high_fit(report, "quiet")

        self.assertEqual(len(hidden), 1)
        self.assertEqual(hidden[0]["opportunity"].id, "narrow")


if __name__ == "__main__":
    unittest.main()
