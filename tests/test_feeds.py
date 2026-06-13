"""Tests for the structured-feed ingestion module (offline, no network)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import feeds


SAMPLE_RSS = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Sample Feed</title>
    <item>
      <title>NUS Coding Hackathon 2026</title>
      <link>https://example.com/hackathon</link>
      <description>A coding and AI hackathon for students.</description>
    </item>
    <item>
      <title>Design Workshop</title>
      <link>https://example.com/design</link>
      <description>Hands-on design session.</description>
    </item>
  </channel>
</rss>"""

SAMPLE_ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Sample</title>
  <entry>
    <title>Cybersecurity Olympiad</title>
    <link href="https://example.com/cyber"/>
    <summary>National cybersecurity competition.</summary>
  </entry>
</feed>"""


class TestFeeds(unittest.TestCase):
    """Test cases for parse_feed_items, item_to_opportunity, and merge."""

    def test_parse_rss_returns_all_items(self):
        """parse_feed_items reads every <item> from an RSS feed."""
        items = feeds.parse_feed_items(SAMPLE_RSS)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "NUS Coding Hackathon 2026")
        self.assertEqual(items[0]["link"], "https://example.com/hackathon")

    def test_parse_atom_reads_href_link(self):
        """parse_feed_items reads the href link from an Atom <entry>."""
        items = feeds.parse_feed_items(SAMPLE_ATOM)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["link"], "https://example.com/cyber")

    def test_parse_invalid_xml_returns_empty(self):
        """parse_feed_items returns an empty list for non-XML input."""
        self.assertEqual(feeds.parse_feed_items("not xml at all"), [])

    def test_item_to_opportunity_guesses_interests(self):
        """item_to_opportunity tags interests it detects in the title and summary."""
        items = feeds.parse_feed_items(SAMPLE_RSS)
        pool = ["coding", "AI", "design"]
        opp = feeds.item_to_opportunity(items[0], "feed-001", pool)
        self.assertIn("coding", opp.interests)
        self.assertIn("AI", opp.interests)

    def test_merge_skips_duplicate_titles(self):
        """merge_opportunities does not add an opportunity whose title already exists."""
        items = feeds.parse_feed_items(SAMPLE_RSS)
        imported = feeds.import_items_as_opportunities(items, 1, ["coding", "design"])
        existing = list(imported)  # same titles already present
        added = feeds.merge_opportunities(existing, imported)
        self.assertEqual(len(added), 0)


if __name__ == "__main__":
    unittest.main()
