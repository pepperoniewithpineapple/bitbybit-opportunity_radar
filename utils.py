import re
from datetime import datetime, date


ACADEMIC_LEVELS: tuple[str] = ("Secondary", "JC", "Poly", "University")


def normalize(text: str) -> str:
    """Lowercase, strip, and sanitize string tokens."""
    return text.strip().lower()


def tokenize(text: str) -> list[str]:
    """Regex split text into alphabetic search terms."""
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if len(t) > 1]


def days_until(date_str: str) -> int:
    """Calculate date delta relative to current date context."""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        delta = target_date - date.today()
        return delta.days
    except ValueError:
        return 999  # Fallback for dynamic/bad dates


def is_open_to(opportunity_levels: list[str], student_level: str) -> bool:
    """Simple list membership inclusion guard."""
    return any(normalize(lvl) == normalize(student_level) for lvl in opportunity_levels)