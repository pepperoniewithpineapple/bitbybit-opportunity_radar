"""Submission review queue for Opportunity Radar.

Sender submissions should not change the live student feed until a reviewer
approves them. This module keeps that gate as plain JSON and pure Python.
"""

import datetime
import json
import os

import matcher
import sender
import storage
from models import Opportunity


PENDING = "pending"
APPROVED = "approved"
REJECTED = "rejected"
STATUSES = [PENDING, APPROVED, REJECTED]


def current_timestamp():
    """Return an ISO timestamp suitable for JSON audit records."""
    return datetime.datetime.now().isoformat(timespec="seconds")


def next_submission_id(submissions):
    """Return a fresh submission id like 'sub-001'."""
    highest = 0

    for submission in submissions:
        submission_id = submission.get("submission_id", "")
        if submission_id.startswith("sub-"):
            number_part = submission_id[len("sub-"):]
            if number_part.isdigit():
                value = int(number_part)
                if value > highest:
                    highest = value

    return "sub-" + str(highest + 1).zfill(3)


def build_submission(submission_id, opportunity, submitted_at=None):
    """Build one pending review submission from an Opportunity object."""
    if submitted_at is None:
        submitted_at = current_timestamp()

    return {
        "submission_id": submission_id,
        "status": PENDING,
        "submitted_at": submitted_at,
        "reviewed_at": "",
        "review_note": "",
        "opportunity": opportunity,
    }


def create_submission(submissions, opportunity, submitted_at=None):
    """Append a pending submission and return it."""
    submission = build_submission(
        next_submission_id(submissions),
        opportunity,
        submitted_at,
    )
    submissions.append(submission)
    return submission


def opportunity_from_dict(record):
    """Convert a stored opportunity dictionary into an Opportunity object."""
    return Opportunity(
        record["id"],
        record["title"],
        record["type"],
        record["interests"],
        record["eligible_levels"],
        record["cost"],
        record["beginner_friendly"],
        record["deadline"],
        record["url"],
        record["organizer"],
    )


def submission_from_dict(record):
    """Convert a stored submission dictionary into runtime objects."""
    status = record["status"]
    if status not in STATUSES:
        raise ValueError("unknown status")

    opportunity = opportunity_from_dict(record["opportunity"])

    return {
        "submission_id": record["submission_id"],
        "status": status,
        "submitted_at": record["submitted_at"],
        "reviewed_at": record.get("reviewed_at", ""),
        "review_note": record.get("review_note", ""),
        "opportunity": opportunity,
    }


def submission_to_dict(submission):
    """Convert one runtime submission into JSON-friendly data."""
    return {
        "submission_id": submission["submission_id"],
        "status": submission["status"],
        "submitted_at": submission["submitted_at"],
        "reviewed_at": submission.get("reviewed_at", ""),
        "review_note": submission.get("review_note", ""),
        "opportunity": submission["opportunity"].to_dict(),
    }


def load_submissions(path):
    """Load review submissions, returning an empty list if unavailable."""
    if not os.path.exists(path):
        return []

    try:
        records = storage.load_json(path)
    except (json.JSONDecodeError, ValueError, OSError):
        print("Notice: submissions file could not be read. Using empty queue.")
        return []

    if not isinstance(records, list):
        print("Notice: submissions file was not a list. Using empty queue.")
        return []

    submissions = []
    for record in records:
        try:
            submissions.append(submission_from_dict(record))
        except (KeyError, TypeError, ValueError):
            print("Notice: skipped one invalid submission record.")

    return submissions


def save_submissions(path, submissions):
    """Save review submissions to JSON."""
    records = []
    for submission in submissions:
        records.append(submission_to_dict(submission))
    storage.save_json(path, records)


def pending_submissions(submissions):
    """Return submissions still waiting for review."""
    pending = []
    for submission in submissions:
        if submission.get("status") == PENDING:
            pending.append(submission)
    return pending


def status_counts(submissions):
    """Return a small status-count dictionary for queue dashboards."""
    counts = {PENDING: 0, APPROVED: 0, REJECTED: 0}
    for submission in submissions:
        status = submission.get("status")
        if status in counts:
            counts[status] = counts[status] + 1
    return counts


def review_flags(submission, opportunities, searches_path):
    """Return quality flags a reviewer should consider before approval."""
    opportunity = submission["opportunity"]
    preview = sender.build_sender_preview(opportunity, opportunities, searches_path)
    days_left = matcher.days_until(opportunity.deadline)
    flags = []

    if preview["duplicate_title"]:
        flags.append({
            "severity": "BLOCKER",
            "label": "Duplicate title",
            "detail": "A live opportunity already uses this title.",
        })

    if days_left < 0:
        flags.append({
            "severity": "BLOCKER",
            "label": "Closed deadline",
            "detail": "The deadline has already passed.",
        })
    elif days_left < 7:
        flags.append({
            "severity": "WARNING",
            "label": "Very close deadline",
            "detail": "Students may not have enough time to apply.",
        })

    if not opportunity.url.lower().startswith(("http://", "https://")):
        flags.append({
            "severity": "WARNING",
            "label": "URL format",
            "detail": "The link should start with http:// or https://.",
        })

    if opportunity.cost == "paid" and not opportunity.beginner_friendly:
        flags.append({
            "severity": "WARNING",
            "label": "Access friction",
            "detail": "Paid and not beginner-friendly may narrow access.",
        })

    if preview["demand_matches"] == 0:
        flags.append({
            "severity": "NOTE",
            "label": "No current demand match",
            "detail": "No anonymous searches currently match these interests.",
        })

    return flags


def has_blocker(flags):
    """Return True when review flags contain an approval blocker."""
    for flag in flags:
        if flag["severity"] == "BLOCKER":
            return True
    return False


def approve_submission(submission, opportunities, new_opp_id,
                       reviewed_at=None, note=""):
    """Approve one pending submission and append it to the live store."""
    if submission.get("status") != PENDING:
        return False

    opportunity = submission["opportunity"]
    if sender.title_exists(opportunities, opportunity.title):
        return False

    if reviewed_at is None:
        reviewed_at = current_timestamp()

    opportunity.id = new_opp_id
    opportunities.append(opportunity)
    submission["status"] = APPROVED
    submission["reviewed_at"] = reviewed_at
    submission["review_note"] = note.strip()
    return True


def reject_submission(submission, note, reviewed_at=None):
    """Reject one pending submission with a reviewer note."""
    if submission.get("status") != PENDING:
        return False

    if reviewed_at is None:
        reviewed_at = current_timestamp()

    submission["status"] = REJECTED
    submission["reviewed_at"] = reviewed_at
    submission["review_note"] = note.strip()
    return True
