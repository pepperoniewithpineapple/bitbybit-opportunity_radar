import json
from pathlib import Path
from datetime import datetime

from models import Opportunity, Student, Application


OPPORTUNITIES_PATH = "data/" + "opportunities.json"
STUDENT_PATH = "data/" + "student.json"
APPLICATIONS_PATH = "data/" + "applications.json"
SEARCHES_PATH = "data/" + "searches.json"
SUBMISSIONS_PATH = "data/" + "submissions.json"


def load_opportunities() -> list[Opportunity]:
    with open(OPPORTUNITIES_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Opportunity(**item) for item in data]
        except json.JSONDecodeError:
            return []


def save_opportunities(opportunities: list[Opportunity]) -> None:
    with open(OPPORTUNITIES_PATH, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in opportunities], f, indent=4, ensure_ascii=False)


def load_student() -> Student | None:
    with open(STUDENT_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return Student(**data) if data else None
        except json.JSONDecodeError:
            return None


def save_student(student: Student) -> None:
    with open(STUDENT_PATH, "w", encoding="utf-8") as f:
        json.dump(student.__dict__, f, indent=4, ensure_ascii=False)


def load_applications() -> list[Application]:
    with open(APPLICATIONS_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Application(**item) for item in data]
        except json.JSONDecodeError:
            return []


def save_applications(apps: list[Application]) -> None:
    with open(APPLICATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump([item.__dict__ for item in apps], f, indent=4, ensure_ascii=False)


def load_submissions() -> list[dict]:
    if not SUBMISSIONS_PATH.exists():
        return []
    with open(SUBMISSIONS_PATH, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return []


def add_submission(submission: dict) -> None:
    data = load_submissions()
    data.append(submission)
    with open(SUBMISSIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_last_updated_timestamp() -> float:
    with open(".last_pulled_timestamp", "r", encoding="utf-8") as f:
        return float(f.read() or 0)


def save_last_updated_timestamp() -> None:
    with open(".last_pulled_timestamp", "w") as f:
        f.write(str(datetime.now().timestamp()))