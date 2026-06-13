"""Plain model classes for Opportunity Radar MVP-1."""


class Opportunity:
    """Store one student opportunity from the curated seed data."""

    def __init__(self, opp_id, title, opp_type, interests, eligible_levels,
                 cost, beginner_friendly, deadline, url, organizer):
        """Create an opportunity with all fields required by the MVP."""
        self.id = opp_id
        self.title = title
        self.type = opp_type
        self.interests = list(interests)
        self.eligible_levels = list(eligible_levels)
        self.cost = cost
        self.beginner_friendly = beginner_friendly
        self.deadline = deadline
        self.url = url
        self.organizer = organizer

    def to_dict(self):
        """Return this opportunity as a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "interests": list(self.interests),
            "eligible_levels": list(self.eligible_levels),
            "cost": self.cost,
            "beginner_friendly": self.beginner_friendly,
            "deadline": self.deadline,
            "url": self.url,
            "organizer": self.organizer,
        }


class Student:
    """Store the student's matching profile for the current CLI session."""

    def __init__(self, name, level, interests):
        """Create a student profile with name, level, and interests."""
        self.name = name
        self.level = level
        self.interests = list(interests)

    def to_dict(self):
        """Return this student profile as a JSON-friendly dictionary."""
        return {
            "name": self.name,
            "level": self.level,
            "interests": list(self.interests),
        }


class Application:
    """Store one application tracker entry."""

    def __init__(self, opp_id, status, notes):
        """Create an application tracker entry with status and notes."""
        self.opp_id = opp_id
        self.status = status
        self.notes = notes

    def to_dict(self):
        """Return this application entry as a JSON-friendly dictionary."""
        return {
            "opp_id": self.opp_id,
            "status": self.status,
            "notes": self.notes,
        }
