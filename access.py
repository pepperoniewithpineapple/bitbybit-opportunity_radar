"""Invisible starting-line simulation for Opportunity Radar.

The matcher already answers: "Which opportunities fit this student?"
This module answers the more surprising question: "Would the student ever
hear about those opportunities without a tool like this?"

The simulation is intentionally transparent. It does not use school, income,
race, grades, or any protected/student-background field. It only models
information-network access: how likely an opportunity is to reach a student
before they actively search for it.
"""

import matcher
import ui


PERSONAS = [
    {
        "key": "quiet",
        "label": "Outside usual networks",
        "base": 0.16,
        "interest_bonus": 0.12,
        "free_bonus": 0.08,
        "beginner_bonus": 0.10,
        "paid_penalty": 0.15,
        "advanced_penalty": 0.10,
        "specialist_penalty": 0.08,
        "short_deadline_penalty": 0.07,
    },
    {
        "key": "average",
        "label": "Average school channels",
        "base": 0.38,
        "interest_bonus": 0.14,
        "free_bonus": 0.08,
        "beginner_bonus": 0.08,
        "paid_penalty": 0.08,
        "advanced_penalty": 0.06,
        "specialist_penalty": 0.04,
        "short_deadline_penalty": 0.04,
    },
    {
        "key": "plugged",
        "label": "Plugged-in network",
        "base": 0.70,
        "interest_bonus": 0.12,
        "free_bonus": 0.04,
        "beginner_bonus": 0.04,
        "paid_penalty": 0.02,
        "advanced_penalty": 0.02,
        "specialist_penalty": 0.00,
        "short_deadline_penalty": 0.01,
    },
]

SPECIALIST_TYPES = ["olympiad", "scholarship"]


def get_persona(persona_key):
    """Return the persona dict for persona_key, falling back to the first persona."""
    for persona in PERSONAS:
        if persona["key"] == persona_key:
            return persona
    return PERSONAS[0]


def awareness_probability(opportunity, student, persona_key, today=None):
    """Estimate the chance that a student hears about an opportunity before Radar.

    The score is not a moral judgement about the student. It is an explicit
    model of information flow. Free, beginner-friendly, interest-aligned items
    are easier to hear about; paid, specialist, and short-deadline items are
    easier to miss unless the student already has strong channels.
    """
    persona = get_persona(persona_key)
    today_date = matcher.get_today(today)

    if not matcher.is_eligible_and_open(opportunity, student, today_date):
        return 0.0

    shared = matcher.find_shared_interests(student, opportunity, use_fuzzy=True)
    days_left = matcher.days_until(opportunity.deadline, today_date)

    probability = persona["base"]

    if len(shared) > 0:
        probability = probability + persona["interest_bonus"]

    if opportunity.cost == "free":
        probability = probability + persona["free_bonus"]
    else:
        probability = probability - persona["paid_penalty"]

    if opportunity.beginner_friendly:
        probability = probability + persona["beginner_bonus"]
    else:
        probability = probability - persona["advanced_penalty"]

    if opportunity.type in SPECIALIST_TYPES:
        probability = probability - persona["specialist_penalty"]

    if days_left <= 7:
        probability = probability - persona["short_deadline_penalty"]

    return matcher.clamp(probability, 0.03, 0.98)


def build_access_report(opportunities, student, today=None):
    """Build a full access report for one student across all network personas."""
    today_date = matcher.get_today(today)
    rows = []

    for opportunity in opportunities:
        if matcher.is_eligible_and_open(opportunity, student, today_date):
            scored = matcher.score_opportunity(
                opportunity,
                student,
                today_date,
                use_fuzzy=True,
            )
            probabilities = {}
            for persona in PERSONAS:
                probabilities[persona["key"]] = awareness_probability(
                    opportunity,
                    student,
                    persona["key"],
                    today_date,
                )

            rows.append({
                "opportunity": opportunity,
                "score": scored["score"],
                "breakdown": scored["breakdown"],
                "reasons": scored["reasons"],
                "probabilities": probabilities,
            })

    rows.sort(key=lambda row: row["score"], reverse=True)
    eligible_count = len(rows)
    persona_summaries = []

    for persona in PERSONAS:
        key = persona["key"]
        expected_before = 0.0
        likely_visible = 0

        for row in rows:
            probability = row["probabilities"][key]
            expected_before = expected_before + probability
            if probability >= 0.50:
                likely_visible = likely_visible + 1

        persona_summaries.append({
            "key": key,
            "label": persona["label"],
            "expected_before": expected_before,
            "likely_visible": likely_visible,
            "after_radar": eligible_count,
            "recovered": eligible_count - expected_before,
        })

    return {
        "student": student,
        "eligible_count": eligible_count,
        "rows": rows,
        "personas": persona_summaries,
    }


def friction_reasons(row):
    """Return short reasons why an otherwise good opportunity may stay hidden."""
    opportunity = row["opportunity"]
    reasons = []

    if opportunity.cost == "paid":
        reasons.append("paid")
    if not opportunity.beginner_friendly:
        reasons.append("not beginner-marked")
    if opportunity.type in SPECIALIST_TYPES:
        reasons.append("specialist channel")
    if row["breakdown"]["days_left"] <= 7:
        reasons.append("short deadline")

    if len(reasons) == 0:
        reasons.append("no direct channel")

    return ", ".join(reasons)


def find_hidden_high_fit(report, persona_key="quiet", limit=5):
    """Return high-scoring opportunities that a persona is likely to miss."""
    hidden = []

    for row in report["rows"]:
        probability = row["probabilities"][persona_key]
        if probability < 0.50:
            hidden.append(row)

    hidden.sort(key=lambda row: (row["score"], -row["probabilities"][persona_key]), reverse=True)
    return hidden[:limit]


def format_probability(value):
    """Format a probability as a whole-number percentage string."""
    return str(int(round(value * 100))) + "%"


def print_starting_line_simulation(opportunities, student, today=None):
    """Print the invisible starting-line simulation for one student."""
    report = build_access_report(opportunities, student, today)

    print("")
    ui.header("Invisible Starting-Line Simulation")
    print("")
    print("Same student. Same ability. Different information network.")
    print("Opportunity Radar changes what the student can SEE, not who they are.")
    print("")
    print("The model uses only opportunity fields: cost, type, beginner label,")
    print("deadline pressure, eligibility, and interest match.")
    print("")

    headers = ["Information network", "Before Radar", "After Radar", "Recovered"]
    rows = []

    for summary in report["personas"]:
        rows.append([
            summary["label"],
            format(summary["expected_before"], ".1f")
            + " of "
            + str(summary["after_radar"]),
            str(summary["after_radar"]),
            "+" + format(summary["recovered"], ".1f"),
        ])

    ui.print_table(headers, rows)

    print("")
    print("Recovered opportunity gap:")
    chart_pairs = []
    for summary in report["personas"]:
        chart_pairs.append((summary["label"], round(summary["recovered"], 1)))
    ui.bar_chart(chart_pairs, max_bars=3, width=26)

    hidden = find_hidden_high_fit(report, "quiet")

    print("")
    print("Best-fit opportunities an outside-network student may miss:")
    if len(hidden) == 0:
        print("  None in this profile. The access gap is low for this student.")
        return report

    hidden_rows = []
    for row in hidden:
        opportunity = row["opportunity"]
        hidden_rows.append([
            opportunity.title[:38] + ("..." if len(opportunity.title) > 38 else ""),
            opportunity.type,
            format(row["score"], ".3f"),
            format_probability(row["probabilities"]["quiet"]),
            friction_reasons(row),
        ])

    ui.print_table(
        ["Opportunity", "Type", "Match", "Heard before", "Why hidden"],
        hidden_rows,
    )

    print("")
    print("Pitch line: the gap is not talent. The gap is who hears in time.")
    return report
