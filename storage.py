import json
from datetime import datetime

from models import Opportunity, Student, AppliedOpportunity, PortfolioItem, OpportunityID


OPPORTUNITIES_PATH = "data/" + "opportunities.json"
STUDENT_PATH = "data/" + "student.json"
MY_OPPORTUNITIES_PATH = "data/" + "my_opportunities.json"
SEARCHES_PATH = "data/" + "searches.json"
SUBMISSIONS_PATH = "data/" + "submissions.json"


def load_opportunities() -> list[Opportunity]:
    with open(OPPORTUNITIES_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [Opportunity(id=k, **v) for k, v in data.items()]
        except json.JSONDecodeError:
            return []


def save_opportunities(opportunities: list[Opportunity]) -> None:
    with open(OPPORTUNITIES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                opp.id: {
                    "title": opp.title,
                    "type": opp.type,
                    "interests": opp.interests,
                    "eligible_levels": opp.eligible_levels,
                    "beginner_friendly": opp.beginner_friendly,
                    "deadline": opp.deadline,
                    "url": opp.url,
                    "organiser": opp.organiser
                }
                for opp in opportunities
            }, 
            f, indent=4, ensure_ascii=False
        )


def load_student() -> Student | None:
    with open(STUDENT_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not data: return None
            student = Student(**data)
            return student
        except json.JSONDecodeError:
            return None


def save_student(student: Student) -> None:
    with open(STUDENT_PATH, "w", encoding="utf-8") as f:
        json.dump(student.__dict__, f, indent=4, ensure_ascii=False)


def load_my_opportunities() -> list[AppliedOpportunity]:
    with open(MY_OPPORTUNITIES_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [AppliedOpportunity(id=k, **v) for k, v in data.items()]
        except json.JSONDecodeError:
            return []


def save_my_opportunities(apps: list[AppliedOpportunity]) -> None:
    with open(MY_OPPORTUNITIES_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                app.id: {
                    "title": app.title,
                    "type": app.type,
                    "interests": app.interests,
                    "eligible_levels": app.eligible_levels,
                    "beginner_friendly": app.beginner_friendly,
                    "deadline": app.deadline,
                    "url": app.url,
                    "organiser": app.organiser,
                    "status": app.status,
                    "notes": app.notes
                }
                for app in apps
            }, 
            f, indent=4, ensure_ascii=False
        )


def is_applied_opportunity(opp_id: OpportunityID) -> bool:
    with open(MY_OPPORTUNITIES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return opp_id in data


def add_applied_opportunity(opportunity: Opportunity) -> None:
    my_opportunities = load_my_opportunities()
    my_opportunities.append(AppliedOpportunity(**opportunity.to_dict()))
    save_my_opportunities(my_opportunities)


def remove_applied_opportunity(opportunity_id: OpportunityID) -> None:
    my_opportunities = load_my_opportunities()
    for i, app in enumerate(my_opportunities):
        if app.id == opportunity_id:
            my_opportunities.pop(i)
            break
    save_my_opportunities(my_opportunities)


def set_applied_status(opp_id: OpportunityID, status: str) -> None:
    my_opportunities = load_my_opportunities()
    for i, app in enumerate(my_opportunities):
        if app.id == opp_id:
            app.status = status
            if status in {"rejected", "competed"}:
                my_opportunities.pop(i)
            break
    save_my_opportunities(my_opportunities)


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