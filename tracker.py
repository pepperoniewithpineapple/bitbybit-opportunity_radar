"""Application tracker helpers for Opportunity Radar MVP-2."""

import matcher
import validation
from models import Application


STATUSES = ["interested", "applied", "accepted", "rejected"]


def find_opportunity_by_id(opportunities, opp_id):
    """Return the opportunity with opp_id, or None when it is missing."""
    for opportunity in opportunities:
        if opportunity.id == opp_id:
            return opportunity

    return None


def find_application_by_opp_id(applications, opp_id):
    """Return the tracked application for opp_id, or None when missing."""
    for application in applications:
        if application.opp_id == opp_id:
            return application

    return None


def add_application(applications, opportunity, status="interested", notes=""):
    """Add opportunity to the tracker and return True when it was added."""
    existing = find_application_by_opp_id(applications, opportunity.id)
    if existing is not None:
        return False

    application = Application(opportunity.id, status, notes)
    applications.append(application)
    return True


def update_application_status(applications, opp_id, status):
    """Update one tracked application's status and return True on success."""
    if status not in STATUSES:
        return False

    application = find_application_by_opp_id(applications, opp_id)
    if application is None:
        return False

    application.status = status
    return True


def update_application_notes(applications, opp_id, notes):
    """Update one tracked application's notes and return True on success."""
    application = find_application_by_opp_id(applications, opp_id)
    if application is None:
        return False

    application.notes = notes
    return True


def remove_application(applications, opp_id):
    """Remove one tracked application and return True when it was removed."""
    index = 0
    while index < len(applications):
        if applications[index].opp_id == opp_id:
            del applications[index]
            return True
        index = index + 1

    return False


def get_deadline_countdown(opportunity, today=None):
    """Return a readable deadline countdown badge for one opportunity."""
    days_left = matcher.days_until(opportunity.deadline, today)

    if days_left < 0:
        return "EXPIRED"

    if days_left == 1:
        text = "1 day left"
    else:
        text = str(days_left) + " days left"

    if days_left < 7:
        text = text + " [WARNING]"

    return text


def print_status_options():
    """Print the valid application statuses."""
    print("Statuses: " + ", ".join(STATUSES))


def ask_status():
    """Ask for a valid application status using the validation gateway."""
    print_status_options()
    return validation.get_valid_choice("Status: ", STATUSES)


def list_applications(applications, opportunities, today=None):
    """Print all tracked applications with deadline countdowns."""
    if len(applications) == 0:
        print("No tracked applications yet.")
        return

    print("")
    print("Application tracker")
    index = 1
    for application in applications:
        opportunity = find_opportunity_by_id(opportunities, application.opp_id)
        print("")
        if opportunity is None:
            print(str(index) + ". Missing opportunity: " + application.opp_id)
            print("   Status: " + application.status)
            print("   Notes: " + application.notes)
        else:
            countdown = get_deadline_countdown(opportunity, today)
            print(str(index) + ". " + opportunity.title)
            print("   Organizer: " + opportunity.organizer)
            print("   Deadline: " + opportunity.deadline + " | " + countdown)
            print("   Status: " + application.status)
            print("   Notes: " + application.notes)
        index = index + 1


def choose_application(applications, opportunities, prompt):
    """Ask the user to choose a tracked application and return it."""
    if len(applications) == 0:
        print("No tracked applications yet.")
        return None

    list_applications(applications, opportunities)
    choice = validation.get_valid_int(prompt, 1, len(applications))
    return applications[choice - 1]


def add_from_feed(applications, results):
    """Add one ranked feed result to the application tracker."""
    if len(results) == 0:
        print("View the For You feed first, then add a result here.")
        return False

    print("")
    print("Choose a feed result to track:")
    index = 1
    for result in results:
        opportunity = result["opportunity"]
        print(str(index) + ". " + opportunity.title)
        index = index + 1

    choice = validation.get_valid_int(
        "Choose a result number from 1 to " + str(len(results)) + ": ",
        1,
        len(results),
    )
    status = ask_status()
    opportunity = results[choice - 1]["opportunity"]
    added = add_application(applications, opportunity, status, "")

    if added:
        print("Added to tracker: " + opportunity.title)
    else:
        print("Already tracked: " + opportunity.title)

    return added


def update_status_flow(applications, opportunities):
    """Run the CLI flow for changing one tracked application's status."""
    application = choose_application(
        applications,
        opportunities,
        "Choose an application number to update: ",
    )
    if application is None:
        return False

    status = ask_status()
    updated = update_application_status(applications, application.opp_id, status)
    if updated:
        print("Status updated.")
    return updated


def update_notes_flow(applications, opportunities):
    """Run the CLI flow for editing one tracked application's note."""
    application = choose_application(
        applications,
        opportunities,
        "Choose an application number for notes: ",
    )
    if application is None:
        return False

    notes = validation.nonempty("Note: ")
    updated = update_application_notes(applications, application.opp_id, notes)
    if updated:
        print("Note saved.")
    return updated


def remove_application_flow(applications, opportunities):
    """Run the CLI flow for removing one tracked application."""
    application = choose_application(
        applications,
        opportunities,
        "Choose an application number to remove: ",
    )
    if application is None:
        return False

    removed = remove_application(applications, application.opp_id)
    if removed:
        print("Removed from tracker.")
    return removed
