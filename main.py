"""Command-line interface for Opportunity Radar."""

import os
import sys

# Reconfigure stdout to UTF-8 for Windows terminals.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import digest
import fairness
import filters
import firsttimer
import ics_export
import interests as interests_module
import matcher
import recommend
import stats as stats_module
import storage
import tracker
import ui
import validation
from models import Student


LEVELS = ["Secondary", "JC", "Poly", "University"]

DEMO_STUDENT_NAME = "Wei Ming"
DEMO_STUDENT_LEVEL = "JC"
DEMO_STUDENT_INTERESTS = ["coding", "AI", "cybersecurity"]


def build_opportunities_path():
    """Return the path to the curated opportunities JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "opportunities.json")


def build_applications_path():
    """Return the path to the persisted applications JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "applications.json")


def build_student_path():
    """Return the path to the persisted student profile JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "student.json")


def build_interests_path():
    """Return the path to the interest taxonomy JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "interests.json")


def build_calendar_export_path():
    """Return the path to the generated calendar export file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "calendar_export.ics")


def build_digest_path():
    """Return the path to the generated weekly digest text file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "weekly_digest.txt")


def parse_interests(raw_text):
    """Split a comma-separated interest string into a clean list."""
    pieces = raw_text.split(",")
    interests = []

    for piece in pieces:
        interest = piece.strip()
        if interest != "":
            interests.append(interest)

    return interests


def ask_student_profile():
    """Ask the user for a student profile using the validation gateway."""
    print("")
    name = validation.nonempty("Name: ")

    print("")
    print("Levels:")
    index = 1
    for level in LEVELS:
        print(str(index) + ". " + level)
        index = index + 1

    level_number = validation.get_valid_int("Choose level number: ", 1, len(LEVELS))
    level = LEVELS[level_number - 1]

    raw_interests = validation.nonempty(
        "Interests, separated by commas (example: AI, coding, public good): "
    )
    interests = parse_interests(raw_interests)

    while len(interests) == 0:
        print("Please include at least one usable interest.")
        raw_interests = validation.nonempty(
            "Interests, separated by commas (example: AI, coding, public good): "
        )
        interests = parse_interests(raw_interests)

    return Student(name, level, interests)


def print_profile(student):
    """Print the current student profile in one compact block."""
    if student is None:
        print("No profile set yet.")
        return

    print("Profile: " + student.name + " | " + student.level)
    print("Interests: " + ", ".join(student.interests))


def get_ranked_results(opportunities, student, interest_tree, cost_filter="all"):
    """Rank opportunities for a student with optional interest expansion and cost filter.

    Uses the interest taxonomy tree to recursively expand broad interests like
    'Technology' into their leaf interests before matching.
    """
    expanded = interests_module.get_expanded_interests(interest_tree, student.interests)
    matching_student = Student(student.name, student.level, expanded)

    results = matcher.rank_opportunities(opportunities, matching_student)

    if cost_filter == "free":
        results = [r for r in results if r["opportunity"].cost == "free"]

    return results


def apply_cost_filter(results, cost_filter):
    """Return ranked results after applying the selected cost filter."""
    if cost_filter == "free":
        return [result for result in results if result["opportunity"].cost == "free"]
    return list(results)


def get_available_types(results):
    """Return opportunity types present in ranked results, sorted A-Z."""
    seen = set()

    for result in results:
        seen.add(result["opportunity"].type)

    return sorted(seen)


def ask_type_filter(results):
    """Ask the user which opportunity type filter to apply."""
    types = get_available_types(results)

    if len(types) == 0:
        print("No opportunity types available to filter.")
        return "all"

    print("")
    print("Filter by type:")
    print("1. All types")
    number = 2
    for opp_type in types:
        print(str(number) + ". " + opp_type)
        number = number + 1

    choice = validation.get_valid_int("Choose type filter: ", 1, len(types) + 1)
    if choice == 1:
        return "all"
    return types[choice - 2]


def ask_keyword_filter():
    """Ask the user whether to filter feed results by title keyword."""
    print("")
    print("Filter by keyword:")
    print("1. No keyword filter")
    print("2. Enter a title keyword")
    choice = validation.get_valid_int("Choose keyword filter: ", 1, 2)

    if choice == 1:
        return ""
    return validation.nonempty("Keyword in title: ")


def ask_deadline_filter():
    """Ask the user whether to keep only results closing within N days."""
    print("")
    print("Filter by deadline window:")
    print("1. No deadline filter")
    print("2. Closing within N days")
    choice = validation.get_valid_int("Choose deadline filter: ", 1, 2)

    if choice == 1:
        return None
    return validation.get_valid_int("Maximum days left: ", 0, 3650)


def ask_sort_key():
    """Ask the user which sort order to use for feed results."""
    print("")
    print("Sort feed:")
    print("1. Highest score")
    print("2. Soonest deadline")
    print("3. Title A-Z")
    choice = validation.get_valid_int("Choose sort order: ", 1, 3)

    if choice == 2:
        return "deadline"
    if choice == 3:
        return "title"
    return "score"


def apply_feed_options(results, cost_filter, type_filter, keyword, max_days, sort_key):
    """Apply selected cost, type, keyword, deadline, and sort options."""
    filtered = apply_cost_filter(results, cost_filter)

    if type_filter != "all":
        filtered = filters.filter_by_type(filtered, type_filter)

    if keyword != "":
        filtered = filters.filter_by_keyword(filtered, keyword)

    if max_days is not None:
        filtered = filters.filter_by_deadline_window(filtered, max_days)

    return filters.sort_results(filtered, sort_key)


def run_feed_options(results):
    """Run the option 2 filter and sorting submenu, then return final results."""
    cost_filter = "all"
    type_filter = "all"
    keyword = ""
    max_days = None
    sort_key = "score"

    while True:
        print("")
        print("Feed filters and sorting")
        print("1. Cost filter: " + cost_filter)
        print("2. Type filter: " + type_filter)
        print("3. Keyword filter: " + (keyword if keyword != "" else "none"))
        if max_days is None:
            print("4. Deadline filter: none")
        else:
            print("4. Deadline filter: within " + str(max_days) + " days")
        print("5. Sort order: " + sort_key)
        print("0. Show results")

        choice = validation.get_valid_int("Choose feed option: ", 0, 5)

        if choice == 0:
            return apply_feed_options(
                results,
                cost_filter,
                type_filter,
                keyword,
                max_days,
                sort_key,
            )

        if choice == 1:
            cost_filter = ask_cost_filter()
            continue

        if choice == 2:
            type_filter = ask_type_filter(results)
            continue

        if choice == 3:
            keyword = ask_keyword_filter()
            continue

        if choice == 4:
            max_days = ask_deadline_filter()
            continue

        if choice == 5:
            sort_key = ask_sort_key()
            continue


def print_match_tips(opportunities, student, interest_tree):
    """Print interest suggestions that could unlock more eligible opportunities."""
    suggestions = recommend.suggest_interests(opportunities, student, interest_tree)

    for interest, count in suggestions:
        print(
            "Tip: add '"
            + interest
            + "' to your interests to unlock "
            + str(count)
            + " more opportunities."
        )


def show_closing_this_week(opportunities, student):
    """Print eligible opportunities closing within the next 7 days."""
    urgent = matcher.closing_this_week(opportunities, student)

    if len(urgent) == 0:
        print("No eligible opportunities are closing this week.")
        return

    print("")
    ui.header("Closing This Week")
    print("")

    headers = ["#", "Title", "Organizer", "Type", "Deadline", "Days Left"]
    rows = []

    for index, opportunity in enumerate(urgent):
        days_left = matcher.days_until(opportunity.deadline)
        rows.append([
            str(index + 1),
            opportunity.title[:45] + ("..." if len(opportunity.title) > 45 else ""),
            opportunity.organizer,
            opportunity.type,
            opportunity.deadline,
            ui.countdown_badge(days_left),
        ])

    ui.print_table(headers, rows)


def show_feed(results):
    """Print the ranked For You feed using aligned tables and countdown badges."""
    if len(results) == 0:
        print("No open opportunities match your level and filters yet.")
        print("(Tip: try the empty-radar view in Stats to see where the gap is.)")
        return

    print("")
    ui.header("For You - Ranked Opportunities")
    print("")

    headers = ["#", "Title", "Organizer", "Deadline", "Days Left", "Score"]
    rows = []

    for rank_number, result in enumerate(results):
        opp = result["opportunity"]
        breakdown = result["breakdown"]
        days_left = breakdown["days_left"]

        rows.append([
            str(rank_number + 1),
            opp.title[:45] + ("..." if len(opp.title) > 45 else ""),
            opp.organizer,
            opp.deadline,
            ui.countdown_badge(days_left),
            format(result["score"], ".3f"),
        ])

    ui.print_table(headers, rows)

    print("")
    print("Tip: choose option 3 to see the full scoring breakdown for any result.")


def show_menu(student):
    """Print the main menu and current profile status."""
    print("")
    ui.header("Opportunity Radar")
    print_profile(student)
    print("")
    print("1.  Set/edit student profile")
    print("2.  View ranked + explained For You feed")
    print("3.  Show full scoring breakdown (transparency screen)")
    print("4.  Application tracker")
    print("5.  Export tracker deadlines to .ics calendar")
    print("6.  First-timer guide")
    print("7.  Opportunity-gap statistics")
    print("8.  Generate shareable weekly digest")
    print("9.  Load demo student (quick-start for demo)")
    print("10. Bias self-audit (does the equity weighting work?)")
    print("11. Closing this week (urgent deadlines)")
    print("0.  Quit")


def ensure_profile(student):
    """Return True when a profile exists, otherwise explain the missing step."""
    if student is None:
        print("Set your student profile first (option 1 or 9 for demo student).")
        return False
    return True


def choose_breakdown_result(results):
    """Ask the user which result should be opened in the transparency screen."""
    if len(results) == 0:
        print("No ranked results available. View the feed first (option 2).")
        return

    choice = validation.get_valid_int(
        "Choose a result number from 1 to " + str(len(results)) + ": ",
        1,
        len(results),
    )
    matcher.print_scoring_breakdown(results[choice - 1])


def show_tracker_menu():
    """Print the application tracker submenu."""
    print("")
    print("Application tracker")
    print("1. Add a For You feed result")
    print("2. List tracked applications")
    print("3. Update a status")
    print("4. Add or edit a note")
    print("5. Remove an item")
    print("0. Back")


def run_tracker_menu(applications, opportunities, last_results, applications_path):
    """Run the application tracker submenu."""
    while True:
        show_tracker_menu()
        choice = validation.get_valid_int("Choose a tracker option: ", 0, 5)

        if choice == 0:
            return

        if choice == 1:
            changed = tracker.add_from_feed(applications, last_results)
            if changed:
                storage.save_applications(applications_path, applications)
            continue

        if choice == 2:
            tracker.list_applications(applications, opportunities)
            continue

        if choice == 3:
            changed = tracker.update_status_flow(applications, opportunities)
            if changed:
                storage.save_applications(applications_path, applications)
            continue

        if choice == 4:
            changed = tracker.update_notes_flow(applications, opportunities)
            if changed:
                storage.save_applications(applications_path, applications)
            continue

        if choice == 5:
            changed = tracker.remove_application_flow(applications, opportunities)
            if changed:
                storage.save_applications(applications_path, applications)
            continue


def export_calendar(applications, opportunities):
    """Export tracked application deadlines to an ICS calendar file."""
    if len(applications) == 0:
        print("No tracked applications yet. Exporting an empty calendar file.")

    calendar_path = build_calendar_export_path()
    written_path = ics_export.export_applications_to_ics(
        applications,
        opportunities,
        calendar_path,
    )
    print("Calendar exported to: " + written_path)
    print("Import this into Google Calendar with Settings > Import & export > Import.")


def ask_cost_filter():
    """Ask whether to show all opportunities or free-only, via validation gateway."""
    print("")
    print("Filter by cost:")
    print("1. All opportunities")
    print("2. Free only")
    choice = validation.get_valid_int("Choose filter: ", 1, 2)

    if choice == 2:
        return "free"
    return "all"


def run_menu():
    """Run the menu loop until the user chooses to quit."""
    opportunities_path = build_opportunities_path()
    applications_path = build_applications_path()
    student_path = build_student_path()
    interests_path = build_interests_path()

    opportunities = storage.load_opportunities(opportunities_path)
    applications = storage.load_applications(applications_path)
    interest_tree = interests_module.load_interest_tree(interests_path)

    student = storage.load_student(student_path)
    if student is not None:
        print("Profile loaded from last session")

    last_results = []

    while True:
        show_menu(student)
        choice = validation.get_valid_int("Choose an option: ", 0, 11)

        if choice == 0:
            print("Goodbye.")
            return

        if choice == 1:
            student = ask_student_profile()
            storage.save_student(student_path, student)
            last_results = []
            print("Profile saved for future sessions.")
            continue

        if choice == 2:
            if ensure_profile(student):
                ranked = get_ranked_results(opportunities, student, interest_tree)
                last_results = run_feed_options(ranked)
                show_feed(last_results)
                print_match_tips(opportunities, student, interest_tree)
            continue

        if choice == 3:
            if ensure_profile(student):
                if len(last_results) == 0:
                    last_results = get_ranked_results(
                        opportunities, student, interest_tree
                    )
                choose_breakdown_result(last_results)
            continue

        if choice == 4:
            run_tracker_menu(
                applications,
                opportunities,
                last_results,
                applications_path,
            )
            continue

        if choice == 5:
            export_calendar(applications, opportunities)
            continue

        if choice == 6:
            firsttimer.run_first_timer_menu()
            continue

        if choice == 7:
            stats_module.print_stats(opportunities, student)
            continue

        if choice == 8:
            if ensure_profile(student):
                if len(last_results) == 0:
                    last_results = get_ranked_results(
                        opportunities, student, interest_tree
                    )
                digest_path = build_digest_path()
                written = digest.generate_digest(last_results, student, digest_path)
                print("")
                print("Weekly digest written to: " + written)
                print("Paste this into your class group chat to share opportunities.")
            continue

        if choice == 9:
            student = Student(
                DEMO_STUDENT_NAME,
                DEMO_STUDENT_LEVEL,
                DEMO_STUDENT_INTERESTS,
            )
            last_results = []
            storage.save_student(student_path, student)
            print("")
            print("Demo student loaded: " + student.name
                  + " | " + student.level
                  + " | " + ", ".join(student.interests))
            continue

        if choice == 10:
            fairness.print_audit(opportunities, Student)
            continue

        if choice == 11:
            if ensure_profile(student):
                show_closing_this_week(opportunities, student)
            continue


def main():
    """Start the command-line program and return an operating-system status."""
    run_menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())
