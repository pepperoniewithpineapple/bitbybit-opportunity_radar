"""Command-line interface for Opportunity Radar."""

import os
import sys

# Reconfigure stdout to UTF-8 for Windows terminals.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import access
import career_model
import demand
import digest
import fairness
import filters
import firsttimer
import graph_rank
import ics_export
import interests as interests_module
import matcher
import pathway
import recommend
import review_queue
import sender
import spam_model
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


def build_searches_path():
    """Return the path to anonymous student search demand signals."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "searches.json")


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


def build_sender_packet_path():
    """Return the path to the generated sender announcement text file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "opportunity_sender_packet.txt")


def build_submissions_path():
    """Return the path to the pending sender submissions JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "data", "submissions.json")


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
    ui.header("Student / Opportunity Finder")
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
    print("12. Invisible starting-line simulation")
    print("13. Career impact simulator")
    print("14. Hidden opportunity graph discovery")
    print("15. Build my career pathway")
    print("0.  Back to mode selection")


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


def ask_career_goal():
    """Ask the student which career direction to simulate."""
    careers = career_model.career_names()

    print("")
    print("Career goals:")
    for index, career in enumerate(careers):
        print(str(index + 1) + ". " + career)

    choice = validation.get_valid_int("Choose career goal: ", 1, len(careers))
    return careers[choice - 1]


def choose_impact_opportunity(results):
    """Ask the user to choose a ranked opportunity for career impact."""
    if len(results) == 0:
        print("No ranked opportunities available. View the feed first.")
        return None

    print("")
    print("Choose an opportunity to simulate:")
    for index, result in enumerate(results):
        opportunity = result["opportunity"]
        print(str(index + 1) + ". " + opportunity.title)

    choice = validation.get_valid_int(
        "Choose opportunity number: ",
        1,
        len(results),
    )
    return results[choice - 1]["opportunity"]


def print_career_impact(impact):
    """Print one career impact result in a transparent, judge-friendly format."""
    opportunity = impact["opportunity"]

    print("")
    ui.header("Career Impact Simulator")
    print("")
    print("Career goal: " + impact["career"])
    print("Opportunity: " + opportunity.title)
    print("")
    print("This is NOT a real hiring-probability prediction.")
    print("It estimates career-readiness alignment if you join and complete it.")
    print("The model uses weighted skill vectors, not real hiring probability.")
    print("")
    print("Before joining: " + format(impact["before"], ".1f") + "/100")
    print("After joining:  " + format(impact["after"], ".1f") + "/100")

    delta_text = format(impact["delta"], "+.1f")
    print("Impact: " + impact["classification"] + " (" + delta_text + " points)")
    print("")
    print("Why:")
    for reason in impact["reasons"]:
        print("- " + reason)


def show_best_career_boosters(career_name, student, results):
    """Print the strongest positive career boosters from current feed results."""
    opportunities = []
    for result in results:
        opportunities.append(result["opportunity"])

    impacts = career_model.rank_impacts(career_name, student, opportunities, limit=5)

    print("")
    print("Strongest career boosters in your current feed:")
    rows = []
    for impact in impacts:
        opportunity = impact["opportunity"]
        rows.append([
            opportunity.title[:42] + ("..." if len(opportunity.title) > 42 else ""),
            impact["classification"],
            format(impact["delta"], "+.1f"),
            format(impact["after"], ".1f") + "/100",
        ])

    ui.print_table(["Opportunity", "Impact", "Delta", "After"], rows)


def run_career_impact_flow(student, results):
    """Run the career impact simulator."""
    if len(results) == 0:
        print("View the For You feed first so there are opportunities to simulate.")
        return

    career_name = ask_career_goal()
    show_best_career_boosters(career_name, student, results)
    opportunity = choose_impact_opportunity(results)

    if opportunity is None:
        return

    impact = career_model.evaluate_opportunity(career_name, student, opportunity)
    print_career_impact(impact)


def run_graph_discovery_flow(opportunities, student):
    """Run hidden opportunity discovery using graph ranking."""
    print("")
    ui.header("Hidden Opportunity Graph Discovery")
    print("")
    print("This uses a personalized PageRank-style graph over interests,")
    print("careers, organizers, and opportunities.")
    print("")

    use_career = validation.get_valid_choice(
        "Add a career goal to personalize the graph? (yes/no): ",
        ["yes", "no"],
    )
    career_name = None
    if use_career == "yes":
        career_name = ask_career_goal()

    rows = graph_rank.rank_hidden_opportunities(
        opportunities,
        student,
        career_name,
        limit=5,
    )

    if len(rows) == 0:
        print("No eligible graph discoveries found yet.")
        return

    table_rows = []
    for index, row in enumerate(rows):
        opportunity = row["opportunity"]
        table_rows.append([
            str(index + 1),
            short_text(opportunity.title, 36),
            format(row["graph_score"], ".4f"),
            str(len(row["shared_interests"])),
            short_text(row["path_text"], 58),
        ])

    ui.print_table(["#", "Opportunity", "GraphRank", "Direct", "Bridge path"], table_rows)
    print("")
    print("Direct = exact interest matches. Low direct match + good graph path")
    print("means the opportunity may be a hidden bridge.")


def run_pathway_flow(opportunities, student):
    """Run the career pathway planner."""
    print("")
    ui.header("Career Pathway Planner")
    print("")
    career_name = ask_career_goal()
    plan = pathway.build_pathway(career_name, student, opportunities)

    print("")
    print("Career goal: " + career_name)
    print("Starting readiness: " + format(plan["starting_score"], ".1f") + "/100")

    missing = []
    for item in plan["missing_skills"][:5]:
        missing.append(item["skill"])

    if len(missing) > 0:
        print("Top missing skills: " + ", ".join(missing))
    else:
        print("Top missing skills: none detected")

    rows = []
    for step in plan["steps"]:
        opportunity = step["opportunity"]
        if opportunity is None:
            title = "No live fit yet"
            deadline = "-"
        else:
            title = short_text(opportunity.title, 38)
            deadline = opportunity.deadline

        rows.append([
            step["stage_label"],
            ", ".join(step["target_types"]),
            title,
            deadline,
            short_text(step["reason"], 50),
        ])

    print("")
    ui.print_table(["Stage", "Types", "Suggested step", "Deadline", "Why"], rows)


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


def show_mode_menu(student):
    """Print the top-level two-mode menu."""
    print("")
    ui.header("Opportunity Radar")
    print("Two modes. One shared opportunity engine.")
    print_profile(student)
    print("")
    print("1. Student / Opportunity Finder mode")
    print("2. Opportunity Sender mode")
    print("0. Quit")


def build_career_student(student, interest_tree):
    """Return a student profile with raw and expanded interests preserved."""
    expanded = interests_module.get_expanded_interests(
        interest_tree,
        student.interests,
    )
    seen = set()
    combined = []

    for interest in list(student.interests) + list(expanded):
        key = interest.strip().lower()
        if key not in seen:
            seen.add(key)
            combined.append(interest)

    return Student(student.name, student.level, combined)


def ask_level_list():
    """Ask for one or more eligible student levels."""
    while True:
        print("")
        print("Eligible levels:")
        for index, level in enumerate(LEVELS):
            print(str(index + 1) + ". " + level)
        print("Type comma-separated numbers, or 'all'.")

        raw_text = validation.nonempty("Eligible levels: ")
        if raw_text.strip().lower() == "all":
            return list(LEVELS)

        selected = []
        valid = True
        pieces = raw_text.split(",")

        for piece in pieces:
            cleaned = piece.strip()
            if not cleaned.isdigit():
                valid = False
                break

            number = int(cleaned)
            if number < 1 or number > len(LEVELS):
                valid = False
                break

            level = LEVELS[number - 1]
            if level not in selected:
                selected.append(level)

        if valid and len(selected) > 0:
            return selected

        print("Please enter level numbers like 1,2 or type all.")


def ask_sender_type():
    """Ask for the opportunity type in sender mode."""
    print("")
    print("Opportunity type:")
    for index, opp_type in enumerate(sender.OPPORTUNITY_TYPES):
        print(str(index + 1) + ". " + opp_type)

    choice = validation.get_valid_int(
        "Choose opportunity type: ",
        1,
        len(sender.OPPORTUNITY_TYPES),
    )
    selected = sender.OPPORTUNITY_TYPES[choice - 1]

    if selected == "other":
        return validation.nonempty("Custom type: ")
    return selected


def ask_sender_interests():
    """Ask for opportunity interest tags."""
    while True:
        raw_interests = validation.nonempty(
            "Interest tags, separated by commas: "
        )
        interests = parse_interests(raw_interests)

        if len(interests) > 0:
            return interests

        print("Please include at least one interest tag.")


def ask_sender_deadline():
    """Ask for a deadline that has not already passed."""
    while True:
        deadline = validation.get_valid_date("Deadline (YYYY-MM-DD): ")
        if matcher.days_until(deadline) >= 0:
            return deadline
        print("Please enter a deadline that has not already passed.")


def ask_sender_opportunity(opportunities):
    """Ask an organizer for a complete opportunity record."""
    print("")
    ui.header("Submit A New Opportunity")
    print("")
    print("This creates a pending submission. A reviewer must approve it before")
    print("students can see it in Finder mode.")
    print("")

    while True:
        title = validation.nonempty("Opportunity title: ")
        if not sender.title_exists(opportunities, title):
            break
        print("That title already exists. Please use a unique title.")

    organizer = validation.nonempty("Organizer name: ")
    opp_type = ask_sender_type()
    interests = ask_sender_interests()
    eligible_levels = ask_level_list()
    cost = validation.get_valid_choice("Cost (free/paid): ", ["free", "paid"])
    beginner_text = validation.get_valid_choice(
        "Beginner-friendly? (yes/no): ",
        ["yes", "no"],
    )
    beginner_friendly = beginner_text == "yes"
    deadline = ask_sender_deadline()
    url = validation.nonempty("Application/info URL: ")

    return sender.build_opportunity(
        storage.next_opportunity_id(opportunities),
        title,
        opp_type,
        interests,
        eligible_levels,
        cost,
        beginner_friendly,
        deadline,
        url,
        organizer,
    )


def print_sender_gap_radar(opportunities, searches_path):
    """Print demand-vs-supply gap information for organizers."""
    print("")
    ui.header("Sender Demand Radar")
    print("")

    rows = sender.build_gap_rows(opportunities, searches_path)

    if len(rows) == 0:
        print("No anonymous student search demand has been logged yet.")
        print("Showing low-supply interests so senders still have a starting point.")
        rows = sender.build_supply_thin_rows(opportunities)

    table_rows = []
    for row in rows:
        if row["gap_score"] > 0:
            gap = "+" + str(row["gap_score"])
        else:
            gap = str(row["gap_score"])

        table_rows.append([
            row["interest"],
            str(row["demand"]),
            str(row["supply"]),
            gap,
            sender.priority_label(row),
        ])

    ui.print_table(["Interest", "Demand", "Supply", "Gap", "Priority"], table_rows)
    print("")
    print("Sender idea: post where demand is high and supply is thin.")


def print_sender_preview(opportunity, opportunities, searches_path):
    """Print an impact preview before saving a sender opportunity."""
    preview = sender.build_sender_preview(opportunity, opportunities, searches_path)

    print("")
    ui.header("Sender Impact Preview")
    print("")
    print("Title: " + opportunity.title)
    print("Organizer: " + opportunity.organizer)
    print("Open to: " + ", ".join(opportunity.eligible_levels))
    print("Interests: " + ", ".join(opportunity.interests))
    print("Deadline: " + opportunity.deadline
          + " (" + str(preview["days_left"]) + " days left)")
    print("Matching anonymous interest-demand hits: "
          + str(preview["demand_matches"]))
    print("Accessibility score: " + str(preview["access_score"]) + "/100")

    if preview["access_score"] >= 80:
        print("Signal: strong access design.")
    elif preview["access_score"] >= 60:
        print("Signal: decent access design; consider making it free or beginner-friendly.")
    else:
        print("Signal: likely harder to access; explain support clearly.")


def short_text(text, limit):
    """Return text shortened for compact terminal tables."""
    if len(text) <= limit:
        return text
    return text[:limit - 3] + "..."


def print_review_flags(flags):
    """Print submission review flags in a compact table."""
    if len(flags) == 0:
        print("Review checks: clear. No blockers or warnings found.")
        return

    rows = []
    for flag in flags:
        rows.append([
            flag["severity"],
            flag["label"],
            flag["detail"],
        ])

    ui.print_table(["Severity", "Check", "Detail"], rows)


def print_submission_detail(submission, submissions, opportunities, searches_path):
    """Print one pending submission with reviewer-focused context."""
    opportunity = submission["opportunity"]
    preview = sender.build_sender_preview(opportunity, opportunities, searches_path)
    spam = review_queue.spam_assessment(submission, submissions)
    flags = review_queue.review_flags(
        submission,
        opportunities,
        searches_path,
        submissions,
    )

    print("")
    ui.header("Submission Review")
    print("")
    print("Submission: " + submission["submission_id"])
    print("Submitted: " + submission["submitted_at"])
    print("Title: " + opportunity.title)
    print("Organizer: " + opportunity.organizer)
    print("Type: " + opportunity.type)
    print("Deadline: " + opportunity.deadline)
    print("Cost: " + opportunity.cost)
    print("Beginner-friendly: " + ("yes" if opportunity.beginner_friendly else "no"))
    print("Open to: " + ", ".join(opportunity.eligible_levels))
    print("Interests: " + ", ".join(opportunity.interests))
    print("URL: " + opportunity.url)
    print("")
    print("Matching anonymous interest-demand hits: "
          + str(preview["demand_matches"]))
    print("Accessibility score: " + str(preview["access_score"]) + "/100")
    print("ML spam risk: " + spam["risk_level"]
          + " (" + str(round(spam["spam_probability"] * 100)) + "%)")
    if spam["risk_level"] != "LOW" and len(spam["signals"]) > 0:
        signal_words = []
        for signal in spam["signals"]:
            signal_words.append(signal["token"])
        print("ML spam signals: " + ", ".join(signal_words))
    print("")
    print_review_flags(flags)
    return flags


def list_pending_submissions(submissions):
    """Print pending sender submissions."""
    pending = review_queue.pending_submissions(submissions)

    print("")
    ui.header("Pending Submission Queue")
    print("")

    if len(pending) == 0:
        print("No pending submissions. The live feed is clean.")
        return []

    rows = []
    for index, submission in enumerate(pending):
        opportunity = submission["opportunity"]
        rows.append([
            str(index + 1),
            submission["submission_id"],
            short_text(opportunity.title, 38),
            short_text(opportunity.organizer, 24),
            opportunity.deadline,
        ])

    ui.print_table(["#", "ID", "Title", "Organizer", "Deadline"], rows)
    return pending


def review_pending_submissions(submissions, submissions_path, opportunities,
                               opportunities_path, searches_path):
    """Let a reviewer approve or reject pending sender submissions."""
    pending = list_pending_submissions(submissions)
    if len(pending) == 0:
        return

    choice = validation.get_valid_int(
        "Choose a submission to review, or 0 to cancel: ",
        0,
        len(pending),
    )
    if choice == 0:
        return

    submission = pending[choice - 1]
    flags = print_submission_detail(
        submission,
        submissions,
        opportunities,
        searches_path,
    )

    decision = validation.get_valid_choice(
        "Decision (approve/reject/skip): ",
        ["approve", "reject", "skip"],
    )

    if decision == "skip":
        print("Left pending for later review.")
        return

    if decision == "reject":
        note = validation.nonempty("Reviewer note: ")
        review_queue.reject_submission(submission, note)
        review_queue.save_submissions(submissions_path, submissions)
        print("Rejected. The submission stayed out of the live student feed.")
        return

    if review_queue.has_blocker(flags):
        print("Cannot approve while a BLOCKER is present.")
        print("Reject it with a note, or fix the live data first.")
        return

    new_opp_id = storage.next_opportunity_id(opportunities)
    approved = review_queue.approve_submission(
        submission,
        opportunities,
        new_opp_id,
        note="Approved through review queue.",
    )

    if approved:
        storage.save_opportunities(opportunities_path, opportunities)
        review_queue.save_submissions(submissions_path, submissions)
        print("Approved. It is now live in Student Finder mode.")
        generate_sender_packet(submission["opportunity"])
    else:
        print("Not approved because a matching live title already exists.")


def list_live_opportunities(opportunities):
    """Print a compact list of current open opportunities."""
    open_opportunities = get_open_opportunities(opportunities)

    print("")
    ui.header("Live Opportunity Store")
    print("")

    if len(open_opportunities) == 0:
        print("No open opportunities are currently stored.")
        return

    rows = []
    for index, opportunity in enumerate(open_opportunities[:15]):
        rows.append([
            str(index + 1),
            opportunity.title[:42] + ("..." if len(opportunity.title) > 42 else ""),
            opportunity.organizer,
            opportunity.type,
            opportunity.deadline,
        ])

    ui.print_table(["#", "Title", "Organizer", "Type", "Deadline"], rows)


def get_open_opportunities(opportunities):
    """Return open opportunities sorted by deadline."""
    open_opportunities = []

    for opportunity in opportunities:
        if matcher.days_until(opportunity.deadline) >= 0:
            open_opportunities.append(opportunity)

    open_opportunities.sort(key=lambda opportunity: opportunity.deadline)
    return open_opportunities


def choose_opportunity(opportunities, prompt):
    """Ask the user to choose one stored opportunity."""
    open_opportunities = get_open_opportunities(opportunities)

    if len(open_opportunities) == 0:
        print("No opportunities are available.")
        return None

    list_live_opportunities(opportunities)
    choice = validation.get_valid_int(prompt, 1, len(open_opportunities))
    return open_opportunities[choice - 1]


def generate_sender_packet(opportunity):
    """Generate a text announcement for one opportunity."""
    if opportunity is None:
        return

    path = build_sender_packet_path()
    written = sender.save_announcement(path, opportunity)
    print("")
    print("Sender announcement written to: " + written)
    print("Paste it into a school chat, CCA chat, or teacher announcement.")


def print_spam_model_audit(submissions):
    """Print training health for the adaptive spam-risk model."""
    health = spam_model.model_health(submissions)

    print("")
    ui.header("ML Spam Model Audit")
    print("")
    print("Model: Multinomial Naive Bayes, standard-library Python")
    print("Seed examples: " + str(health["seed_examples"]))
    print("Reviewer-history examples: " + str(health["history_examples"]))
    print("Total training examples: " + str(health["total_examples"]))
    print("Spam examples: " + str(health["spam_examples"]))
    print("Legit examples: " + str(health["legit_examples"]))
    print(
        "Leave-one-out accuracy: "
        + format(health["leave_one_out_accuracy"] * 100, ".1f")
        + "%"
    )

    rows = []
    for signal in health["top_spam_tokens"]:
        rows.append([
            signal["token"],
            format(signal["weight"], ".2f"),
        ])

    if len(rows) > 0:
        print("")
        ui.print_table(["Learned spam token", "Weight"], rows)


def show_sender_menu(submissions):
    """Print the Opportunity Sender mode menu."""
    counts = review_queue.status_counts(submissions)
    print("")
    ui.header("Opportunity Sender Mode")
    print("Submit supply into the gaps students reveal. Review before publishing.")
    print("Queue: " + str(counts[review_queue.PENDING]) + " pending, "
          + str(counts[review_queue.APPROVED]) + " approved, "
          + str(counts[review_queue.REJECTED]) + " rejected")
    print("")
    print("1. View demand gap radar")
    print("2. Submit a new opportunity for review")
    print("3. Review pending submissions")
    print("4. List live opportunities")
    print("5. Generate announcement for an opportunity")
    print("6. Model health and training audit")
    print("0. Back to mode selection")


def run_sender_mode(opportunities, opportunities_path, searches_path,
                    submissions_path):
    """Run the organizer-facing sender mode."""
    submissions = review_queue.load_submissions(submissions_path)

    while True:
        show_sender_menu(submissions)
        choice = validation.get_valid_int("Choose sender option: ", 0, 6)

        if choice == 0:
            return

        if choice == 1:
            print_sender_gap_radar(opportunities, searches_path)
            continue

        if choice == 2:
            print_sender_gap_radar(opportunities, searches_path)
            opportunity = ask_sender_opportunity(opportunities)
            print_sender_preview(opportunity, opportunities, searches_path)
            confirm = validation.get_valid_choice(
                "Submit this opportunity for review? (yes/no): ",
                ["yes", "no"],
            )

            if confirm == "yes":
                submission = review_queue.create_submission(
                    submissions,
                    opportunity,
                )
                review_queue.save_submissions(submissions_path, submissions)
                print("Submitted as " + submission["submission_id"] + ".")
                print("It is not live until a reviewer approves it.")
            else:
                print("Draft discarded.")
            continue

        if choice == 3:
            review_pending_submissions(
                submissions,
                submissions_path,
                opportunities,
                opportunities_path,
                searches_path,
            )
            continue

        if choice == 4:
            list_live_opportunities(opportunities)
            continue

        if choice == 5:
            opportunity = choose_opportunity(
                opportunities,
                "Choose an opportunity number for the announcement: ",
            )
            generate_sender_packet(opportunity)
            continue

        if choice == 6:
            print_spam_model_audit(submissions)
            continue


def run_student_finder_mode(student, opportunities, applications, interest_tree,
                            applications_path, student_path, searches_path):
    """Run the student-facing opportunity finder mode."""

    last_results = []

    while True:
        show_menu(student)
        choice = validation.get_valid_int("Choose an option: ", 0, 15)

        if choice == 0:
            return student

        if choice == 1:
            student = ask_student_profile()
            storage.save_student(student_path, student)
            last_results = []
            print("Profile saved for future sessions.")
            continue

        if choice == 2:
            if ensure_profile(student):
                demand.log_search(searches_path, student.level, student.interests)
                print("Anonymous demand signal saved.")
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

        if choice == 12:
            if ensure_profile(student):
                expanded = interests_module.get_expanded_interests(
                    interest_tree,
                    student.interests,
                )
                simulation_student = Student(student.name, student.level, expanded)
                access.print_starting_line_simulation(
                    opportunities,
                    simulation_student,
                )
            continue

        if choice == 13:
            if ensure_profile(student):
                if len(last_results) == 0:
                    last_results = get_ranked_results(
                        opportunities,
                        student,
                        interest_tree,
                    )
                impact_student = build_career_student(student, interest_tree)
                run_career_impact_flow(impact_student, last_results)
            continue

        if choice == 14:
            if ensure_profile(student):
                graph_student = build_career_student(student, interest_tree)
                run_graph_discovery_flow(opportunities, graph_student)
            continue

        if choice == 15:
            if ensure_profile(student):
                pathway_student = build_career_student(student, interest_tree)
                run_pathway_flow(opportunities, pathway_student)
            continue


def run_menu():
    """Run the two-mode Opportunity Radar product until the user quits."""
    opportunities_path = build_opportunities_path()
    applications_path = build_applications_path()
    student_path = build_student_path()
    interests_path = build_interests_path()
    searches_path = build_searches_path()
    submissions_path = build_submissions_path()

    opportunities = storage.load_opportunities(opportunities_path)
    applications = storage.load_applications(applications_path)
    interest_tree = interests_module.load_interest_tree(interests_path)

    student = storage.load_student(student_path)
    if student is not None:
        print("Profile loaded from last session")

    while True:
        show_mode_menu(student)
        choice = validation.get_valid_int("Choose a mode: ", 0, 2)

        if choice == 0:
            print("Goodbye.")
            return

        if choice == 1:
            student = run_student_finder_mode(
                student,
                opportunities,
                applications,
                interest_tree,
                applications_path,
                student_path,
                searches_path,
            )
            continue

        if choice == 2:
            run_sender_mode(
                opportunities,
                opportunities_path,
                searches_path,
                submissions_path,
            )
            continue


def main():
    """Start the command-line program and return an operating-system status."""
    run_menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())
