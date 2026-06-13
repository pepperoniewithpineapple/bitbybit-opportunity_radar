# BUILD-PLAN MVP-4 — make the TERMINAL app deeper (codex executes)

The web app is REMOVED. This is a terminal-only Python app. Existing state: 46 tests pass.
Goal: add depth so it feels like a real, advanced product — NOT a toy — while keeping the
code beginner-readable and 100% standard library. Every feature must be COMPLETE + TESTED.

## Hard constraints (obey exactly)
- Python 3, STDLIB ONLY. No web app, no pip packages.
- Beginner-readable: plain classes, docstring on every class + function, clear names.
- Windows host. main.py already reconfigures stdout to utf-8. Use os.path.join.
- EVERY input goes through validation.py gateway (get_valid_int / get_valid_choice / get_valid_date / nonempty). No raw input().
- Do NOT break the existing 46 tests. Run the full suite at the end.
- Read existing files first and match their style: main.py, matcher.py, storage.py, models.py, stats.py, ui.py, interests.py, validation.py.

## Existing main.py menu (extend it, keep 0 = Quit)
1 profile · 2 feed · 3 breakdown · 4 tracker · 5 ics · 6 first-timer · 7 stats · 8 digest · 9 demo student · 10 bias audit · 0 quit.
Existing helper: get_ranked_results(opportunities, student, interest_tree, cost_filter).

## TASK 1 — Persist the student profile (Data Handling + demo continuity)
- storage.py: add save_student(path, student) and load_student(path) (returns Student or None; crash-resistant on missing/corrupt file, like load_opportunities). Use models.Student.to_dict and a from-dict rebuild.
- main.py: build data/student.json path. On startup, load the saved profile if present (so the app remembers you across restarts). When the user sets a profile (option 1) or loads the demo student (option 9), save it. Print "Profile loaded from last session" when restored.

## TASK 2 — Advanced feed filtering + sorting (option 2 becomes interactive)
- New module filters.py (all functions docstringed, pure, testable):
  - filter_by_type(results, opp_type): keep results whose opportunity.type == opp_type.
  - filter_by_keyword(results, keyword): keep results whose title contains keyword (case-insensitive).
  - filter_by_deadline_window(results, max_days): keep results whose breakdown["days_left"] <= max_days.
  - sort_results(results, key): key in {"score","deadline","title"}; "score" = total desc (default), "deadline" = soonest first, "title" = A-Z. Use stdlib sorted.
- main.py option 2 flow: after ranking, offer a small submenu (via validation gateway): filter by cost (existing), by type, by keyword, by "closing within N days", and choose a sort order. Apply chosen filters/sort, then show the feed. Keep it simple and looping-friendly.

## TASK 3 — "Improve your match" suggestions (delight + intelligence)
- New module recommend.py:
  - suggest_interests(opportunities, student, interest_tree, limit=3): look at opportunities the student is ELIGIBLE for but that did NOT match their interests; count the interests on those opportunities that are NOT already in the student's (expanded) profile; return the top `limit` as a list of (interest, count) sorted by count desc. Docstring explains the idea: "interests you could add to unlock more opportunities."
- main.py: after showing the feed (option 2), print up to 3 suggestions like:
  "Tip: add 'design' to your interests to unlock 3 more opportunities."
  If none, print nothing.

## TASK 4 — ASCII bar charts in stats (terminal visual, replaces web SVG)
- ui.py: add bar_chart(pairs, max_bars=8, width=30) -> prints a horizontal ASCII bar chart from (label, value) pairs. Scale bars to the max value; use a block char like '#'. Docstring it. Keep ASCII-safe (no unicode).
- stats.py print_stats: render "supply by interest" and "deadline pressure" using ui.bar_chart so the stats screen is visual, not just numbers. Keep the existing unmet-interest "opportunity gap" section.

## TASK 5 — "Closing this week" urgent view (new menu option 11)
- New function (in matcher.py or a small new module) that returns all eligible, open opportunities for the current student closing within 7 days, sorted soonest-first.
- main.py: add menu option "11. Closing this week (urgent deadlines)". Requires a profile. Show them as a table via ui.print_table with countdown badges. If none, print a friendly message.
- Update the menu print + the get_valid_int range to 0..11.

## TASK 6 — tests for everything new (do not break the 46)
- tests/test_filters.py: each filter keeps/drops correctly; sort_results orders by score, deadline, title.
- tests/test_recommend.py: suggest_interests returns interests from eligible-but-unmatched opportunities, excludes already-held interests, respects limit.
- tests/test_storage_student.py: save_student then load_student round-trips name/level/interests; load_student returns None for missing file and for corrupt JSON.
- (Optional) a tiny ui.bar_chart smoke test: returns/prints without error for normal and empty input.
- Build minimal Opportunity/Student fixtures in each test (see existing tests for the pattern). Use tempfile for any file I/O.

## TASK 7 — docs
- Update README.md: remove all web-app mentions; add the new terminal features (persistent profile, filtering/sorting, improve-your-match, ASCII charts, closing-this-week) to the Features list and the file map; update the test count; keep it accurate.

## FINISH
Run `python -m unittest discover -s tests` — ALL tests (old + new) must pass.
Smoke-check `python main.py` launches and the new menu items (filter/sort on option 2, option 11) work.
Report: final file tree, total test count + pass/fail, and the new menu.
