"""Career readiness impact model for Opportunity Radar.

This is a small, transparent "ML-style" model. It uses weighted skill vectors
and a sigmoid curve to estimate career-readiness alignment before and after a
student joins a specific opportunity.

It does NOT predict real hiring probability. It estimates whether an event is
likely to increase, decrease, or leave unchanged the student's alignment with a
chosen career direction.
"""

import math

import matcher


CAREER_PATHS = {
    "software engineer": {
        "coding": 3.0,
        "algorithms": 2.4,
        "web development": 2.0,
        "AI": 1.3,
        "data science": 1.0,
        "problem solving": 2.0,
        "engineering": 1.2,
    },
    "cybersecurity analyst": {
        "cybersecurity": 3.0,
        "coding": 2.0,
        "problem solving": 1.8,
        "defence tech": 1.6,
        "algorithms": 1.2,
        "AI": 0.8,
    },
    "data analyst": {
        "data science": 3.0,
        "AI": 2.0,
        "coding": 1.7,
        "math": 1.6,
        "research": 1.3,
        "business": 1.2,
        "public good": 0.8,
    },
    "research scientist": {
        "research": 3.0,
        "science": 2.4,
        "math": 1.8,
        "presentation": 1.2,
        "AI": 1.0,
        "biotech": 1.8,
        "engineering": 1.2,
    },
    "startup founder": {
        "entrepreneurship": 3.0,
        "business": 2.4,
        "marketing": 1.7,
        "public good": 1.4,
        "social impact": 1.4,
        "coding": 1.1,
        "design": 1.0,
    },
    "product designer": {
        "design": 3.0,
        "UI/UX": 2.4,
        "graphic design": 1.6,
        "public good": 1.0,
        "entrepreneurship": 0.9,
        "coding": 0.8,
        "presentation": 1.1,
    },
}


TYPE_MULTIPLIERS = {
    "internship": 1.35,
    "research": 1.25,
    "competition": 1.20,
    "hackathon": 1.15,
    "olympiad": 1.10,
    "workshop": 1.00,
    "programme": 1.00,
    "scholarship": 0.95,
    "volunteering": 0.90,
}


def career_names():
    """Return supported career names sorted for stable menus."""
    return sorted(CAREER_PATHS.keys())


def normalize(value):
    """Normalize a skill label for matching."""
    return value.strip().lower()


def get_skill_weight(career_name, skill):
    """Return the career weight for skill, case-insensitively."""
    weights = CAREER_PATHS[career_name]
    wanted = normalize(skill)

    for label, weight in weights.items():
        if normalize(label) == wanted:
            return weight

    return 0.0


def weighted_skill_coverage(career_name, skills):
    """Return 0..1 weighted coverage of career-required skills."""
    weights = CAREER_PATHS[career_name]
    total_weight = sum(weights.values())
    covered = 0.0
    seen = set()

    for skill in skills:
        key = normalize(skill)
        if key in seen:
            continue
        seen.add(key)
        covered = covered + get_skill_weight(career_name, skill)

    if total_weight == 0:
        return 0.0

    return matcher.clamp(covered / total_weight, 0.0, 1.0)


def sigmoid(value):
    """Return a sigmoid transform for a model-like readiness curve."""
    return 1 / (1 + math.exp(-value))


def readiness_score(career_name, student_skills, evidence_strength=0.0):
    """Return a 0..100 career-readiness alignment score.

    The score uses weighted skill coverage and a small evidence_strength term
    for concrete experiences. The sigmoid curve makes early gains visible while
    avoiding fake precision at the extremes.
    """
    coverage = weighted_skill_coverage(career_name, student_skills)
    raw = (coverage * 4.2) + evidence_strength - 2.1
    return sigmoid(raw) * 100


def opportunity_relevance(career_name, opportunity):
    """Return 0..1 relevance of an opportunity to a career path."""
    return weighted_skill_coverage(career_name, opportunity.interests)


def opportunity_evidence_gain(career_name, opportunity):
    """Return model evidence gained by joining opportunity."""
    relevance = opportunity_relevance(career_name, opportunity)
    multiplier = TYPE_MULTIPLIERS.get(opportunity.type, 0.95)
    gain = relevance * multiplier * 0.25

    if opportunity.beginner_friendly:
        gain = gain + 0.03

    return matcher.clamp(gain, 0.0, 0.35)


def opportunity_cost_penalty(career_name, opportunity):
    """Return a small penalty for low-relevance opportunities.

    This models short-term attention cost, not moral value. An opportunity can
    be good in general but still slightly pull focus away from a chosen career.
    """
    relevance = opportunity_relevance(career_name, opportunity)

    if relevance >= 0.12:
        return 0.0

    penalty = 0.08
    if opportunity.cost == "paid":
        penalty = penalty + 0.05
    if not opportunity.beginner_friendly:
        penalty = penalty + 0.04

    return penalty


def merge_skills(existing_skills, opportunity):
    """Return student skills plus opportunity interest tags, deduplicated."""
    seen = set()
    merged = []

    for skill in list(existing_skills) + list(opportunity.interests):
        key = normalize(skill)
        if key not in seen:
            seen.add(key)
            merged.append(skill)

    return merged


def classify_delta(delta):
    """Classify the readiness-score change."""
    if delta >= 1.0:
        return "INCREASE"
    if delta <= -1.0:
        return "DECREASE"
    return "NO CHANGE"


def impact_reasons(career_name, opportunity, relevance, gain, penalty):
    """Return explanation strings for an opportunity's career impact."""
    reasons = []

    matching = []
    for interest in opportunity.interests:
        if get_skill_weight(career_name, interest) > 0:
            matching.append(interest)

    if len(matching) > 0:
        reasons.append("career-relevant skills: " + ", ".join(matching))
    else:
        reasons.append("no direct skill match for this career path")

    reasons.append("event type multiplier: " + opportunity.type)

    if opportunity.beginner_friendly:
        reasons.append("beginner-friendly experience adds usable evidence")

    if penalty > 0:
        reasons.append("low relevance creates a small attention-cost penalty")

    reasons.append("relevance score: " + format(relevance, ".2f"))
    reasons.append("experience gain: " + format(gain, ".2f"))

    return reasons


def evaluate_opportunity(career_name, student, opportunity):
    """Return before/after career-readiness impact for one opportunity."""
    before = readiness_score(career_name, student.interests)
    relevance = opportunity_relevance(career_name, opportunity)
    gain = opportunity_evidence_gain(career_name, opportunity)
    penalty = opportunity_cost_penalty(career_name, opportunity)
    after_skills = merge_skills(student.interests, opportunity)
    after = readiness_score(career_name, after_skills, gain - penalty)
    delta = after - before

    return {
        "career": career_name,
        "opportunity": opportunity,
        "before": before,
        "after": after,
        "delta": delta,
        "classification": classify_delta(delta),
        "relevance": relevance,
        "gain": gain,
        "penalty": penalty,
        "reasons": impact_reasons(career_name, opportunity, relevance, gain, penalty),
    }


def rank_impacts(career_name, student, opportunities, limit=5):
    """Return opportunities sorted by strongest positive career impact."""
    impacts = []

    for opportunity in opportunities:
        impacts.append(evaluate_opportunity(career_name, student, opportunity))

    impacts.sort(key=lambda impact: impact["delta"], reverse=True)
    return impacts[:limit]
