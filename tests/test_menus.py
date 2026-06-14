"""Tests for grouped CLI menu presentation."""

import io
import unittest
from contextlib import redirect_stdout

import main
from models import Student


def render(function, *args):
    """Capture printed menu text."""
    output = io.StringIO()
    with redirect_stdout(output):
        function(*args)
    return output.getvalue()


class TestGroupedMenus(unittest.TestCase):
    """Check that features are grouped without disappearing."""

    def test_student_top_menu_is_grouped(self):
        student = Student("Wei Ming", "JC", ["coding"])

        text = render(main.show_menu, student)

        self.assertIn("1. Profile", text)
        self.assertIn("2. Discover opportunities", text)
        self.assertIn("3. My applications and sharing", text)
        self.assertIn("4. Equity and transparency lab", text)
        self.assertIn("5. Career intelligence lab", text)
        self.assertIn("6. Help and demo tools", text)
        self.assertNotIn("15. Build my career pathway", text)

    def test_student_submenus_keep_old_features_reachable(self):
        discover = render(main.show_discover_menu)
        applications = render(main.show_applications_menu)
        equity = render(main.show_equity_menu)
        career = render(main.show_career_lab_menu)
        help_menu = render(main.show_help_menu)

        self.assertIn("View ranked + explained For You feed", discover)
        self.assertIn("Show full scoring breakdown", discover)
        self.assertIn("Closing this week", discover)
        self.assertIn("Application tracker", applications)
        self.assertIn("Export tracker deadlines", applications)
        self.assertIn("Generate shareable weekly digest", applications)
        self.assertIn("Invisible starting-line simulation", equity)
        self.assertIn("Bias self-audit", equity)
        self.assertIn("Opportunity-gap statistics", equity)
        self.assertIn("Career impact simulator", career)
        self.assertIn("Hidden opportunity graph discovery", career)
        self.assertIn("Build my career pathway", career)
        self.assertIn("Load demo student", help_menu)
        self.assertIn("First-timer guide", help_menu)

    def test_sender_top_menu_is_grouped(self):
        text = render(main.show_sender_menu, [])

        self.assertIn("1. Demand gap radar", text)
        self.assertIn("2. Submit a new opportunity for review", text)
        self.assertIn("3. Review pending submissions", text)
        self.assertIn("4. Live opportunities and announcements", text)
        self.assertIn("5. Reviewer diagnostics", text)
        self.assertNotIn("6. Model health and training audit", text)

    def test_sender_submenus_keep_old_features_reachable(self):
        live = render(main.show_live_announcements_menu)
        diagnostics = render(main.show_reviewer_diagnostics_menu)

        self.assertIn("List live opportunities", live)
        self.assertIn("Generate announcement for an opportunity", live)
        self.assertIn("Model health and training audit", diagnostics)


if __name__ == "__main__":
    unittest.main()
