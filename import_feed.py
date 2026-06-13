"""Command-line runner for importing opportunities from a structured feed.

Usage:
    python import_feed.py <RSS-or-Atom-feed-URL>

This fetches a real structured feed, converts each entry into an Opportunity,
and merges new ones into data/opportunities.json (skipping duplicate titles).
Run it offline before a demo so the data is cached in the JSON file — the app
never depends on the network at runtime.

Only the Python standard library is used (urllib + xml.etree, via feeds.py).
"""

import os
import sys

import feeds
import storage


INTEREST_POOL = [
    "coding", "AI", "cybersecurity", "robotics", "data science", "design",
    "entrepreneurship", "finance", "fintech", "science", "research", "math",
    "engineering", "public good", "social impact", "sustainability",
]


def build_opportunities_path():
    """Return the path to the curated opportunities JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "opportunities.json")


def main():
    """Fetch a feed from the URL argument and merge new opportunities into the store."""
    if len(sys.argv) < 2:
        print("Usage: python import_feed.py <RSS-or-Atom-feed-URL>")
        return 1

    url = sys.argv[1]
    path = build_opportunities_path()
    existing = storage.load_opportunities(path)

    print("Fetching feed: " + url)
    try:
        feed_text = feeds.fetch_feed_text(url)
    except Exception as error:
        print("Could not fetch the feed: " + str(error))
        print("Check the URL and your internet connection.")
        return 1

    items = feeds.parse_feed_items(feed_text)
    print("Parsed " + str(len(items)) + " items from the feed.")

    if len(items) == 0:
        print("No items found. The URL may not be a valid RSS or Atom feed.")
        return 1

    imported = feeds.import_items_as_opportunities(items, 1, INTEREST_POOL)
    added = feeds.merge_opportunities(existing, imported)

    storage.save_opportunities(path, existing)
    print("Added " + str(len(added)) + " new opportunities (duplicates skipped).")
    print("Saved to " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
