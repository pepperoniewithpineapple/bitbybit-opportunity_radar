"""Unit tests for the central validation gateway."""

import unittest
from unittest import mock

import validation


class TestValidation(unittest.TestCase):
    """Check that validation rejects bad input and accepts good input."""

    def test_get_valid_int_rejects_junk_then_accepts_valid(self):
        """Verify letters and out-of-range numbers are rejected."""
        with mock.patch("builtins.input", side_effect=["abc", "9", "2"]):
            value = validation.get_valid_int("Number: ", 1, 3)

        self.assertEqual(value, 2)

    def test_get_valid_choice_rejects_bad_choice_then_accepts_valid(self):
        """Verify choices must match one of the allowed option strings."""
        with mock.patch("builtins.input", side_effect=["University", "JC"]):
            value = validation.get_valid_choice("Level: ", ["Secondary", "JC"])

        self.assertEqual(value, "JC")

    def test_get_valid_date_rejects_malformed_then_accepts_valid(self):
        """Verify empty, malformed, and impossible dates are rejected."""
        with mock.patch(
            "builtins.input",
            side_effect=["", "2026/07/01", "2026-02-30", "2026-07-01"],
        ):
            value = validation.get_valid_date("Date: ")

        self.assertEqual(value, "2026-07-01")

    def test_nonempty_rejects_blank_then_accepts_text(self):
        """Verify blank text is rejected and stripped text is returned."""
        with mock.patch("builtins.input", side_effect=["   ", "  Noor  "]):
            value = validation.nonempty("Name: ")

        self.assertEqual(value, "Noor")


if __name__ == "__main__":
    unittest.main()
