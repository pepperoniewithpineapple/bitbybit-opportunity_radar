"""Core data and product logic for Opportunity Radar."""

from __future__ import annotations

import datetime as dt
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OPPORTUNITIES_PATH = DATA_DIR / "opportunities.json"
INTERESTS_PATH = DATA_DIR / "interests.json"
STUDENT_PATH = DATA_DIR / "student.json"
SEARCHES_PATH = DATA_DIR / "searches.json"
APPLICATIONS_PATH = DATA_DIR / "applications.json"
SUBMISSIONS_PATH = DATA_DIR / "submissions.json"
DIGEST_PATH = ROOT / "weekly_digest.txt"
CALENDAR_PATH = ROOT / "calendar_export.ics"
ANNOUNCEMENT_PATH = ROOT / "opportunity_sender_packet.txt"

LEVELS = ["Secondary", "JC", "Poly", "University"]
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


@dataclass
class Opportunity:
    id: str
    title: str
    type: str
    interests: list[str]
    eligible_levels: list[str]
    cost: str
    beginner_friendly: bool
    deadline: str
    url: str
    organizer: str


@dataclass
class Student:
    name: str
    level: str
    interests: list[str]


@dataclass
class Application:
    opp_id: str
    status: str
    notes: str = ""


def load_json(path: Path, default):
    """Load JSON, returning default when missing or invalid."""
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError, json.JSONDecodeError):
        return default


def save_json(path: Path, data) -> None:
    """Save JSON atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    os.replace(temp_path, path)


def parse_interests(text: str) -> list[str]:
    """Split comma-separated interest tags."""
    return [piece.strip() for piece in text.split(",") if piece.strip()]


def normalize(value: str) -> str:
    return value.strip().lower()


def load_opportunities() -> list[Opportunity]:
    records = load_json(OPPORTUNITIES_PATH, [])
    opportunities: list[Opportunity] = []
    for record in records:
        try:
            opportunities.append(Opportunity(**record))
        except TypeError:
            continue
    return opportunities


def save_opportunities(opportunities: list[Opportunity]) -> None:
    save_json(OPPORTUNITIES_PATH, [asdict(opportunity) for opportunity in opportunities])


def load_student() -> Student | None:
    record = load_json(STUDENT_PATH, None)
    if not isinstance(record, dict):
        return None
    try:
        return Student(record["name"], record["level"], list(record["interests"]))
    except (KeyError, TypeError):
        return None


def save_student(student: Student) -> None:
    save_json(STUDENT_PATH, asdict(student))


def demo_student() -> Student:
    return Student("Wei Ming", "JC", ["coding", "AI", "cybersecurity"])


def load_applications() -> list[Application]:
    records = load_json(APPLICATIONS_PATH, [])
    applications: list[Application] = []
    for record in records:
        try:
            applications.append(
                Application(record["opp_id"], record["status"], record.get("notes", ""))
            )
        except (KeyError, TypeError):
            continue
    return applications


def save_applications(applications: list[Application]) -> None:
    save_json(APPLICATIONS_PATH, [asdict(application) for application in applications])


def load_submissions() -> list[dict]:
    records = load_json(SUBMISSIONS_PATH, [])
    if not isinstance(records, list):
        return []
    return records


def save_submissions(submissions: list[dict]) -> None:
    save_json(SUBMISSIONS_PATH, submissions)


def opportunity_from_record(record: dict) -> Opportunity:
    return Opportunity(**record)


def opportunity_to_record(opportunity: Opportunity) -> dict:
    return asdict(opportunity)


def today() -> dt.date:
    return dt.date.today()


def parse_date(value: str) -> dt.date:
    return dt.datetime.strptime(value, "%Y-%m-%d").date()


def days_until(deadline: str, base: dt.date | None = None) -> int:
    if base is None:
        base = today()
    return (parse_date(deadline) - base).days


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def is_open_to(opportunity: Opportunity, student: Student) -> bool:
    return student.level in opportunity.eligible_levels and days_until(opportunity.deadline) >= 0


def shared_interests(student: Student, opportunity: Opportunity) -> list[str]:
    student_keys = {normalize(interest) for interest in student.interests}
    return [
        interest
        for interest in opportunity.interests
        if normalize(interest) in student_keys
    ]


def score_opportunity(opportunity: Opportunity, student: Student) -> dict:
    """Score one opportunity with transparent components."""
    shared = shared_interests(student, opportunity)
    days_left = days_until(opportunity.deadline)
    interest_score = len(shared) / max(1, len(student.interests)) * 0.5
    urgency_score = (1 - clamp(days_left / 60, 0, 1)) * 0.2
    access_score = (0.10 if opportunity.cost == "free" else 0) + (
        0.05 if opportunity.beginner_friendly else 0
    )
    total = interest_score + urgency_score + access_score
    return {
        "opportunity": opportunity,
        "score": total,
        "shared": shared,
        "days_left": days_left,
        "breakdown": {
            "interest_score": interest_score,
            "urgency_score": urgency_score,
            "access_score": access_score,
            "total": total,
        },
    }


def rank_opportunities(
    opportunities: list[Opportunity],
    student: Student,
    cost: str = "all",
    opp_type: str = "all",
    keyword: str = "",
    max_days: int | None = None,
    sort: str = "score",
) -> list[dict]:
    """Return eligible scored opportunities with filters."""
    results = []
    for opportunity in opportunities:
        if not is_open_to(opportunity, student):
            continue
        if cost != "all" and opportunity.cost != cost:
            continue
        if opp_type != "all" and opportunity.type != opp_type:
            continue
        if keyword and normalize(keyword) not in normalize(opportunity.title):
            continue
        if max_days is not None and days_until(opportunity.deadline) > max_days:
            continue
        results.append(score_opportunity(opportunity, student))

    if sort == "deadline":
        results.sort(key=lambda result: result["opportunity"].deadline)
    elif sort == "title":
        results.sort(key=lambda result: result["opportunity"].title)
    else:
        results.sort(key=lambda result: result["score"], reverse=True)
    return results


def closing_this_week(opportunities: list[Opportunity], student: Student) -> list[Opportunity]:
    return [
        opportunity
        for opportunity in opportunities
        if is_open_to(opportunity, student) and days_until(opportunity.deadline) <= 7
    ]


def load_interest_tree() -> dict:
    tree = load_json(INTERESTS_PATH, {})
    return tree if isinstance(tree, dict) else {}


def expand_interest(tree: dict, name: str) -> list[str]:
    if name in tree:
        children = tree[name]
        if not children:
            return [name]
        result: list[str] = []
        for child in children:
            result.extend(expand_interest(children, child))
        return result
    for child, subtree in tree.items():
        if subtree:
            found = expand_interest(subtree, name)
            if found:
                return found
    return []


def expanded_interests(raw_interests: list[str]) -> list[str]:
    tree = load_interest_tree()
    seen: set[str] = set()
    expanded: list[str] = []
    for interest in raw_interests:
        leaves = expand_interest(tree, interest.strip()) or [interest.strip()]
        for leaf in leaves:
            key = normalize(leaf)
            if key not in seen:
                seen.add(key)
                expanded.append(leaf)
    return expanded


def log_search(student: Student) -> None:
    records = load_json(SEARCHES_PATH, [])
    if not isinstance(records, list):
        records = []
    records.append(
        {
            "level": student.level,
            "interests": [normalize(interest) for interest in student.interests],
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        }
    )
    save_json(SEARCHES_PATH, records)


def demand_counts() -> dict[str, int]:
    records = load_json(SEARCHES_PATH, [])
    counts: dict[str, int] = {}
    for record in records if isinstance(records, list) else []:
        for interest in record.get("interests", []):
            key = normalize(interest)
            counts[key] = counts.get(key, 0) + 1
    return counts


def supply_counts(opportunities: list[Opportunity]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for opportunity in opportunities:
        if days_until(opportunity.deadline) < 0:
            continue
        for interest in opportunity.interests:
            key = normalize(interest)
            counts[key] = counts.get(key, 0) + 1
    return counts


def gap_rows(opportunities: list[Opportunity], limit: int = 8) -> list[dict]:
    demand = demand_counts()
    supply = supply_counts(opportunities)
    interests = set(demand) | set(supply)
    rows = [
        {
            "interest": interest,
            "demand": demand.get(interest, 0),
            "supply": supply.get(interest, 0),
            "gap": demand.get(interest, 0) - supply.get(interest, 0),
        }
        for interest in interests
    ]
    rows.sort(key=lambda row: (row["gap"], row["demand"]), reverse=True)
    return rows[:limit]


def opportunity_stats(opportunities: list[Opportunity], student: Student | None = None) -> dict:
    open_opps = [opportunity for opportunity in opportunities if days_until(opportunity.deadline) >= 0]
    free = sum(1 for opportunity in open_opps if opportunity.cost == "free")
    paid = len(open_opps) - free
    urgent = sum(1 for opportunity in open_opps if days_until(opportunity.deadline) < 7)
    soon = sum(1 for opportunity in open_opps if 7 <= days_until(opportunity.deadline) <= 30)
    supply = supply_counts(opportunities)
    missing: list[tuple[str, int]] = []
    if student:
        for interest in student.interests:
            missing.append((interest, supply.get(normalize(interest), 0)))
    return {
        "open": len(open_opps),
        "free": free,
        "paid": paid,
        "urgent": urgent,
        "soon": soon,
        "supply": sorted(supply.items(), key=lambda item: item[1], reverse=True)[:8],
        "missing": missing,
    }


def suggest_interests(opportunities: list[Opportunity], student: Student) -> list[tuple[str, int]]:
    current = {normalize(interest) for interest in student.interests}
    suggestions: dict[str, int] = {}
    for opportunity in opportunities:
        if student.level not in opportunity.eligible_levels or days_until(opportunity.deadline) < 0:
            continue
        if shared_interests(student, opportunity):
            continue
        for interest in opportunity.interests:
            key = normalize(interest)
            if key not in current:
                suggestions[interest] = suggestions.get(interest, 0) + 1
    return sorted(suggestions.items(), key=lambda item: item[1], reverse=True)[:3]


def add_application(applications: list[Application], opportunity: Opportunity) -> bool:
    if any(application.opp_id == opportunity.id for application in applications):
        return False
    applications.append(Application(opportunity.id, "interested", ""))
    save_applications(applications)
    return True


def update_application(applications: list[Application], opp_id: str, status: str, notes: str) -> None:
    for application in applications:
        if application.opp_id == opp_id:
            application.status = status
            application.notes = notes
            save_applications(applications)
            return


def remove_application(applications: list[Application], opp_id: str) -> None:
    applications[:] = [application for application in applications if application.opp_id != opp_id]
    save_applications(applications)


def next_opportunity_id(opportunities: list[Opportunity]) -> str:
    highest = 0
    for opportunity in opportunities:
        if opportunity.id.startswith("opp-") and opportunity.id[4:].isdigit():
            highest = max(highest, int(opportunity.id[4:]))
    return "opp-" + str(highest + 1).zfill(3)


def next_submission_id(submissions: list[dict]) -> str:
    highest = 0
    for submission in submissions:
        value = submission.get("submission_id", "")
        if value.startswith("sub-") and value[4:].isdigit():
            highest = max(highest, int(value[4:]))
    return "sub-" + str(highest + 1).zfill(3)


def title_exists(opportunities: list[Opportunity], title: str) -> bool:
    target = normalize(title)
    return any(normalize(opportunity.title) == target for opportunity in opportunities)


def submission_opportunity(submission: dict) -> Opportunity:
    return opportunity_from_record(submission["opportunity"])


def create_submission(submissions: list[dict], opportunity: Opportunity) -> dict:
    submission = {
        "submission_id": next_submission_id(submissions),
        "status": "pending",
        "submitted_at": dt.datetime.now().isoformat(timespec="seconds"),
        "reviewed_at": "",
        "review_note": "",
        "opportunity": opportunity_to_record(opportunity),
    }
    submissions.append(submission)
    save_submissions(submissions)
    return submission


def pending_submissions(submissions: list[dict]) -> list[dict]:
    return [submission for submission in submissions if submission.get("status") == "pending"]


def status_counts(submissions: list[dict]) -> dict[str, int]:
    counts = {"pending": 0, "approved": 0, "rejected": 0}
    for submission in submissions:
        status = submission.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def submission_preview(opportunity: Opportunity, opportunities: list[Opportunity]) -> dict:
    demand = demand_counts()
    matches = sum(demand.get(normalize(interest), 0) for interest in set(opportunity.interests))
    access = 40
    access += 25 if opportunity.cost == "free" else 0
    access += 20 if opportunity.beginner_friendly else 0
    access += 10 if len(opportunity.eligible_levels) >= 3 else 0
    access += 5 if opportunity.type in ("workshop", "volunteering", "programme") else 0
    return {
        "duplicate": title_exists(opportunities, opportunity.title),
        "demand_matches": matches,
        "days_left": days_until(opportunity.deadline),
        "access_score": int(clamp(access, 0, 100)),
    }


def approve_submission(submissions: list[dict], opportunities: list[Opportunity], submission_id: str) -> bool:
    for submission in submissions:
        if submission.get("submission_id") != submission_id or submission.get("status") != "pending":
            continue
        opportunity = submission_opportunity(submission)
        if title_exists(opportunities, opportunity.title):
            return False
        opportunity.id = next_opportunity_id(opportunities)
        opportunities.append(opportunity)
        submission["status"] = "approved"
        submission["reviewed_at"] = dt.datetime.now().isoformat(timespec="seconds")
        submission["review_note"] = "Approved through review queue."
        save_opportunities(opportunities)
        save_submissions(submissions)
        return True
    return False


def reject_submission(submissions: list[dict], submission_id: str, note: str) -> bool:
    for submission in submissions:
        if submission.get("submission_id") == submission_id and submission.get("status") == "pending":
            submission["status"] = "rejected"
            submission["reviewed_at"] = dt.datetime.now().isoformat(timespec="seconds")
            submission["review_note"] = note.strip()
            save_submissions(submissions)
            return True
    return False


def announcement_text(opportunity: Opportunity) -> str:
    return "\n".join(
        [
            "OPPORTUNITY RADAR - New Opportunity",
            "",
            opportunity.title,
            "Organizer: " + opportunity.organizer,
            "Type: " + opportunity.type,
            "Deadline: " + opportunity.deadline,
            "Cost: " + opportunity.cost,
            "Open to: " + ", ".join(opportunity.eligible_levels),
            "Interests: " + ", ".join(opportunity.interests),
            "Beginner-friendly: " + ("yes" if opportunity.beginner_friendly else "no"),
            "Link: " + opportunity.url,
            "",
            "Sent through Opportunity Radar.",
        ]
    )


def save_announcement(opportunity: Opportunity) -> Path:
    ANNOUNCEMENT_PATH.write_text(announcement_text(opportunity), encoding="utf-8")
    return ANNOUNCEMENT_PATH


def weekly_digest(results: list[dict], student: Student) -> Path:
    lines = [
        "Opportunity Radar Weekly Digest",
        "For: " + student.name,
        "",
    ]
    for index, result in enumerate(results[:8], 1):
        opportunity = result["opportunity"]
        lines.extend(
            [
                f"{index}. {opportunity.title}",
                f"   {opportunity.organizer} | {opportunity.deadline} | score {result['score']:.3f}",
                f"   {opportunity.url}",
            ]
        )
    DIGEST_PATH.write_text("\n".join(lines), encoding="utf-8")
    return DIGEST_PATH


def export_calendar(applications: list[Application], opportunities: list[Opportunity]) -> Path:
    by_id = {opportunity.id: opportunity for opportunity in opportunities}
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Opportunity Radar//EN",
    ]
    for application in applications:
        opportunity = by_id.get(application.opp_id)
        if not opportunity:
            continue
        date = opportunity.deadline.replace("-", "")
        lines.extend(
            [
                "BEGIN:VEVENT",
                "UID:" + opportunity.id + "@opportunity-radar",
                "DTSTAMP:" + dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
                "DTSTART;VALUE=DATE:" + date,
                "SUMMARY:" + opportunity.title,
                "DESCRIPTION:" + opportunity.url,
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    CALENDAR_PATH.write_text("\n".join(lines), encoding="utf-8")
    return CALENDAR_PATH


def first_timer_guides() -> dict[str, list[str]]:
    return {
        "hackathon": [
            "Expect a short build sprint, usually in teams.",
            "Prepare one simple idea and a clear demo.",
            "Judges usually value clarity more than complexity.",
        ],
        "competition": [
            "Read judging criteria before starting.",
            "Track deadlines and submission formats early.",
            "Ask organizers what a strong entry looks like.",
        ],
        "scholarship": [
            "Prepare achievements, reflection, and financial/context details.",
            "Explain why the opportunity changes your path.",
            "Ask a teacher or mentor for feedback before submitting.",
        ],
        "workshop": [
            "Bring questions and take notes.",
            "Follow up with the organizer or speaker.",
            "Use the workshop to decide whether to go deeper.",
        ],
        "olympiad": [
            "Practise past problems.",
            "Learn the scoring format.",
            "Expect challenge; improvement matters.",
        ],
    }
