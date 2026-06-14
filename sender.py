"""Opportunity sender mode helpers for Opportunity Radar.

Sender mode turns the app into a two-sided tool. Students reveal anonymous
demand by searching. Organizers then use that demand to send opportunities into
real gaps instead of guessing what students need.
"""

import os

import demand
import matcher
import stats
from models import Opportunity


OPPORTUNITY_TYPES = [
    "competition",
    "hackathon",
    "scholarship",
    "workshop",
    "olympiad",
    "internship",
    "research",
    "volunteering",
    "programme",
    "other",
]


def normalize_interest(interest):
    """Return a normalized interest key for demand and duplicate checks."""
    return interest.strip().lower()


def title_exists(opportunities, title):
    """Return True when an opportunity with the same title already exists."""
    target = title.strip().lower()

    for opportunity in opportunities:
        if opportunity.title.strip().lower() == target:
            return True

    return False


def build_opportunity(opp_id, title, opp_type, interests, eligible_levels,
                      cost, beginner_friendly, deadline, url, organizer):
    """Build an Opportunity object from validated sender-mode fields."""
    return Opportunity(
        opp_id,
        title,
        opp_type,
        interests,
        eligible_levels,
        cost,
        beginner_friendly,
        deadline,
        url,
        organizer,
    )


def matching_demand_count(demand_counts, interests):
    """Return how many anonymous searches match any of the opportunity interests."""
    total = 0
    seen = set()

    for interest in interests:
        key = normalize_interest(interest)
        if key not in seen:
            total = total + demand_counts.get(key, 0)
            seen.add(key)

    return total


def build_gap_rows(opportunities, searches_path, limit=8):
    """Return demand-vs-supply rows for sender mode, highest gap first.

    Each row contains interest, demand, supply, and gap_score. The data comes
    from anonymous student searches and the current opportunity store.
    """
    demand_counts = demand.demand_by_interest(searches_path)
    supply_counts = stats.supply_by_interest(opportunities)
    gaps = demand.gap_report(demand_counts, supply_counts)

    rows = []
    for interest, demand_count, supply_count, gap_score in gaps:
        if demand_count <= 0:
            continue
        rows.append({
            "interest": interest,
            "demand": demand_count,
            "supply": supply_count,
            "gap_score": gap_score,
        })

    rows.sort(key=lambda row: (row["gap_score"], row["demand"]), reverse=True)
    return rows[:limit]


def build_supply_thin_rows(opportunities, limit=8):
    """Return low-supply interest rows for demos before demand data exists."""
    supply_counts = stats.supply_by_interest(opportunities)
    rows = []

    for interest, supply in supply_counts.items():
        rows.append({
            "interest": interest,
            "demand": 0,
            "supply": supply,
            "gap_score": -supply,
        })

    rows.sort(key=lambda row: (row["supply"], row["interest"]))
    return rows[:limit]


def priority_label(row):
    """Return a sender-friendly priority label for a demand/supply row."""
    if row["demand"] <= 0:
        return "LOW SUPPLY"
    if row["gap_score"] > 0:
        return "UNMET"
    if row["supply"] <= 2:
        return "THIN"
    return "COVERED"


def build_sender_preview(opportunity, opportunities, searches_path):
    """Return a short impact preview for a newly drafted opportunity."""
    demand_counts = demand.demand_by_interest(searches_path)
    demand_matches = matching_demand_count(demand_counts, opportunity.interests)
    days_left = matcher.days_until(opportunity.deadline)

    return {
        "duplicate_title": title_exists(opportunities, opportunity.title),
        "demand_matches": demand_matches,
        "level_count": len(opportunity.eligible_levels),
        "interest_count": len(opportunity.interests),
        "days_left": days_left,
        "access_score": sender_access_score(opportunity),
    }


def sender_access_score(opportunity):
    """Return a simple 0..100 score for how accessible a sent opportunity is."""
    score = 40

    if opportunity.cost == "free":
        score = score + 25
    if opportunity.beginner_friendly:
        score = score + 20
    if len(opportunity.eligible_levels) >= 3:
        score = score + 10
    if opportunity.type in ("workshop", "volunteering", "programme"):
        score = score + 5

    return matcher.clamp(score, 0, 100)


def add_opportunity(opportunities, opportunity):
    """Add opportunity if its title is new; return True when added."""
    if title_exists(opportunities, opportunity.title):
        return False

    opportunities.append(opportunity)
    return True


def build_announcement(opportunity):
    """Return a student-facing announcement for a posted opportunity."""
    lines = []
    lines.append("OPPORTUNITY RADAR - New Opportunity")
    lines.append("")
    lines.append(opportunity.title)
    lines.append("Organizer: " + opportunity.organizer)
    lines.append("Type: " + opportunity.type)
    lines.append("Deadline: " + opportunity.deadline)
    lines.append("Cost: " + opportunity.cost)
    lines.append("Open to: " + ", ".join(opportunity.eligible_levels))
    lines.append("Interests: " + ", ".join(opportunity.interests))
    if opportunity.beginner_friendly:
        lines.append("Beginner-friendly: yes")
    else:
        lines.append("Beginner-friendly: no")
    lines.append("Link: " + opportunity.url)
    lines.append("")
    lines.append("Sent through Opportunity Radar.")
    return "\n".join(lines)


def save_announcement(path, opportunity):
    """Write a sender announcement text file and return its absolute path."""
    absolute_path = os.path.abspath(path)
    folder = os.path.dirname(absolute_path)
    if folder != "" and not os.path.exists(folder):
        os.makedirs(folder)

    with open(absolute_path, "w", encoding="utf-8") as file_handle:
        file_handle.write(build_announcement(opportunity))

    return absolute_path
