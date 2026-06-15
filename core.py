import datetime as dt
from pathlib import Path

import storage
import intelligence
import utils
from models import Opportunity, Student, Application


DIGEST_PATH = storage.ROOT / "weekly_digest.txt"


def score_opportunity(opportunity: Opportunity, student: Student | None) -> dict:
    """
    Combines match logic matrix with status checks into uniform layout outputs.

    Args:
        opportunity (Opportunity)
        student (Student | None)

    Returns:
        dict: {
            "opportunity": Opportunity,
            "score": float,
            "eligible": bool,
            "reason": str
        }
    """
    if not student:
        return {"opportunity": opportunity, "score": 0.0, "eligible": True, "reason": "No student profile"}
        
    eligible = utils.is_open_to(opportunity.eligible_levels, student.level)
    match_score = intelligence.calculate_match_score(opportunity, student)
    
    reason = "Matches your profile interests" if match_score > 0.4 else "Alternative opportunity option"
    if not eligible:
        reason = f"Requires level: {', '.join(opportunity.eligible_levels)}"
        
    return {
        "opportunity": opportunity,
        "score": match_score,
        "eligible": eligible,
        "reason": reason
    }


#  >>?????????
def generate_weekly_digest(student: Student, opportunities: list[Opportunity]) -> Path:
    """Builds and writes a personalized text-digest summary report file."""
    lines = [f"WEEKLY DIGEST FOR {student.name.upper()}", f"Generated: {dt.date.today()}", ""]
    
    scored_items = []
    for opp in opportunities:
        res = score_opportunity(opp, student)
        if res["eligible"]:
            scored_items.append(res)
            
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    
    for item in scored_items[:5]:
        opp = item["opportunity"]
        lines.extend([
            f"- {opp.title} ({opp.type.upper()})",
            f"  Match Fit: {int(item['score']*100)}% | Deadline: {opp.deadline}",
            f"  Link: {opp.url}", ""
        ])
        
    DIGEST_PATH.write_text("\n".join(lines), encoding="utf-8")
    return DIGEST_PATH


#  TO DELETE
def export_calendar_ics(opportunities: list[Opportunity]) -> Path:
    """Creates individual calendar data events inside a structural iCalendar payload."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//OpportunityRadar//Scheduler//EN"]
    
    for opp in opportunities:
        if not opp.deadline or "-" not in opp.deadline:
            continue
        clean_date = opp.deadline.replace("-", "")
        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTAMP:{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{clean_date}",
            f"SUMMARY:Deadline: {opp.title}",
            f"DESCRIPTION:Apply here: {opp.url}",
            "END:VEVENT"
        ])
    lines.append("END:VCALENDAR")
    CALENDAR_PATH.write_text("\n".join(lines), encoding="utf-8")
    return CALENDAR_PATH