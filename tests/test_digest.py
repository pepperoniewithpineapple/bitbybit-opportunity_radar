"""Tests for the weekly digest generator."""

import datetime
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import digest
from models import Opportunity, Student


def make_result(title, organizer, deadline, days_left, url="http://example.com"):
    """Build a minimal matcher result dict for testing digest output."""
    opp = Opportunity(
        "test-1", title, "hackathon",
        ["coding"], ["JC"],
        "free", True, deadline,
        url, organizer,
    )
    reasons = ["✓ Interests matched: coding (1 shared)"]
    breakdown = {
        "shared_interests": ["coding"],
        "shared_count": 1,
        "student_interest_count": 1,
        "interest_score": 0.5,
        "days_left": days_left,
        "urgency_score": 0.1,
        "equity_boost": 0.15,
        "total": 0.75,
    }
    return {"opportunity": opp, "score": 0.75, "reasons": reasons, "breakdown": breakdown}


class TestDigest(unittest.TestCase):
    """Test cases for digest.generate_digest."""

    def setUp(self):
        """Create a temporary file path and a student for testing."""
        self.student = Student("Wei Ming", "JC", ["coding", "AI"])
        self.tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt"
        )
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        """Remove the temporary file after each test."""
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_digest_file_is_written(self):
        """generate_digest creates a file at the given path."""
        results = [make_result("NUS Hackathon", "NUS", "2026-07-01", 18)]
        digest.generate_digest(results, self.student, self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_digest_contains_header(self):
        """The generated file contains the required header line."""
        results = [make_result("NUS Hackathon", "NUS", "2026-07-01", 18)]
        digest.generate_digest(results, self.student, self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("OPPORTUNITY RADAR", content)

    def test_digest_contains_top_match_title(self):
        """The top match title appears in the generated digest."""
        results = [make_result("NUS Hackathon", "NUS", "2026-07-01", 18)]
        digest.generate_digest(results, self.student, self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("NUS Hackathon", content)

    def test_digest_contains_closing_line(self):
        """The generated digest contains the sharing footer line."""
        results = [make_result("NUS Hackathon", "NUS", "2026-07-01", 18)]
        digest.generate_digest(results, self.student, self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Shared from Opportunity Radar", content)

    def test_digest_handles_empty_results(self):
        """generate_digest does not crash when there are no results."""
        digest.generate_digest([], self.student, self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_digest_returns_absolute_path(self):
        """generate_digest returns the absolute path of the written file."""
        results = [make_result("NUS Hackathon", "NUS", "2026-07-01", 18)]
        returned = digest.generate_digest(results, self.student, self.path)
        self.assertTrue(os.path.isabs(returned))


if __name__ == "__main__":
    unittest.main()
