"""Input validation helpers for every input in Opportunity Radar.

This is the single validation gateway. The interactive helpers (get_valid_*)
are used by the command-line interface. The pure-function checks (is_*) keep
the same rules easy to test without prompting.
"""

import datetime


def is_nonempty(text):
    """Return True when text contains at least one non-space character."""
    return text is not None and text.strip() != ""


def is_valid_date(text):
    """Return True when text is a real date in YYYY-MM-DD format."""
    if text is None:
        return False
    try:
        datetime.datetime.strptime(text.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_one_of(text, options):
    """Return True when text exactly matches one of the allowed options."""
    if text is None:
        return False
    return text.strip() in options


def clean_text(text):
    """Return text trimmed of surrounding whitespace, or empty string if None."""
    if text is None:
        return ""
    return text.strip()


def get_valid_int(prompt, lo, hi):
    """Ask for an integer between lo and hi until the user gives one."""
    while True:
        raw_value = input(prompt).strip()
        try:
            value = int(raw_value)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if value < lo or value > hi:
            print("Please enter a number from " + str(lo) + " to " + str(hi) + ".")
            continue

        return value


def get_valid_choice(prompt, options):
    """Ask for one value from options until the user gives a valid choice."""
    while True:
        value = input(prompt).strip()
        for option in options:
            if value == option:
                return value

        print("Please choose one of: " + ", ".join(options) + ".")


def get_valid_date(prompt):
    """Ask for a YYYY-MM-DD date until the user gives a valid date string."""
    while True:
        value = input(prompt).strip()
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            print("Please enter a real date in YYYY-MM-DD format.")
            continue

        return value


def nonempty(prompt):
    """Ask for text until the user gives a non-empty answer."""
    while True:
        value = input(prompt).strip()
        if value == "":
            print("Please enter something before continuing.")
            continue

        return value
