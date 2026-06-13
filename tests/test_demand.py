"""Tests for the anonymous demand-signal logging module."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import demand


class TestDemand(unittest.TestCase):
    """Test cases for log_search, demand_by_interest, and gap_report."""

    def setUp(self):
        """Create a temporary demand-log path for each test."""
        handle = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        handle.close()
        self.path = handle.name
        # Start empty so counts are predictable.
        os.remove(self.path)

    def tearDown(self):
        """Remove the temporary file after each test."""
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_log_search_writes_record(self):
        """log_search appends a record that can be read back."""
        demand.log_search(self.path, "JC", ["coding", "AI"])
        self.assertEqual(demand.total_searches(self.path), 1)

    def test_demand_by_interest_aggregates_and_lowercases(self):
        """demand_by_interest counts interests case-insensitively across searches."""
        demand.log_search(self.path, "JC", ["Coding", "AI"])
        demand.log_search(self.path, "Poly", ["coding"])
        counts = demand.demand_by_interest(self.path)
        self.assertEqual(counts["coding"], 2)
        self.assertEqual(counts["ai"], 1)

    def test_gap_report_ranks_unmet_demand_first(self):
        """gap_report puts high-demand low-supply interests at the top."""
        demand_counts = {"coding": 5, "design": 1}
        supply_counts = {"coding": 1, "design": 4}
        report = demand.gap_report(demand_counts, supply_counts)
        # coding has gap 5-1=4; design has gap 1-4=-3, so coding ranks first.
        self.assertEqual(report[0][0], "coding")

    def test_load_log_missing_file_returns_empty(self):
        """load_log returns an empty list when the file does not exist."""
        self.assertEqual(demand.load_log(self.path), [])


if __name__ == "__main__":
    unittest.main()
