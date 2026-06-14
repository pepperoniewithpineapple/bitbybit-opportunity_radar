"""Tests for recommend.py — suggest_interests."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import recommend
from models import Opportunity, Student


def make_opp(opp_id, interests, eligible_levels=None, deadline="2099-12-31"):
    """Build a minimal Opportunity for testing."""
    if eligible_levels is None:
        eligible_levels = ["JC", "Secondary", "Poly", "University"]
    return Opportunity(
        opp_id,
        "Opp " + opp_id,
        "hackathon",
        interests,
        eligible_levels,
        "free",
        True,
        deadline,
        "https://example.com",
        "Organizer",
    )


EMPTY_TREE = {}

SIMPLE_TREE = {
    "Technology": {
        "children": {
            "AI": {"children": {}},
            "coding": {"children": {}},
        }
    }
}


class TestSuggestInterests(unittest.TestCase):

    def test_suggests_interest_from_unmatched_eligible_opp(self):
        student = Student("Ali", "JC", ["coding"])
        opps = [
            make_opp("opp-001", ["coding"]),
            make_opp("opp-002", ["robotics"]),
        ]
        suggestions = recommend.suggest_interests(opps, student, EMPTY_TREE, limit=3)
        interest_names = [name for name, count in suggestions]
        self.assertIn("robotics", interest_names)

    def test_does_not_suggest_existing_interest(self):
        student = Student("Ali", "JC", ["coding"])
        opps = [make_opp("opp-001", ["coding"])]
        suggestions = recommend.suggest_interests(opps, student, EMPTY_TREE, limit=3)
        interest_names = [name for name, count in suggestions]
        self.assertNotIn("coding", interest_names)

    def test_does_not_suggest_raw_interest_after_expansion(self):
        student = Student("Ali", "JC", ["AI"])
        tree = {
            "AI": {
                "machine learning": {},
                "computer vision": {},
            }
        }
        opps = [
            make_opp("opp-001", ["machine learning"]),
            make_opp("opp-002", ["AI"]),
        ]

        suggestions = recommend.suggest_interests(opps, student, tree, limit=3)
        interest_names = [name for name, count in suggestions]

        self.assertNotIn("AI", interest_names)

    def test_counts_are_correct(self):
        student = Student("Ali", "JC", ["coding"])
        opps = [
            make_opp("opp-001", ["robotics"]),
            make_opp("opp-002", ["robotics"]),
            make_opp("opp-003", ["music"]),
        ]
        suggestions = recommend.suggest_interests(opps, student, EMPTY_TREE, limit=3)
        counts = {name: count for name, count in suggestions}
        self.assertEqual(counts.get("robotics", 0), 2)
        self.assertEqual(counts.get("music", 0), 1)

    def test_respects_limit(self):
        student = Student("Ali", "JC", ["coding"])
        opps = [
            make_opp("opp-001", ["robotics"]),
            make_opp("opp-002", ["music"]),
            make_opp("opp-003", ["chess"]),
            make_opp("opp-004", ["debate"]),
        ]
        suggestions = recommend.suggest_interests(opps, student, EMPTY_TREE, limit=2)
        self.assertLessEqual(len(suggestions), 2)

    def test_ineligible_opp_not_suggested(self):
        student = Student("Ali", "JC", ["coding"])
        opps = [make_opp("opp-001", ["robotics"], eligible_levels=["University"])]
        suggestions = recommend.suggest_interests(opps, student, EMPTY_TREE, limit=3)
        interest_names = [name for name, count in suggestions]
        self.assertNotIn("robotics", interest_names)

    def test_empty_opportunities(self):
        student = Student("Ali", "JC", ["coding"])
        suggestions = recommend.suggest_interests([], student, EMPTY_TREE, limit=3)
        self.assertEqual(suggestions, [])

    def test_returns_list_of_tuples(self):
        student = Student("Ali", "JC", ["coding"])
        opps = [make_opp("opp-001", ["robotics"])]
        suggestions = recommend.suggest_interests(opps, student, EMPTY_TREE, limit=3)
        for item in suggestions:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], str)
            self.assertIsInstance(item[1], int)
