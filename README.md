# Opportunity Radar

A two-interface platform that aggregates student opportunities in Singapore, matches them to each student with a transparent and explainable algorithm, lets organizers post new opportunities, and maps where the opportunity gap actually is — all in pure Python with zero external libraries.

**Why it exists:** In Singapore, opportunities — hackathons, scholarships, olympiads, workshops — travel through privileged networks: elite schools, connected parents, plugged-in teachers. Students outside those networks never hear about the competition that could have changed their trajectory. This tool replaces network privilege with open access. Following Dr. Jennifer Eberhardt's insight about algorithmic bias, the matcher is not a black box: every recommendation explains its own reasoning, and instead of amplifying prestige signals it is deliberately and transparently weighted toward free and beginner-friendly events. We don't claim the algorithm is neutral — we **measure** that it widens access, and show the numbers.

---

## Two interfaces, one engine

The same scoring engine (`matcher.py`), data store (`data/opportunities.json`), and validation gateway (`validation.py`) power **both** front-ends, with no duplicated logic:

- **Command-line app** (`python main.py`) — the full, tested core. Profile, ranked feed, transparency screen, tracker, calendar export, stats, bias audit.
- **Web app** (`python webapp.py`) — a browser interface built on Python's standard-library `http.server` (no Flask, no installs). Two roles:
  - **Students** search and see ranked, explained matches.
  - **Organizers** post new opportunities that appear on the student side immediately.
  - Runs on your wifi, so anyone (a teacher, a judge) can open it on their phone.

---

## Features

- **Weighted, explainable scoring** — ranks by interest overlap, deadline urgency, and a transparent equity boost for free / beginner-friendly events. Every recommendation prints why it matched.
- **Transparency screen** — shows the full scoring formula with real numbers for any result. No black box.
- **Bias self-audit** (`fairness.py`) — runs the matcher across many synthetic students with and without the equity weighting and reports how much it widens access to free opportunities. Eberhardt's challenge, answered with measurement.
- **Recursive interest taxonomy** (`interests.py`) — broad interests like "Technology" expand recursively through a nested category tree to match every leaf interest at any depth.
- **Fuzzy interest matching** — uses the standard-library `difflib` so typos and near-synonyms still match.
- **Live demand map** (`demand.py`) — every search is logged anonymously (level + interests, no names). The opportunity-gap view is driven by real demand versus real supply, not guesses.
- **Two-role web app** (`webapp.py`) — student finder + organizer posting, sharing one live data store, with hand-written SVG charts.
- **Structured feed ingestion** (`feeds.py`, `import_feed.py`) — imports real opportunities from RSS / Atom feeds using only `urllib` + `xml.etree`. No brittle HTML scraping, no dependencies.
- **Persistent structured state via JSON File I/O** — opportunities, applications, and demand signals all persist as structured JSON.
- **Calendar export (.ics File I/O)** — generates real RFC-5545 calendar files (whole-tracker export in the CLI, single-event download in the web app).
- **Application tracker** — status, notes, deadline countdowns with urgency badges.
- **Shareable weekly digest** — generates a `weekly_digest.txt` formatted to paste into a class group chat.
- **First-timer guide** — explains each opportunity type to students who've never entered one.
- **Central input-validation gateway** (`validation.py`) — every input in both front-ends validates here. Unhandled crashes on bad input are impossible by design. Data files load crash-resistantly even if missing or corrupt.
- **Hand-rolled terminal polish** (`ui.py`) — ANSI colors, aligned tables, countdown badges, no libraries.
- **OOP throughout** — `Opportunity`, `Student`, `Application` classes; single-responsibility modules.
- **Zero external libraries** — 100% Python standard library. Every line is ours and explainable.

---

## How to Run

**Requirements:** Python 3. Nothing to install.

**Command-line app:**
```bash
python main.py
```

**Web app (student finder + organizer posting):**
```bash
python webapp.py
```
Then open `http://localhost:8000` in a browser. On the same wifi, others can open `http://<your-computer-ip>:8000` on their phones.

**Import opportunities from a live feed (optional):**
```bash
python import_feed.py <RSS-or-Atom-feed-URL>
```

**Run the tests:**
```bash
python -m unittest discover -s tests
```

---

## File Structure

```
bbb/
├── main.py            CLI entry point — menu loop wiring everything together
├── webapp.py          Web app (http.server) — student finder + organizer posting
├── import_feed.py     Runner: import opportunities from an RSS/Atom feed
│
├── matcher.py         Scoring engine: hard filter, weighted score, fuzzy match, explanations
├── models.py          Opportunity, Student, Application classes
├── validation.py      Central input gateway — interactive (CLI) and pure (web) checks
├── storage.py         Crash-resistant JSON load/save for opportunities and applications
├── interests.py       Recursive interest-taxonomy expansion
├── demand.py          Anonymous search logging and demand-vs-supply gap reporting
├── fairness.py        Bias self-audit: measures the equity weighting's effect
├── feeds.py           RSS/Atom feed parsing and conversion to opportunities
├── tracker.py         Application tracker: status, notes, deadline countdown
├── ics_export.py      RFC-5545 .ics calendar file generator
├── digest.py          Weekly digest text-file generator
├── stats.py           Opportunity-gap statistics: supply, ratio, unmet interests
├── firsttimer.py      First-timer guide for each opportunity type
├── ui.py              Hand-rolled ANSI terminal polish: colors, tables, badges
│
├── data/
│   ├── opportunities.json   Curated seed: 20 real Singapore student opportunities
│   ├── interests.json       Nested interest taxonomy tree (for recursive expansion)
│   ├── applications.json    Auto-created; persists tracked applications
│   └── searches.json        Auto-created; anonymous demand log
│
└── tests/                   54 unit tests across all modules
    ├── test_matcher.py      Scoring math, filters, equity ordering, fuzzy matching
    ├── test_validation.py   Input gateway: rejects junk, accepts valid input
    ├── test_tracker.py      Status transitions, persistence, countdown badges
    ├── test_ics.py          ICS wrapper structure and VEVENT generation
    ├── test_interests.py    Recursive expansion at every depth, deduplication
    ├── test_stats.py        Supply counts, free/paid ratio, unmet-interest detection
    ├── test_digest.py       Digest written, header present, top match included
    ├── test_demand.py       Search logging, demand aggregation, gap ranking
    ├── test_fairness.py     Free-share measurement and audit lift
    ├── test_feeds.py        RSS/Atom parsing, interest guessing, dedup merge
    └── test_webapp.py       Badges, SVG chart, posted-opportunity validation
```

---

## Reflection

**Hardest problem:** Designing a scoring algorithm that is simultaneously personalised, fair, and explainable. Early versions were either too opaque (a single number) or too crude (counting shared interests). The breakthrough was attaching human-readable reason strings to each score at the moment it is computed, so the explanation can never disagree with the ranking. We also refused to claim the matcher is "unbiased." Instead we built `fairness.py` to **measure** whether our equity weighting actually changes outcomes — turning a claim into a number.

**Second hardest:** Building a second interface without duplicating the engine. We kept `matcher.py`, `storage.py`, `models.py`, and `validation.py` as a shared core and added the web app as a thin layer on top. Getting the standard-library `http.server` to handle form posting, validation, and a live shared JSON store — so an organizer's post appears on the student side instantly — took careful routing, but it meant the CLI and the web app can never drift apart.

**If we had two more weeks:** Authenticated organizer accounts, a school-facing dashboard of the anonymised opportunity-gap data, and email/calendar deadline reminders. We'd also let opportunities be posted only after demand is proven, so the platform never suffers an empty-marketplace cold start.

---

## Tech Notes

- No external libraries anywhere. `pip install` is never required.
- File I/O uses `json`, `datetime`, plain text, and `.ics` generation — all standard library.
- The web app uses `http.server`; feed ingestion uses `urllib` + `xml.etree`.
- ANSI colors in `ui.py` have a TTY-detection fallback so piped output stays clean.
- Recursion lives in `interests.py`; its docstring explains why recursion is necessary.
- Run `python -m unittest discover -s tests` to execute all 54 tests.
