"""Tests for filters.py — filter_by_type, filter_by_keyword, filter_by_deadline_window, sort_results."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import filters
from models import Opportunity


def make_result(title, opp_type, days_left, score=0.5):
    """Build a minimal ranked-result dict for testing."""
    opp = Opportunity(
        "opp-001",
        title,
        opp_type,
        ["coding"],
        ["JC"],
        "free",
        True,
        "2099-12-31",
        "https://example.com",
        "Organizer",
    )
    return {
        "opportunity": opp,
        "score": score,
        "breakdown": {"total": score, "days_left": days_left},
    }


class TestFilterByType(unittest.TestCase):

    def test_keeps_matching_type(self):
        results = [
            make_result("Hackathon A", "hackathon", 30),
            make_result("Scholarship B", "scholarship", 60),
            make_result("Hackathon C", "hackathon", 10),
        ]
        filtered = filters.filter_by_type(results, "hackathon")
        self.assertEqual(len(filtered), 2)
        for r in filtered:
            self.assertEqual(r["opportunity"].type, "hackathon")

    def test_returns_empty_when_no_match(self):
        results = [make_result("Hackathon A", "hackathon", 30)]
        filtered = filters.filter_by_type(results, "olympiad")
        self.assertEqual(len(filtered), 0)

    def test_empty_input(self):
        self.assertEqual(filters.filter_by_type([], "hackathon"), [])


class TestFilterByKeyword(unittest.TestCase):

    def test_case_insensitive_match(self):
        results = [
            make_result("National Coding Olympiad", "olympiad", 30),
            make_result("Hult Prize", "competition", 60),
        ]
        filtered = filters.filter_by_keyword(results, "CODING")
        self.assertEqual(len(filtered), 1)
        self.assertIn("Coding", filtered[0]["opportunity"].title)

    def test_empty_keyword_returns_all(self):
        results = [make_result("A", "hackathon", 10), make_result("B", "olympiad", 20)]
        self.assertEqual(len(filters.filter_by_keyword(results, "")), 2)

    def test_whitespace_keyword_returns_all(self):
        results = [make_result("A", "hackathon", 10)]
        self.assertEqual(len(filters.filter_by_keyword(results, "   ")), 1)

    def test_no_match(self):
        results = [make_result("Hackathon A", "hackathon", 30)]
        self.assertEqual(filters.filter_by_keyword(results, "scholarship"), [])


class TestFilterByDeadlineWindow(unittest.TestCase):

    def test_keeps_results_within_window(self):
        results = [
            make_result("A", "hackathon", 5),
            make_result("B", "olympiad", 30),
            make_result("C", "competition", 3),
        ]
        filtered = filters.filter_by_deadline_window(results, 7)
        self.assertEqual(len(filtered), 2)

    def test_exact_boundary_included(self):
        results = [make_result("A", "hackathon", 7)]
        self.assertEqual(len(filters.filter_by_deadline_window(results, 7)), 1)

    def test_beyond_boundary_excluded(self):
        results = [make_result("A", "hackathon", 8)]
        self.assertEqual(len(filters.filter_by_deadline_window(results, 7)), 0)


class TestSortResults(unittest.TestCase):

    def test_sort_by_score_descending(self):
        results = [
            make_result("A", "hackathon", 10, score=0.3),
            make_result("B", "hackathon", 10, score=0.9),
            make_result("C", "hackathon", 10, score=0.6),
        ]
        sorted_results = filters.sort_results(results, "score")
        scores = [r["score"] for r in sorted_results]
        self.assertEqual(scores, [0.9, 0.6, 0.3])

    def test_sort_by_deadline_ascending(self):
        results = [
            make_result("A", "hackathon", 30),
            make_result("B", "hackathon", 5),
            make_result("C", "hackathon", 15),
        ]
        sorted_results = filters.sort_results(results, "deadline")
        days = [r["breakdown"]["days_left"] for r in sorted_results]
        self.assertEqual(days, [5, 15, 30])

    def test_sort_by_title_alphabetical(self):
        results = [
            make_result("Zebra Hackathon", "hackathon", 10),
            make_result("Apple Olympiad", "olympiad", 10),
            make_result("Mango Prize", "competition", 10),
        ]
        sorted_results = filters.sort_results(results, "title")
        titles = [r["opportunity"].title for r in sorted_results]
        self.assertEqual(titles, ["Apple Olympiad", "Mango Prize", "Zebra Hackathon"])

    def test_unknown_key_falls_back_to_score(self):
        results = [
            make_result("A", "hackathon", 10, score=0.2),
            make_result("B", "hackathon", 10, score=0.8),
        ]
        sorted_results = filters.sort_results(results, "unknown_key")
        self.assertEqual(sorted_results[0]["score"], 0.8)
