"""JSON storage helpers for Opportunity Radar MVP-1."""

import json
import os

from models import Application
from models import Opportunity
from models import Student


def load_json(path):
    """Load JSON data from path and return the decoded value."""
    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def save_json(path, data):
    """Save data as readable JSON, creating the parent folder if needed."""
    folder = os.path.dirname(path)
    if folder != "" and not os.path.exists(folder):
        os.makedirs(folder)

    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)


def load_opportunities(path):
    """Load opportunity records from JSON and return Opportunity objects.

    Returns an empty list (with a message) if the file is missing or corrupt
    so the app never crashes on startup.
    """
    if not os.path.exists(path):
        print("Notice: opportunities file not found at " + path + ". Using empty list.")
        return []

    try:
        records = load_json(path)
    except (json.JSONDecodeError, ValueError):
        print("Notice: opportunities file could not be read. Using empty list.")
        return []

    opportunities = []

    for record in records:
        opportunity = Opportunity(
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
        opportunities.append(opportunity)

    return opportunities


def load_applications(path):
    """Load application records from JSON and return Application objects."""
    if not os.path.exists(path):
        return []

    records = load_json(path)
    applications = []

    for record in records:
        application = Application(
            record["opp_id"],
            record["status"],
            record["notes"],
        )
        applications.append(application)

    return applications


def save_applications(path, applications):
    """Save Application objects to JSON at path."""
    records = []

    for application in applications:
        records.append(application.to_dict())

    save_json(path, records)


def load_student(path):
    """Load one Student profile from JSON, returning None when unavailable."""
    if not os.path.exists(path):
        return None

    try:
        record = load_json(path)
        return Student(
            record["name"],
            record["level"],
            record["interests"],
        )
    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        print("Notice: student profile could not be read. Starting without a profile.")
        return None


def save_student(path, student):
    """Save one Student profile to JSON at path."""
    save_json(path, student.to_dict())


def save_opportunities(path, opportunities):
    """Save Opportunity objects back to JSON at path."""
    records = []

    for opportunity in opportunities:
        records.append(opportunity.to_dict())

    save_json(path, records)


def next_opportunity_id(opportunities):
    """Return a fresh unique opportunity id like 'opp-021' based on existing ids."""
    highest = 0

    for opportunity in opportunities:
        opp_id = opportunity.id
        if opp_id.startswith("opp-"):
            number_part = opp_id[len("opp-"):]
            if number_part.isdigit():
                value = int(number_part)
                if value > highest:
                    highest = value

    return "opp-" + str(highest + 1).zfill(3)
