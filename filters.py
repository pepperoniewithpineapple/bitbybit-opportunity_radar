"""Pure filtering and sorting helpers for ranked opportunity results."""


def filter_by_type(results, opp_type):
    """Return results whose opportunity type exactly matches opp_type."""
    filtered = []

    for result in results:
        opportunity = result["opportunity"]
        if opportunity.type == opp_type:
            filtered.append(result)

    return filtered


def filter_by_keyword(results, keyword):
    """Return results whose opportunity title contains keyword, ignoring case."""
    filtered = []
    lowered_keyword = keyword.strip().lower()

    if lowered_keyword == "":
        return list(results)

    for result in results:
        opportunity = result["opportunity"]
        if lowered_keyword in opportunity.title.lower():
            filtered.append(result)

    return filtered


def filter_by_deadline_window(results, max_days):
    """Return results whose deadline is no more than max_days away."""
    filtered = []

    for result in results:
        days_left = result["breakdown"]["days_left"]
        if days_left <= max_days:
            filtered.append(result)

    return filtered


def sort_results(results, key):
    """Sort ranked results by score, deadline, or title.

    The supported keys are "score", "deadline", and "title". Unknown keys
    fall back to score sorting, with the highest total score first.
    """
    if key == "deadline":
        return sorted(results, key=lambda result: result["breakdown"]["days_left"])

    if key == "title":
        return sorted(
            results,
            key=lambda result: result["opportunity"].title.lower(),
        )

    return sorted(
        results,
        key=lambda result: result["breakdown"]["total"],
        reverse=True,
    )
