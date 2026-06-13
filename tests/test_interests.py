"""Tests for the recursive interest taxonomy module."""

import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import interests


SAMPLE_TREE = {
    "Technology": {
        "AI": {
            "machine learning": {},
            "computer vision": {},
        },
        "coding": {
            "algorithms": {},
        },
        "cybersecurity": {},
    },
    "Business": {
        "entrepreneurship": {},
        "finance": {
            "fintech": {},
        },
    },
}


class TestInterests(unittest.TestCase):
    """Test cases for expand_interest and get_expanded_interests."""

    def test_expand_leaf_returns_single_name(self):
        """Expanding a leaf node returns just that node name."""
        result = interests.expand_interest(SAMPLE_TREE, "cybersecurity")
        self.assertEqual(result, ["cybersecurity"])

    def test_expand_mid_node_returns_all_leaves(self):
        """Expanding a mid-level node returns all its leaf descendants."""
        result = interests.expand_interest(SAMPLE_TREE, "AI")
        self.assertIn("machine learning", result)
        self.assertIn("computer vision", result)
        self.assertEqual(len(result), 2)

    def test_expand_top_node_recurses_all_depths(self):
        """Expanding a top-level node gathers leaves at every depth — proving genuine recursion."""
        result = interests.expand_interest(SAMPLE_TREE, "Technology")
        self.assertIn("machine learning", result)
        self.assertIn("computer vision", result)
        self.assertIn("algorithms", result)
        self.assertIn("cybersecurity", result)
        # Technology > AI (2 leaves) + coding (1 leaf) + cybersecurity (1 leaf) = 4 total
        self.assertEqual(len(result), 4)

    def test_expand_three_level_deep_node(self):
        """Expanding 'finance' reaches 'fintech' two levels down from root."""
        result = interests.expand_interest(SAMPLE_TREE, "finance")
        self.assertIn("fintech", result)

    def test_expand_unknown_name_returns_empty(self):
        """Searching for a node that does not exist anywhere returns an empty list."""
        result = interests.expand_interest(SAMPLE_TREE, "marine biology")
        self.assertEqual(result, [])

    def test_get_expanded_interests_broad_and_leaf(self):
        """get_expanded_interests expands broad interests and keeps unknown ones as-is."""
        raw = ["cybersecurity", "marine biology"]
        result = interests.get_expanded_interests(SAMPLE_TREE, raw)
        self.assertIn("cybersecurity", result)
        self.assertIn("marine biology", result)

    def test_get_expanded_interests_no_duplicates(self):
        """Duplicate leaves are deduplicated in the output."""
        raw = ["AI", "machine learning"]
        result = interests.get_expanded_interests(SAMPLE_TREE, raw)
        self.assertEqual(result.count("machine learning"), 1)


if __name__ == "__main__":
    unittest.main()
