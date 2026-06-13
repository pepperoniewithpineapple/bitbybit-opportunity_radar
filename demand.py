"""Anonymous demand-signal logging for Opportunity Radar.

Every student search is logged (level + interests + timestamp, no name) so the
opportunity-gap map can be driven by REAL demand instead of guesses. This is the
working version of the 'data flywheel': the more the tool is used, the clearer
the picture of where access breaks down.
"""

import datetime
import json
import os


def log_search(path, level, interests):
    """Append one anonymous search record to the demand log JSON file."""
    record = {
        "level": level,
        "interests": [interest.strip().lower() for interest in interests],
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }

    log = load_log(path)
    log.append(record)

    folder = os.path.dirname(path)
    if folder != "" and not os.path.exists(folder):
        os.makedirs(folder)

    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(log, file_handle, indent=2)

    return record


def load_log(path):
    """Load the demand log, returning an empty list if missing or corrupt."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except (json.JSONDecodeError, ValueError):
        return []


def demand_by_interest(path):
    """Aggregate the demand log into a {interest: search_count} dict."""
    log = load_log(path)
    counts = {}

    for record in log:
        for interest in record.get("interests", []):
            key = interest.strip().lower()
            counts[key] = counts.get(key, 0) + 1

    return counts


def gap_report(demand_counts, supply_counts):
    """Compare demand against supply and return a sorted gap list.

    Each entry is (interest, demand, supply, gap_score) where a higher gap_score
    means more students want it but fewer opportunities exist. This is the
    quantified opportunity gap.
    """
    gaps = []
    all_interests = set(demand_counts.keys()) | set(supply_counts.keys())

    for interest in all_interests:
        demand = demand_counts.get(interest, 0)
        supply = supply_counts.get(interest, 0)
        # Gap score: demand pressure relative to available supply.
        gap_score = demand - supply
        gaps.append((interest, demand, supply, gap_score))

    gaps.sort(key=lambda item: item[3], reverse=True)
    return gaps


def total_searches(path):
    """Return how many searches have been logged so far."""
    return len(load_log(path))
