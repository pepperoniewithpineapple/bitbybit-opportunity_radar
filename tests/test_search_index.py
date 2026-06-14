"""Tests for optional SQLite FTS and Python TF-IDF search."""

import unittest

import search_index
from models import Opportunity


def make_opp(opp_id, title, interests):
    """Build a search opportunity fixture."""
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
        "Organizer",
    )


class TestSearchIndex(unittest.TestCase):
    """Check generated search index behavior."""

    def test_tfidf_search_finds_matching_document(self):
        ai = make_opp("opp-001", "AI Coding Sprint", ["AI", "coding"])
        music = make_opp("opp-002", "Music Showcase", ["music"])

        results = search_index.tfidf_search([music, ai], "AI coding")

        self.assertEqual(results[0]["opportunity"].id, "opp-001")
        self.assertEqual(results[0]["engine"], "python-tfidf")

    def test_search_opportunities_can_force_fallback(self):
        ai = make_opp("opp-001", "AI Coding Sprint", ["AI", "coding"])
        music = make_opp("opp-002", "Music Showcase", ["music"])

        results = search_index.search_opportunities(
            [music, ai],
            "AI coding",
            force_fallback=True,
        )

        self.assertEqual(results[0]["opportunity"].id, "opp-001")
        self.assertEqual(results[0]["engine"], "python-tfidf")

    def test_empty_query_returns_no_results(self):
        ai = make_opp("opp-001", "AI Coding Sprint", ["AI", "coding"])

        self.assertEqual(search_index.search_opportunities([ai], "!!!"), [])


if __name__ == "__main__":
    unittest.main()
