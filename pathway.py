"""Career pathway planning with a prerequisite graph."""

from graphlib import CycleError
from graphlib import TopologicalSorter

import career_model
import matcher


STAGE_DEPENDENCIES = {
    "foundation": set(),
    "practice": {"foundation"},
    "proof": {"practice"},
    "launch": {"proof"},
}

STAGE_LABELS = {
    "foundation": "Foundation",
    "practice": "Practice",
    "proof": "Proof",
    "launch": "Launch",
}

STAGE_TYPES = {
    "foundation": ["workshop", "programme", "volunteering"],
    "practice": ["competition", "hackathon", "olympiad"],
    "proof": ["research", "internship"],
    "launch": ["scholarship", "programme", "internship"],
}


def ordered_stages(stage_dependencies=None):
    """Return pathway stages in prerequisite-safe order."""
    if stage_dependencies is None:
        stage_dependencies = STAGE_DEPENDENCIES

    try:
        sorter = TopologicalSorter(stage_dependencies)
        return list(sorter.static_order())
    except CycleError as error:
        raise ValueError("career pathway stages contain a cycle") from error


def normalized_set(values):
    """Return normalized labels as a set."""
    result = set()
    for value in values:
        result.add(career_model.normalize(value))
    return result


def missing_skills(career_name, student):
    """Return career-required skills the student has not shown yet."""
    student_skills = normalized_set(student.interests)
    missing = []

    for skill, weight in career_model.CAREER_PATHS[career_name].items():
        if career_model.normalize(skill) not in student_skills:
            missing.append({
                "skill": skill,
                "weight": weight,
            })

    missing.sort(key=lambda item: item["weight"], reverse=True)
    return missing


def stage_type_match(stage, opportunity):
    """Return True when the opportunity type fits a pathway stage."""
    return opportunity.type in STAGE_TYPES[stage]


def stage_score(career_name, student, stage, opportunity):
    """Return a score for placing an opportunity in one pathway stage."""
    relevance = career_model.opportunity_relevance(career_name, opportunity)
    score = relevance

    if stage_type_match(stage, opportunity):
        score = score + 0.35
    if stage == "foundation" and opportunity.beginner_friendly:
        score = score + 0.18
    if stage == "launch" and opportunity.type in ("scholarship", "internship"):
        score = score + 0.15
    if opportunity.cost == "free":
        score = score + 0.05
    if student.level in opportunity.eligible_levels:
        score = score + 0.05

    return score


def choose_stage_opportunity(career_name, student, opportunities, stage,
                             used_ids, today=None):
    """Return the best unused opportunity for one pathway stage."""
    candidates = []

    for opportunity in opportunities:
        if opportunity.id in used_ids:
            continue
        if not matcher.is_eligible_and_open(opportunity, student, today):
            continue

        score = stage_score(career_name, student, stage, opportunity)
        if score <= 0.05:
            continue

        candidates.append({
            "opportunity": opportunity,
            "score": score,
            "relevance": career_model.opportunity_relevance(career_name, opportunity),
        })

    candidates.sort(key=lambda item: item["score"], reverse=True)
    if len(candidates) == 0:
        return None
    return candidates[0]


def stage_reason(career_name, stage, item):
    """Return a concise explanation for a pathway stage recommendation."""
    if item is None:
        return "No eligible live opportunity fits this stage yet."

    opportunity = item["opportunity"]
    reasons = []

    if stage_type_match(stage, opportunity):
        reasons.append("stage type match: " + opportunity.type)

    matching = []
    for interest in opportunity.interests:
        if career_model.get_skill_weight(career_name, interest) > 0:
            matching.append(interest)

    if len(matching) > 0:
        reasons.append("career skills: " + ", ".join(matching))

    if opportunity.beginner_friendly:
        reasons.append("beginner-friendly")

    if opportunity.cost == "free":
        reasons.append("free")

    return "; ".join(reasons)


def build_pathway(career_name, student, opportunities, today=None):
    """Build a multi-step career pathway for a student."""
    used_ids = set()
    steps = []

    for stage in ordered_stages():
        item = choose_stage_opportunity(
            career_name,
            student,
            opportunities,
            stage,
            used_ids,
            today,
        )

        if item is not None:
            used_ids.add(item["opportunity"].id)

        steps.append({
            "stage": stage,
            "stage_label": STAGE_LABELS[stage],
            "target_types": list(STAGE_TYPES[stage]),
            "opportunity": None if item is None else item["opportunity"],
            "score": 0.0 if item is None else item["score"],
            "reason": stage_reason(career_name, stage, item),
        })

    return {
        "career": career_name,
        "missing_skills": missing_skills(career_name, student),
        "steps": steps,
        "starting_score": career_model.readiness_score(
            career_name,
            student.interests,
        ),
    }
