"""Calendar export helpers for Opportunity Radar MVP-2."""

import datetime
import os

import tracker


def escape_ics_text(value):
    """Escape text for safe use in an RFC-5545 text value."""
    text = value.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def fold_ics_line(line):
    """Fold one ICS content line to the RFC-5545 recommended length."""
    if len(line) <= 75:
        return [line]

    lines = []
    remaining = line
    first_line = True

    while len(remaining) > 75:
        if first_line:
            limit = 75
            first_line = False
        else:
            limit = 74

        lines.append(remaining[:limit])
        remaining = " " + remaining[limit:]

    lines.append(remaining)
    return lines


def append_ics_line(lines, line):
    """Append a folded ICS line to lines."""
    folded_lines = fold_ics_line(line)

    for folded_line in folded_lines:
        lines.append(folded_line)


def format_date_for_ics(date_text):
    """Convert a YYYY-MM-DD date string into an ICS DATE value."""
    date_value = datetime.datetime.strptime(date_text, "%Y-%m-%d").date()
    return date_value.strftime("%Y%m%d")


def get_next_date_for_ics(date_text):
    """Return the day after date_text as an ICS DATE value."""
    date_value = datetime.datetime.strptime(date_text, "%Y-%m-%d").date()
    next_date = date_value + datetime.timedelta(days=1)
    return next_date.strftime("%Y%m%d")


def get_timestamp():
    """Return the current UTC timestamp for DTSTAMP."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y%m%dT%H%M%SZ")


def build_event_lines(application, opportunity, timestamp):
    """Return ICS lines for one tracked opportunity deadline event."""
    lines = []
    description = opportunity.organizer + "\\n" + opportunity.url

    append_ics_line(lines, "BEGIN:VEVENT")
    append_ics_line(
        lines,
        "UID:" + escape_ics_text(application.opp_id)
        + "-deadline@opportunity-radar",
    )
    append_ics_line(lines, "DTSTAMP:" + timestamp)
    append_ics_line(
        lines,
        "SUMMARY:" + escape_ics_text("Deadline: " + opportunity.title),
    )
    append_ics_line(
        lines,
        "DTSTART;VALUE=DATE:" + format_date_for_ics(opportunity.deadline),
    )
    append_ics_line(
        lines,
        "DTEND;VALUE=DATE:" + get_next_date_for_ics(opportunity.deadline),
    )
    append_ics_line(lines, "DESCRIPTION:" + escape_ics_text(description))
    append_ics_line(lines, "END:VEVENT")

    return lines


def generate_ics_text(applications, opportunities):
    """Generate RFC-5545 calendar text for tracked application deadlines."""
    lines = []
    timestamp = get_timestamp()

    append_ics_line(lines, "BEGIN:VCALENDAR")
    append_ics_line(lines, "VERSION:2.0")
    append_ics_line(lines, "PRODID:-//Opportunity Radar//MVP-2//EN")
    append_ics_line(lines, "CALSCALE:GREGORIAN")

    for application in applications:
        opportunity = tracker.find_opportunity_by_id(
            opportunities,
            application.opp_id,
        )
        if opportunity is not None:
            event_lines = build_event_lines(application, opportunity, timestamp)
            for event_line in event_lines:
                lines.append(event_line)

    append_ics_line(lines, "END:VCALENDAR")

    return "\r\n".join(lines) + "\r\n"


def export_applications_to_ics(applications, opportunities, path):
    """Write tracked application deadlines to an ICS file and return its path."""
    absolute_path = os.path.abspath(path)
    ics_text = generate_ics_text(applications, opportunities)

    with open(absolute_path, "w", encoding="utf-8", newline="") as file_handle:
        file_handle.write(ics_text)

    return absolute_path
