"""Tests for storage.load_student, save_student, and next_opportunity_id."""

import sys
import os
import json
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import storage
from models import Opportunity, Student


def make_opp(opp_id):
    """Build a minimal Opportunity for testing."""
    return Opportunity(
        opp_id,
        "Title " + opp_id,
        "hackathon",
        ["coding"],
        ["JC"],
        "free",
        True,
        "2099-12-31",
        "https://example.com",
        "Organizer",
    )


class TestLoadStudent(unittest.TestCase):

    def test_returns_none_when_file_missing(self):
        result = storage.load_student("/nonexistent/path/student.json")
        self.assertIsNone(result)

    def test_loads_valid_student(self):
        data = {"name": "Wei Ming", "level": "JC", "interests": ["coding", "AI"]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name

        try:
            student = storage.load_student(tmp_path)
            self.assertIsNotNone(student)
            self.assertEqual(student.name, "Wei Ming")
            self.assertEqual(student.level, "JC")
            self.assertEqual(student.interests, ["coding", "AI"])
        finally:
            os.unlink(tmp_path)

    def test_returns_none_on_corrupt_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("NOT VALID JSON }{")
            tmp_path = tmp.name

        try:
            result = storage.load_student(tmp_path)
            self.assertIsNone(result)
        finally:
            os.unlink(tmp_path)

    def test_returns_none_on_missing_keys(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump({"name": "Wei Ming"}, tmp)
            tmp_path = tmp.name

        try:
            result = storage.load_student(tmp_path)
            self.assertIsNone(result)
        finally:
            os.unlink(tmp_path)


class TestSaveStudent(unittest.TestCase):

    def test_save_and_reload(self):
        student = Student("Siti", "Secondary", ["robotics", "chess"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "student.json")
            storage.save_student(path, student)

            loaded = storage.load_student(path)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.name, "Siti")
            self.assertEqual(loaded.level, "Secondary")
            self.assertEqual(loaded.interests, ["robotics", "chess"])

    def test_overwrite_existing_file(self):
        student_a = Student("Ali", "JC", ["coding"])
        student_b = Student("Beng", "Poly", ["music"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "student.json")
            storage.save_student(path, student_a)
            storage.save_student(path, student_b)

            loaded = storage.load_student(path)
            self.assertEqual(loaded.name, "Beng")

    def test_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested = os.path.join(tmp_dir, "sub", "student.json")
            student = Student("Ali", "JC", ["coding"])
            storage.save_student(nested, student)
            self.assertTrue(os.path.exists(nested))


class TestNextOpportunityId(unittest.TestCase):

    def test_returns_opp_001_when_empty(self):
        result = storage.next_opportunity_id([])
        self.assertEqual(result, "opp-001")

    def test_increments_past_highest(self):
        opps = [make_opp("opp-005"), make_opp("opp-012"), make_opp("opp-003")]
        result = storage.next_opportunity_id(opps)
        self.assertEqual(result, "opp-013")

    def test_ignores_non_standard_ids(self):
        opps = [make_opp("custom-id"), make_opp("opp-007")]
        result = storage.next_opportunity_id(opps)
        self.assertEqual(result, "opp-008")

    def test_zero_pads_to_three_digits(self):
        opps = [make_opp("opp-009")]
        result = storage.next_opportunity_id(opps)
        self.assertEqual(result, "opp-010")
