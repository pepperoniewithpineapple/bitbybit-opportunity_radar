import json
import os
from pathlib import Path
from datetime import datetime

from models import Opportunity, Student, Application


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OPPORTUNITIES_PATH = DATA_DIR / "opportunities.json"
STUDENT_PATH = DATA_DIR / "student.json"
APPLICATIONS_PATH = DATA_DIR / "applications.json"
SEARCHES_PATH = DATA_DIR / "searches.json"
SUBMISSIONS_PATH = DATA_DIR / "submissions.json"


def _ensure_data_dir():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_opportunities() -> list[Opportunity]:
    if not OPPORTUNITIES_PATH.exists():
        return []
    with open(OPPORTUNITIES_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Opportunity(**item) for item in data]
        except json.JSONDecodeError:
            return []


def save_opportunities(opportunities: list[Opportunity]) -> None:
    _ensure_data_dir()
    with open(OPPORTUNITIES_PATH, "w", encoding="utf-8") as f:
        json.dump([item.__dict__ for item in opportunities], f, indent=4, ensure_ascii=False)


def load_student() -> Student | None:
    if not STUDENT_PATH.exists():
        return None
    with open(STUDENT_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return Student(**data) if data else None
        except json.JSONDecodeError:
            return None


def save_student(student: Student) -> None:
    _ensure_data_dir()
    with open(STUDENT_PATH, "w", encoding="utf-8") as f:
        json.dump(student.__dict__, f, indent=4, ensure_ascii=False)


def load_applications() -> list[Application]:
    if not APPLICATIONS_PATH.exists():
        return []
    with open(APPLICATIONS_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Application(**item) for item in data]
        except json.JSONDecodeError:
            return []


def save_applications(apps: list[Application]) -> None:
    _ensure_data_dir()
    with open(APPLICATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump([item.__dict__ for item in apps], f, indent=4, ensure_ascii=False)


def log_search(query: str, filters: dict) -> None:
    _ensure_data_dir()
    data = []
    if SEARCHES_PATH.exists():
        with open(SEARCHES_PATH, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except json.JSONDecodeError: pass
    data.append({"query": query, "filters": filters})
    with open(SEARCHES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_submissions() -> list[dict]:
    if not SUBMISSIONS_PATH.exists():
        return []
    with open(SUBMISSIONS_PATH, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return []


def add_submission(submission: dict) -> None:
    _ensure_data_dir()
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