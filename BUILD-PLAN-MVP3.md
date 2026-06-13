# BUILD-PLAN MVP-3 — polish to rubric-max (codex executes this)

Existing app in this directory works: 14 tests pass. MVP-1 (profile→matcher→explained feed) + MVP-2 (tracker, .ics export, first-timer) done. This pass = POLISH + DEPTH to maximize the BbB Grand Challenge rubric. **Do NOT add half-finished scope — every new feature must be complete + tested.**

## Hard constraints (unchanged — obey exactly)
- Python 3, STDLIB ONLY. No pip packages.
- Beginner-readable: plain classes, docstring on every class + function, clear names, no clever one-liners.
- Windows host. Keep the existing `sys.stdout.reconfigure(encoding="utf-8")`. Use `os.path.join`.
- EVERY input goes through `validation.py` gateway. No raw `input()`.
- Do NOT break the existing 14 tests. Run the full suite at the end.
- Read existing files first and match their style: main.py, models.py, validation.py, storage.py, matcher.py, tracker.py, ics_export.py, firsttimer.py, data/opportunities.json.

## Rubric targets (why each task exists)
Logic&Syntax /5 (recursion), Code Structure /5 (modular — keep), Documentation /5 (README), Data Handling /5 (stats + digest File I/O), Innovation&Effort /5 (ANSI polish + real problem).

---

## TASK 1 — `ui.py` (NEW): hand-rolled terminal polish
- ANSI color constants (RESET, BOLD, RED, GREEN, YELLOW, CYAN, DIM). No external libs (no colorama).
- On Windows enable ANSI once at import with `os.system("")` (add a comment: "enables ANSI escape processing on Windows terminals").
- `use_color()` returns False if output is not a TTY (`sys.stdout.isatty()`) so piped output stays clean — fallback to plain text.
- Functions (all docstringed): `paint(text, code)`, `header(title)` (bold cyan banner), `print_table(headers, rows)` (compute column widths, aligned columns, no external lib), `countdown_badge(days_left)` (returns "⚠ 3 days" yellow if <7, "EXPIRED" red if <0, green "✓ 21 days" otherwise).
- Refactor existing feed/tracker prints to use `print_table` + `countdown_badge` so the whole app looks designed. Keep it readable.

## TASK 2 — recursion: interest taxonomy
- `data/interests.json` (NEW): a nested tree of interest categories, e.g. `{"Technology": ["AI","coding","cybersecurity","robotics","data"], "Science": ["biology","chemistry","physics","astronomy"], "Arts": ["design","writing","music"], "Business": ["entrepreneurship","finance","marketing"]}` — make 4-5 top categories, each with leaf interests. Support at least one nested-deeper branch (a sub-category that itself has children) so recursion is genuinely needed, not a flat loop.
- `interests.py` (NEW): `load_interest_tree(path)`, and **a genuinely RECURSIVE** `expand_interest(tree, name)` that returns the full list of leaf interests under any node (handles arbitrary nesting depth). Docstring must state it is recursive and why.
- Wire into `matcher.py`: when a student picks a broad interest like "Technology", expand it recursively so they match AI/coding/etc. Existing scoring + explanation still works; the explanation should still name the concrete matched interests.

## TASK 3 — `stats.py` (NEW): the gap-map view (Data Handling flourish)
- Compute from `data/opportunities.json` (+ tracked applications if present):
  - Supply by interest (count of opportunities per interest).
  - Free-vs-paid ratio (count + percentage).
  - Deadline-pressure distribution (how many close in <7 / 7-30 / 30+ days).
  - "Unmet interests": interests in the student profile / interest-tree with ZERO or very few matching opportunities — print these as "the opportunity gap" (the empty-radar idea: a near-empty result is itself the insight).
- Display with `ui.py` tables. Add a menu option. Keep all logic in functions, docstringed.

## TASK 4 — `digest.py` (NEW): shareable weekly digest (File I/O flourish)
- Generate `weekly_digest.txt`: a clean, plain-text formatted digest of the current student's top ~5 ranked opportunities (title, deadline countdown, one-line why, url), with a header line and a footer "Shared from Opportunity Radar". Made to paste into a class group chat.
- Print the absolute path written + a one-line "paste this into your class chat" hint. Add a menu option.

## TASK 5 — cost filter on the feed (equity filter)
- Add ability to filter the For You feed by cost: All / Free only. Use `get_valid_choice`. Small, complete.

## TASK 6 — demo insurance + robustness
- Add menu option "Load demo student" that instantly sets a preset profile (name "Wei Ming", level "JC", interests ["coding","AI","cybersecurity"]) so the live 7-min demo never depends on fat-fingered typing.
- `storage.py`: make load functions handle MISSING file and CORRUPT/invalid JSON gracefully — return an empty list + a human message, never crash. (Brief rewards crash-resistance.)

## TASK 7 — seed recognizable real events into `data/opportunities.json`
Add these (realistic, deadlines spread within next 5-55 days from 2026-06-13; keep existing entries):
- **National Cybersecurity Olympiad (NCO)** — organizer "NUS Computing / CeNCE", type "competition", interests ["cybersecurity","coding"], eligible_levels ["Secondary","JC"], cost "free", beginner_friendly true, a real-looking URL (comp.nus.edu.sg). (This is judge Mr Zhen Xian Kee's event.)
- A **Hult Prize**-style social-enterprise student challenge (interests ["entrepreneurship","social impact"], University+JC).
- An **IMDA / DSTA**-style tech programme and an **NUS/NTU** workshop. Keep them plausible, clearly student-facing, mix of free/paid and levels.

## TASK 8 — `README.md` (NEW): Documentation 0→5 (Advanced tier)
Write a detailed, polished README with these sections (the rubric's Advanced tier wants file map + usage examples + thoughtful reflection):
1. **Title & one-paragraph description** — what it is + WHY (tie to the BbB mission: opportunities travel through privileged networks; this opens access; matcher is transparent/bias-interrupting per Eberhardt; levels the starting line per Teo You Yenn). 2-3 sentences of "why".
2. **Features** — bullets that NAME the rubric-relevant techniques: "Persistent structured state via JSON File I/O", "Generates a real .ics calendar file (File I/O)", "Hand-written weighted scoring algorithm with transparent, explainable output", "Recursive interest-taxonomy expansion", "Central input-validation gateway — crash-resistant on any bad input", "OOP: Opportunity / Student / Application classes".
3. **How to Run** — exact: `python main.py` (Python 3, no installs needed). Note Windows UTF-8 handled automatically.
4. **File Structure** — a map of every file + one line each.
5. **Reflection** — hardest problem + how solved (e.g. designing a fair, explainable scoring algorithm; making it crash-resistant); "If we had two more weeks" (a live opportunity-gap dashboard, schools posting opportunities after demand is proven). Keep honest + thoughtful.
6. **Tech notes** — "No external libraries — every line is ours and explainable." + how to run tests: `python -m unittest discover -s tests`.

## TASK 9 — tests for new modules
- `tests/test_interests.py`: recursion returns all leaves incl. deep nesting; unknown node returns empty.
- `tests/test_stats.py`: supply count correct, free/paid ratio correct, unmet-interest detection.
- `tests/test_digest.py`: digest file is written, contains the header + at least the top match title.
- Keep beginner-comprehensible (use tempfile for file outputs). Do NOT break existing tests.

## TASK 10 — repo hygiene (local only — do NOT create a remote or push)
- `git init` locally.
- `.gitignore`: `__pycache__/`, `*.pyc`, `weekly_digest.txt`, `calendar_export.ics`, `*.ics`.
- Do NOT create a GitHub remote, do NOT push, do NOT touch any credentials. (User will create the public GitHub repo + add teammates themselves via VS Code per the brief's Annex A.)

## FINISH
Run `python -m unittest discover -s tests` — ALL tests (old + new) must pass. Smoke-check `python main.py` launches and every new menu item appears + works. Report: final file tree, total test count + pass/fail, the new menu, and first ~12 lines of a generated weekly_digest.txt.
