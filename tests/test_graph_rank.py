"""Tests for graph-based hidden opportunity discovery."""

import unittest

import graph_rank
from models import Opportunity
from models import Student


def make_opp(opp_id, title, interests, opp_type="workshop"):
    """Build a graph ranking opportunity fixture."""
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
        "Organizer " + opp_id,
    )


class TestGraphRank(unittest.TestCase):
    """Check graph ranking and path explanations."""

    def test_rank_hidden_opportunities_surfaces_career_bridge(self):
        student = Student("Wei Ming", "JC", ["cybersecurity"])
        ai = make_opp("opp-001", "AI Defence Sprint", ["AI", "defence tech"])
        music = make_opp("opp-002", "Music Showcase", ["music"])

        rows = graph_rank.rank_hidden_opportunities(
            [music, ai],
            student,
            "cybersecurity analyst",
            limit=2,
        )

        self.assertEqual(rows[0]["opportunity"].id, "opp-001")
        self.assertIn("AI Defence Sprint", rows[0]["path_text"])
        self.assertIn("cybersecurity", rows[0]["path_text"])

    def test_personalized_pagerank_is_stable(self):
        graph = {
            "interest:coding": {"opportunity:one": 1.0},
            "opportunity:one": {"interest:coding": 1.0},
        }
        restart = {"interest:coding": 1.0}

        scores = graph_rank.personalized_pagerank(graph, restart, iterations=10)

        self.assertGreater(scores["interest:coding"], 0)
        self.assertGreater(scores["opportunity:one"], 0)


if __name__ == "__main__":
    unittest.main()
