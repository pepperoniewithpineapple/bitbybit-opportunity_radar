"""Tests for career pathway planning."""

import unittest

import pathway
from models import Opportunity
from models import Student


def make_opp(opp_id, opp_type, interests, title=None):
    """Build a pathway opportunity fixture."""
    if title is None:
        title = opp_type.title() + " " + opp_id

    return Opportunity(
        opp_id,
        title,
        opp_type,
        interests,
        ["JC"],
        "free",
        True,
        "2099-12-31",
        "https://example.com",
        "Organizer",
    )


class TestPathway(unittest.TestCase):
    """Check pathway stage ordering and recommendation behavior."""

    def test_ordered_stages_follow_dependencies(self):
        stages = pathway.ordered_stages()

        self.assertLess(stages.index("foundation"), stages.index("practice"))
        self.assertLess(stages.index("practice"), stages.index("proof"))
        self.assertLess(stages.index("proof"), stages.index("launch"))

    def test_ordered_stages_reject_cycle(self):
        with self.assertRaises(ValueError):
            pathway.ordered_stages({
                "foundation": {"launch"},
                "launch": {"foundation"},
            })

    def test_build_pathway_uses_distinct_stage_opportunities(self):
        student = Student("Wei Ming", "JC", ["coding"])
        opportunities = [
            make_opp("one", "workshop", ["coding", "algorithms"]),
            make_opp("two", "hackathon", ["coding", "problem solving"]),
            make_opp("three", "research", ["AI", "research"]),
            make_opp("four", "scholarship", ["coding", "AI"]),
        ]

        plan = pathway.build_pathway(
            "software engineer",
            student,
            opportunities,
        )

        chosen = []
        for step in plan["steps"]:
            if step["opportunity"] is not None:
                chosen.append(step["opportunity"].id)

        self.assertEqual(len(chosen), len(set(chosen)))
        self.assertEqual(plan["steps"][0]["stage"], "foundation")
        self.assertGreater(len(plan["missing_skills"]), 0)


if __name__ == "__main__":
    unittest.main()
