"""Bias self-audit for Opportunity Radar.

This module measures whether our equity weighting actually changes who gets seen.
It answers Dr. Jennifer Eberhardt's challenge with numbers: instead of claiming
the algorithm is fair, we test it. We run the matcher across many synthetic
students twice -- once with the equity boost and once without -- and report how
often free / beginner-friendly opportunities reach a student's top results.
"""

import matcher


def score_without_equity(opportunity, student, today):
    """Re-score an opportunity with the equity boost removed.

    Returns interest_score + urgency_score only, so we can compare a purely
    'neutral' ranking against our access-weighted ranking.
    """
    result = matcher.score_opportunity(opportunity, student, today, use_fuzzy=True)
    breakdown = result["breakdown"]
    neutral_total = breakdown["interest_score"] + breakdown["urgency_score"]
    return neutral_total


def rank_neutral(opportunities, student, today=None):
    """Rank opportunities WITHOUT the equity boost (the 'neutral' baseline)."""
    today_date = matcher.get_today(today)
    scored = []

    for opportunity in opportunities:
        if matcher.is_eligible_and_open(opportunity, student, today_date):
            neutral_total = score_without_equity(opportunity, student, today_date)
            scored.append((opportunity, neutral_total))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [opportunity for opportunity, total in scored]


def rank_with_equity(opportunities, student, today=None):
    """Rank opportunities WITH the equity boost (our actual ranking)."""
    results = matcher.rank_opportunities(opportunities, student, today, use_fuzzy=True)
    return [result["opportunity"] for result in results]


def free_share_in_top(ranked_opportunities, top_n):
    """Return the fraction of the top_n ranked opportunities that are free."""
    top = ranked_opportunities[:top_n]
    if len(top) == 0:
        return 0.0

    free_count = 0
    for opportunity in top:
        if opportunity.cost == "free":
            free_count = free_count + 1

    return free_count / len(top)


def audit(opportunities, sample_students, today=None, top_n=5):
    """Audit the equity weighting across a sample of students.

    Returns a dict with the average share of free opportunities in the top_n,
    both with and without the equity boost, plus the lift the boost provides.
    """
    neutral_shares = []
    equity_shares = []

    for student in sample_students:
        neutral_ranked = rank_neutral(opportunities, student, today)
        equity_ranked = rank_with_equity(opportunities, student, today)

        if len(equity_ranked) == 0:
            continue

        neutral_shares.append(free_share_in_top(neutral_ranked, top_n))
        equity_shares.append(free_share_in_top(equity_ranked, top_n))

    neutral_avg = average(neutral_shares)
    equity_avg = average(equity_shares)

    return {
        "students_tested": len(equity_shares),
        "top_n": top_n,
        "neutral_free_share": neutral_avg,
        "equity_free_share": equity_avg,
        "lift": equity_avg - neutral_avg,
    }


def average(values):
    """Return the mean of a list of numbers, or 0.0 when the list is empty."""
    if len(values) == 0:
        return 0.0
    return sum(values) / len(values)


def build_sample_students(student_class, interest_pool, levels):
    """Build a spread of synthetic students for the audit.

    Each student gets one interest from the pool paired with one level, so the
    audit covers a realistic variety of profiles.
    """
    students = []
    counter = 1

    for level in levels:
        for interest in interest_pool:
            name = "sample-" + str(counter)
            students.append(student_class(name, level, [interest]))
            counter = counter + 1

    return students


def print_audit(opportunities, student_class, today=None):
    """Run the audit on a built-in sample and print a readable report."""
    interest_pool = [
        "coding", "AI", "cybersecurity", "design", "entrepreneurship",
        "research", "robotics", "data science", "math", "public good",
    ]
    levels = ["Secondary", "JC", "Poly", "University"]
    sample = build_sample_students(student_class, interest_pool, levels)

    report = audit(opportunities, sample, today)

    print("")
    print("Bias Self-Audit  (does our equity weighting actually change outcomes?)")
    print("=" * 68)
    print("Synthetic students tested: " + str(report["students_tested"]))
    print("Measuring: share of FREE opportunities in each student's top "
          + str(report["top_n"]))
    print("")
    print("  Without equity weighting (neutral): "
          + format(report["neutral_free_share"] * 100, ".1f") + "%")
    print("  With our equity weighting:          "
          + format(report["equity_free_share"] * 100, ".1f") + "%")
    print("  Access lift from our design:        "
          + format(report["lift"] * 100, ".1f") + " percentage points")
    print("")

    if report["lift"] > 0:
        print("Result: our weighting measurably widens access to free opportunities.")
    else:
        print("Result: no measurable lift on this dataset -- worth investigating.")

    print("We do not claim neutrality. We claim a measured, intentional lift.")
    return report
