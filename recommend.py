"""Interest recommendations that help students unlock more opportunities."""

import interests as interests_module
import matcher
from models import Student


def suggest_interests(opportunities, student, interest_tree, limit=3):
    """Suggest interests you could add to unlock more opportunities.

    The function looks at opportunities the student is eligible for, but that
    do not currently match any of their expanded interests. It then counts the
    new interest tags on those opportunities and returns the most common ones.
    """
    expanded_interests = interests_module.get_expanded_interests(
        interest_tree,
        student.interests,
    )
    matching_student = Student(student.name, student.level, expanded_interests)

    existing = set()
    for interest in student.interests:
        existing.add(matcher.normalize_interest(interest))
    for interest in expanded_interests:
        existing.add(matcher.normalize_interest(interest))

    counts = {}
    labels = {}

    for opportunity in opportunities:
        if not matcher.is_eligible_and_open(opportunity, matching_student, None):
            continue

        shared = matcher.find_shared_interests(matching_student, opportunity)
        if len(shared) > 0:
            continue

        for interest in opportunity.interests:
            key = matcher.normalize_interest(interest)
            if key in existing:
                continue
            if key not in labels:
                labels[key] = interest
            counts[key] = counts.get(key, 0) + 1

    ordered = sorted(counts.items(), key=lambda item: (-item[1], labels[item[0]].lower()))
    suggestions = []

    for key, count in ordered[:limit]:
        suggestions.append((labels[key], count))

    return suggestions
