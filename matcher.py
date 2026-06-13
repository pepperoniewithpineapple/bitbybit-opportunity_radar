"""Scoring, ranking, and explanation logic for Opportunity Radar."""

import datetime
import difflib


CHECK = "[OK]"
WARN = "[WARN]"

FUZZY_THRESHOLD = 0.82


def clamp(value, lo, hi):
    """Return value limited to the inclusive range from lo to hi."""
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def parse_deadline(deadline_text):
    """Convert a YYYY-MM-DD deadline string into a date object."""
    return datetime.datetime.strptime(deadline_text, "%Y-%m-%d").date()


def get_today(today):
    """Return today as a date object, using the real date when today is None."""
    if today is None:
        return datetime.date.today()
    if isinstance(today, datetime.date):
        return today
    return parse_deadline(today)


def days_until(deadline_text, today=None):
    """Return the number of days from today until the deadline date."""
    today_date = get_today(today)
    deadline_date = parse_deadline(deadline_text)
    return (deadline_date - today_date).days


def normalize_interest(value):
    """Normalize one interest name for fair case-insensitive matching."""
    return value.strip().lower()


def interest_similarity(first, second):
    """Return a 0..1 similarity ratio between two interest names."""
    return difflib.SequenceMatcher(None, first, second).ratio()


def find_shared_interests(student, opportunity, use_fuzzy=False):
    """Return opportunity interest names that also appear in the student profile.

    When use_fuzzy is True, near-matches (e.g. 'ML' vs 'machine learning',
    or small typos) also count, using difflib similarity above FUZZY_THRESHOLD.
    Exact matching is the default so scoring stays predictable for tests.
    """
    student_normalized = []
    for interest in student.interests:
        student_normalized.append(normalize_interest(interest))

    student_interest_set = set(student_normalized)

    shared = []
    for interest in opportunity.interests:
        normalized = normalize_interest(interest)

        if normalized in student_interest_set:
            shared.append(interest)
            continue

        if use_fuzzy:
            for student_interest in student_normalized:
                if interest_similarity(normalized, student_interest) >= FUZZY_THRESHOLD:
                    shared.append(interest)
                    break

    return shared


def build_reasons(opportunity, student, shared_interests, days_left):
    """Build human-readable reason strings for one scored opportunity."""
    reasons = []

    if len(shared_interests) > 0:
        reasons.append(
            CHECK + " Interests matched: " + ", ".join(shared_interests)
            + " (" + str(len(shared_interests)) + " shared)"
        )
    else:
        reasons.append(WARN + " Interests matched: none yet (0 shared)")

    reasons.append(CHECK + " Eligible: open to " + student.level)
    reasons.append(WARN + " Deadline: closes in " + str(days_left) + " days")

    if opportunity.cost == "free":
        reasons.append(CHECK + " Free opportunity (+0.10 access weight)")
    else:
        reasons.append(WARN + " Paid opportunity (+0.00 access weight)")

    if opportunity.beginner_friendly:
        reasons.append(CHECK + " Beginner friendly (+0.05 access weight)")
    else:
        reasons.append(WARN + " Not marked beginner friendly (+0.00 access weight)")

    return reasons


def score_opportunity(opportunity, student, today, use_fuzzy=False):
    """Score one opportunity and return a result dictionary with explanations."""
    today_date = get_today(today)
    days_left = days_until(opportunity.deadline, today_date)
    shared_interests = find_shared_interests(student, opportunity, use_fuzzy)

    shared_count = len(shared_interests)
    interest_count = max(1, len(student.interests))
    interest_score = shared_count / interest_count * 0.5
    urgency_score = (1 - clamp(days_left / 60, 0, 1)) * 0.2

    equity_boost = 0
    if opportunity.cost == "free":
        equity_boost = equity_boost + 0.10
    if opportunity.beginner_friendly:
        equity_boost = equity_boost + 0.05

    total = interest_score + urgency_score + equity_boost
    reasons = build_reasons(opportunity, student, shared_interests, days_left)

    return {
        "opportunity": opportunity,
        "score": total,
        "reasons": reasons,
        "breakdown": {
            "shared_interests": shared_interests,
            "shared_count": shared_count,
            "student_interest_count": len(student.interests),
            "interest_score": interest_score,
            "days_left": days_left,
            "urgency_score": urgency_score,
            "equity_boost": equity_boost,
            "total": total,
        },
    }


def is_eligible_and_open(opportunity, student, today):
    """Return True when level eligibility passes and the deadline is not expired."""
    today_date = get_today(today)
    days_left = days_until(opportunity.deadline, today_date)

    if student.level not in opportunity.eligible_levels:
        return False
    if days_left < 0:
        return False
    return True


def rank_opportunities(opportunities, student, today=None, use_fuzzy=False):
    """Return scored opportunities after hard filters, sorted by total descending."""
    today_date = get_today(today)
    results = []

    for opportunity in opportunities:
        if is_eligible_and_open(opportunity, student, today_date):
            result = score_opportunity(opportunity, student, today_date, use_fuzzy)
            results.append(result)

    return sorted(results, key=lambda result: result["score"], reverse=True)


def closing_this_week(opportunities, student, today=None):
    """Return eligible open opportunities closing within 7 days, soonest first."""
    today_date = get_today(today)
    urgent = []

    for opportunity in opportunities:
        if not is_eligible_and_open(opportunity, student, today_date):
            continue

        days_left = days_until(opportunity.deadline, today_date)
        if days_left <= 7:
            urgent.append(opportunity)

    return sorted(
        urgent,
        key=lambda opportunity: days_until(opportunity.deadline, today_date),
    )


def print_result_summary(result, rank_number):
    """Print one compact ranked feed item with its explanation reasons."""
    opportunity = result["opportunity"]
    print("")
    print(str(rank_number) + ". " + opportunity.title)
    print("   Organizer: " + opportunity.organizer)
    print("   Type: " + opportunity.type + " | Deadline: " + opportunity.deadline)
    print("   Score: " + format(result["score"], ".3f"))

    for reason in result["reasons"]:
        print("   " + reason)


def print_scoring_breakdown(result):
    """Print the transparent scoring breakdown for one ranked result."""
    opportunity = result["opportunity"]
    breakdown = result["breakdown"]

    print("")
    print("Scoring breakdown: " + opportunity.title)
    print("Organizer: " + opportunity.organizer)
    print("URL: " + opportunity.url)
    print("")
    print("interest_score = shared_interests / max(1, student_interests) * 0.5")
    print(
        "interest_score = "
        + str(breakdown["shared_count"])
        + " / max(1, "
        + str(breakdown["student_interest_count"])
        + ") * 0.5 = "
        + format(breakdown["interest_score"], ".3f")
    )
    print("")
    print("urgency_score = (1 - clamp(days_left / 60, 0, 1)) * 0.2")
    print(
        "urgency_score = (1 - clamp("
        + str(breakdown["days_left"])
        + " / 60, 0, 1)) * 0.2 = "
        + format(breakdown["urgency_score"], ".3f")
    )
    print("")
    print("equity_boost = free boost + beginner-friendly boost")
    print("equity_boost = " + format(breakdown["equity_boost"], ".3f"))
    print("total = " + format(breakdown["total"], ".3f"))
    print("")

    for reason in result["reasons"]:
        print(reason)
