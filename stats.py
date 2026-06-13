"""Opportunity-gap statistics for Opportunity Radar."""

import matcher
import ui


def supply_by_interest(opportunities):
    """Count open opportunities per interest tag and return a dict of {interest: count}."""
    counts = {}

    for opp in opportunities:
        days_left = matcher.days_until(opp.deadline)
        if days_left < 0:
            continue
        for interest in opp.interests:
            key = interest.strip().lower()
            if key in counts:
                counts[key] = counts[key] + 1
            else:
                counts[key] = 1

    return counts


def free_vs_paid_ratio(opportunities):
    """Return counts and percentages of free vs paid open opportunities."""
    free_count = 0
    paid_count = 0

    for opp in opportunities:
        days_left = matcher.days_until(opp.deadline)
        if days_left < 0:
            continue
        if opp.cost == "free":
            free_count = free_count + 1
        else:
            paid_count = paid_count + 1

    total = free_count + paid_count

    if total == 0:
        return {"free": 0, "paid": 0, "free_pct": 0, "paid_pct": 0, "total": 0}

    return {
        "free": free_count,
        "paid": paid_count,
        "free_pct": round(free_count / total * 100),
        "paid_pct": round(paid_count / total * 100),
        "total": total,
    }


def deadline_pressure(opportunities):
    """Count open opportunities bucketed by urgency: <7 days, 7-30 days, 30+ days."""
    urgent = 0
    soon = 0
    later = 0

    for opp in opportunities:
        days_left = matcher.days_until(opp.deadline)
        if days_left < 0:
            continue
        if days_left < 7:
            urgent = urgent + 1
        elif days_left <= 30:
            soon = soon + 1
        else:
            later = later + 1

    return {"urgent": urgent, "soon": soon, "later": later}


def unmet_interests(student_interests, supply_counts, threshold=1):
    """Return interests from the student profile with fewer than threshold matching opportunities.

    These are the 'empty radar' rows — interests the student cares about but
    where the supply is too thin. They visualise the opportunity gap directly.
    """
    unmet = []

    for interest in student_interests:
        key = interest.strip().lower()
        count = supply_counts.get(key, 0)
        if count < threshold:
            unmet.append((interest, count))

    return unmet


def print_stats(opportunities, student=None):
    """Print the opportunity-gap stats view to the terminal."""
    supply = supply_by_interest(opportunities)
    ratio = free_vs_paid_ratio(opportunities)
    pressure = deadline_pressure(opportunities)

    print("")
    print("Opportunity Gap Statistics")
    print("=" * 40)
    print("")
    print("Open opportunities:  " + str(ratio["total"]))
    print("  Free:  " + str(ratio["free"]) + " (" + str(ratio["free_pct"]) + "%)")
    print("  Paid:  " + str(ratio["paid"]) + " (" + str(ratio["paid_pct"]) + "%)")
    print("")
    print("Deadline pressure:")
    ui.bar_chart([
        ("Urgent <7 days", pressure["urgent"]),
        ("Soon 7-30 days", pressure["soon"]),
        ("Later 30+ days", pressure["later"]),
    ])
    print("")
    print("Supply by interest (top 8 most-covered):")

    sorted_interests = sorted(supply.items(), key=lambda item: item[1], reverse=True)
    ui.bar_chart(sorted_interests, max_bars=8)

    if student is not None:
        print("")
        print("Your interests vs supply - the opportunity gap:")
        print("-" * 40)
        unmet = unmet_interests(student.interests, supply)

        if len(unmet) == 0:
            print("  All your interests have at least one matching opportunity.")
        else:
            for interest, count in unmet:
                if count == 0:
                    print("  " + interest + ":  NO opportunities found  <-- gap here")
                else:
                    print("  " + interest + ":  only " + str(count) + " found  <-- thin supply")

        print("")
        print("This near-empty list IS the data.")
        print("It shows where the opportunity gap actually is.")
