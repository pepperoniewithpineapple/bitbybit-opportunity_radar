"""Tests for the career readiness impact model."""

import unittest

import career_model
from models import Opportunity
from models import Student


def make_opp(opp_id, interests, opp_type="workshop", cost="free", beginner=True):
    """Build a small opportunity fixture."""
    return Opportunity(
        opp_id,
        "Opportunity " + opp_id,
        opp_type,
        interests,
        ["JC"],
        cost,
        beginner,
        "2099-12-31",
        "https://example.com",
        "Organizer",
    )


class TestCareerModel(unittest.TestCase):
    """Check career score math and impact classifications."""

    def test_readiness_score_increases_with_matching_skills(self):
        """Relevant skills should produce a higher readiness score."""
        weak = career_model.readiness_score("software engineer", ["music"])
        strong = career_model.readiness_score(
            "software engineer",
            ["coding", "algorithms", "problem solving"],
        )

        self.assertGreater(strong, weak)

    def test_relevant_opportunity_increases_readiness(self):
        """A career-aligned opportunity should increase readiness alignment."""
        student = Student("Wei Ming", "JC", ["coding"])
        opportunity = make_opp(
            "cyber",
            ["cybersecurity", "coding", "problem solving"],
            "competition",
        )

        impact = career_model.evaluate_opportunity(
            "cybersecurity analyst",
            student,
            opportunity,
        )

        self.assertEqual(impact["classification"], "INCREASE")
        self.assertGreater(impact["delta"], 0)

    def test_off_track_paid_advanced_event_can_decrease_alignment(self):
        """A low-relevance paid advanced event can have a small negative impact."""
        student = Student("Wei Ming", "JC", ["coding", "algorithms"])
        opportunity = make_opp(
            "music",
            ["music"],
            "competition",
            cost="paid",
            beginner=False,
        )

        impact = career_model.evaluate_opportunity(
            "software engineer",
            student,
            opportunity,
        )

        self.assertEqual(impact["classification"], "DECREASE")
        self.assertLess(impact["delta"], 0)

    def test_low_relevance_free_beginner_event_can_be_no_change(self):
        """A low-friction but unrelated event should often be no change."""
        student = Student("Wei Ming", "JC", ["coding"])
        opportunity = make_opp("writing", ["writing"], "workshop", "free", True)

        impact = career_model.evaluate_opportunity(
            "software engineer",
            student,
            opportunity,
        )

        self.assertEqual(impact["classification"], "NO CHANGE")

    def test_rank_impacts_puts_best_booster_first(self):
        """rank_impacts should surface the strongest career booster first."""
        student = Student("Wei Ming", "JC", ["coding"])
        weak = make_opp("weak", ["music"])
        strong = make_opp("strong", ["cybersecurity", "problem solving"])

        impacts = career_model.rank_impacts(
            "cybersecurity analyst",
            student,
            [weak, strong],
        )

        self.assertEqual(impacts[0]["opportunity"].id, "strong")


if __name__ == "__main__":
    unittest.main()
