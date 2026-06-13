"""First-timer guides for common opportunity types."""

import validation


GUIDES = {
    "hackathon": {
        "title": "Hackathon",
        "what": (
            "A hackathon is a short build sprint where students create a "
            "prototype, demo, or idea around a theme. In Singapore, many are "
            "run by universities, agencies, or companies, and beginner tracks "
            "often care more about clear problem-solving than polished code."
        ),
        "prepare": (
            "Bring a laptop, charger, water bottle, and any account logins you "
            "need for coding tools. Prepare a simple intro about your skills: "
            "coding, design, slides, research, pitching, or organising."
        ),
        "teams": (
            "Teams usually form before the event or during a matching session. "
            "If you do not have a team, look for classmates from other schools "
            "who bring different strengths instead of only choosing friends."
        ),
        "expect": (
            "Judges usually expect a clear problem, a realistic user, a demo "
            "that proves the idea, and honest next steps. A simple working "
            "prototype beats an overpromised pitch."
        ),
        "tip": (
            "First step: write one sentence for the problem you want to solve "
            "for Singapore students, families, schools, or communities."
        ),
    },
    "competition": {
        "title": "Competition",
        "what": (
            "A competition asks you to submit work against a brief, such as a "
            "case solution, science project, business idea, or design proposal."
        ),
        "prepare": (
            "Read the judging criteria first, then plan backwards from the "
            "deadline. Prepare evidence, screenshots, citations, calculations, "
            "or user feedback depending on the competition type."
        ),
        "teams": (
            "Some competitions allow solo entries, while others require teams. "
            "For team entries, agree early on who owns research, writing, "
            "slides, prototype work, and final submission."
        ),
        "expect": (
            "Assessors expect your answer to match the brief directly. They "
            "look for clarity, feasibility, originality, and whether you can "
            "explain tradeoffs without sounding vague."
        ),
        "tip": (
            "First step: copy the judging criteria into a checklist and make "
            "sure every section of your submission answers one item."
        ),
    },
    "scholarship": {
        "title": "Scholarship",
        "what": (
            "A scholarship supports study, research, or a pathway into a field. "
            "In Singapore, many scholarships also look for service, leadership, "
            "and a clear reason you care about the sector."
        ),
        "prepare": (
            "Prepare your results, CCA or project records, personal statement, "
            "referee details, and examples of work. Keep a simple timeline so "
            "teachers or mentors have enough time to write references."
        ),
        "teams": (
            "Scholarships are usually individual applications, but you should "
            "still ask seniors, ECG counsellors, teachers, or family members to "
            "review your statement before submission."
        ),
        "expect": (
            "Assessors expect evidence of commitment, not just ambition. They "
            "want to see what you have tried, what you learned, and why this "
            "scholarship fits your next step."
        ),
        "tip": (
            "First step: draft three short stories about projects, setbacks, "
            "or service experiences that show how you think and follow through."
        ),
    },
    "workshop": {
        "title": "Workshop",
        "what": (
            "A workshop is a guided learning session where you practise a skill "
            "or explore a field. It is often the best low-pressure first step "
            "before a competition, olympiad, attachment, or scholarship."
        ),
        "prepare": (
            "Bring note-taking tools, a laptop if requested, and any pre-event "
            "setup instructions. If the organiser sends software steps, finish "
            "them before arrival so you can focus on learning."
        ),
        "teams": (
            "Most workshops are individual, but activities may put you in small "
            "groups. Be ready to introduce yourself and ask clear questions."
        ),
        "expect": (
            "Facilitators expect attention, participation, and a willingness to "
            "try. You are not expected to already know everything."
        ),
        "tip": (
            "First step: write down two questions you want answered by the end "
            "of the workshop."
        ),
    },
    "olympiad": {
        "title": "Olympiad",
        "what": (
            "An olympiad is a high-rigour academic contest, usually in areas "
            "like math, informatics, physics, chemistry, biology, or astronomy."
        ),
        "prepare": (
            "Prepare by practising past questions under timed conditions. Keep "
            "a mistake log so you can spot patterns instead of only collecting "
            "more questions."
        ),
        "teams": (
            "Most early rounds are individual. Training groups still help: "
            "students can compare solution methods and explain ideas to each "
            "other after attempting problems alone."
        ),
        "expect": (
            "Assessors expect precise reasoning, not just final answers. For "
            "informatics, clean algorithms matter. For math and science, show "
            "the steps that justify your conclusion."
        ),
        "tip": (
            "First step: attempt one past-paper question, then spend more time "
            "reviewing the solution than you spent doing the question."
        ),
    },
}


GUIDE_TYPES = ["hackathon", "competition", "scholarship", "workshop", "olympiad"]


def print_guide(guide_type):
    """Print the first-timer guide for one opportunity type."""
    guide = GUIDES[guide_type]

    print("")
    print(guide["title"])
    print("")
    print(guide["what"])
    print("")
    print("What to bring or prepare:")
    print(guide["prepare"])
    print("")
    print("How teams form:")
    print(guide["teams"])
    print("")
    print("What judges or assessors expect:")
    print(guide["expect"])
    print("")
    print("One first-step tip:")
    print(guide["tip"])


def run_first_timer_menu():
    """Ask for an opportunity type and print its first-timer guide."""
    print("")
    print("First-timer mode")
    index = 1
    for guide_type in GUIDE_TYPES:
        print(str(index) + ". " + guide_type)
        index = index + 1

    choice = validation.get_valid_int(
        "Choose a type number: ",
        1,
        len(GUIDE_TYPES),
    )
    print_guide(GUIDE_TYPES[choice - 1])
