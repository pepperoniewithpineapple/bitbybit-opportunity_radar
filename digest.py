"""Weekly digest generator for Opportunity Radar."""

import datetime
import os


def generate_digest(results, student, path):
    """Generate a plain-text weekly digest of top matches and write it to path.

    The digest is formatted to be pasted into a class group chat.
    Returns the absolute path of the written file.
    """
    today = datetime.date.today().isoformat()
    lines = []

    lines.append("=" * 55)
    lines.append("OPPORTUNITY RADAR — Weekly Digest")
    lines.append("Generated: " + today)

    if student is not None:
        lines.append("For: " + student.name + " (" + student.level + ")")

    lines.append("=" * 55)
    lines.append("")

    top_results = results[:5]

    if len(top_results) == 0:
        lines.append("No matching opportunities found this week.")
    else:
        for rank_number, result in enumerate(top_results):
            opp = result["opportunity"]
            breakdown = result["breakdown"]
            days_left = breakdown["days_left"]

            if days_left < 7:
                urgency_tag = "  ⚠ CLOSING SOON"
            else:
                urgency_tag = ""

            lines.append(str(rank_number + 1) + ". " + opp.title + urgency_tag)
            lines.append("   Organizer: " + opp.organizer)
            lines.append("   Deadline:  " + opp.deadline + " (" + str(days_left) + " days)")
            lines.append("   Cost:      " + opp.cost.capitalize())
            lines.append("   Why:       " + result["reasons"][0])
            lines.append("   Link:      " + opp.url)
            lines.append("")

    lines.append("-" * 55)
    lines.append("Shared from Opportunity Radar — free for all students.")
    lines.append("Run it yourself: python main.py")
    lines.append("-" * 55)

    content = "\n".join(lines)

    with open(path, "w", encoding="utf-8") as file_handle:
        file_handle.write(content)

    return os.path.abspath(path)
