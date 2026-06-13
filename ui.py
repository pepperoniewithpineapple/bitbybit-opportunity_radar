"""Hand-rolled terminal polish for Opportunity Radar — ANSI colors and aligned tables."""

import os
import re
import sys

# Enable ANSI escape code processing on Windows terminals.
os.system("")

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"

# Matches ANSI escape sequences so we can measure a cell's *visible* width.
ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def use_color():
    """Return True when the terminal supports ANSI colors and color is not disabled."""
    if os.environ.get("NO_COLOR", "") != "":
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def paint(text, code):
    """Wrap text in an ANSI color code when the terminal supports it."""
    if use_color():
        return code + text + RESET
    return text


def visible_len(text):
    """Return the on-screen length of text, ignoring any ANSI color codes."""
    return len(ANSI_PATTERN.sub("", str(text)))


def pad_cell(text, width):
    """Left-justify text to width using its visible length, so colored cells still align."""
    padding = width - visible_len(text)
    if padding < 0:
        padding = 0
    return str(text) + (" " * padding)


def header(title):
    """Print a bold cyan banner line for a section heading."""
    line = "=" * (len(title) + 4)
    print(paint(line, BOLD + CYAN))
    print(paint("  " + title + "  ", BOLD + CYAN))
    print(paint(line, BOLD + CYAN))


def print_table(headers, rows):
    """Print a left-aligned table with computed column widths.

    Columns are sized to the widest value in each column so nothing wraps
    or misaligns even when content lengths vary.
    """
    col_widths = []
    for i, header_text in enumerate(headers):
        col_widths.append(visible_len(header_text))

    for row in rows:
        for i, cell in enumerate(row):
            cell_len = visible_len(cell)
            if cell_len > col_widths[i]:
                col_widths[i] = cell_len

    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    header_cells = ""
    for i, header_text in enumerate(headers):
        header_cells = header_cells + "| " + pad_cell(header_text, col_widths[i]) + " "
    header_cells = header_cells + "|"

    print(separator)
    print(paint(header_cells, BOLD))
    print(separator)

    for row in rows:
        row_line = ""
        for i, cell in enumerate(row):
            row_line = row_line + "| " + pad_cell(cell, col_widths[i]) + " "
        row_line = row_line + "|"
        print(row_line)

    print(separator)


def bar_chart(pairs, max_bars=8, width=30):
    """Print a horizontal ASCII bar chart from (label, value) pairs."""
    limited_pairs = list(pairs)[:max_bars]

    if len(limited_pairs) == 0:
        print("  No data to chart.")
        return

    max_value = 0
    label_width = 0

    for label, value in limited_pairs:
        if value > max_value:
            max_value = value
        if len(str(label)) > label_width:
            label_width = len(str(label))

    if max_value <= 0:
        max_value = 1

    for label, value in limited_pairs:
        bar_length = int(round(value / max_value * width))
        if value > 0 and bar_length == 0:
            bar_length = 1

        label_text = str(label)
        padding = " " * (label_width - len(label_text))
        bar = "#" * bar_length
        print("  " + label_text + padding + " | " + bar + " " + str(value))


def countdown_badge(days_left):
    """Return a colored, ASCII-safe countdown badge based on deadline urgency.

    ASCII tokens (no unicode glyphs) so it renders on every terminal, including
    Windows code pages that cannot display symbols.
    """
    if days_left < 0:
        return paint("CLOSED", RED)
    if days_left < 7:
        return paint("DUE " + str(days_left) + "d", YELLOW)
    return paint(str(days_left) + "d left", GREEN)
