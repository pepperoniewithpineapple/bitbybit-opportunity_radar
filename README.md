# Opportunity Radar

Opportunity Radar is a two-sided access system for Singapore students and opportunity organizers. Students discover opportunities and reveal anonymous demand. Organizers see where supply is missing, submit new opportunities, and use review safeguards before anything reaches the live student feed.

The core idea is simple: the gap is not always talent or effort. Often, the gap is who hears in time.

## Why This Matters

Dr. Teo You Yenn's work on inequality highlights how different starting lines compound over time. Dr. Jennifer Eberhardt's work on bias warns that technology can quietly reproduce unequal outcomes if its assumptions stay hidden.

Opportunity Radar responds by making the hidden layer visible. It does not claim neutrality. It ranks with transparent access weights for free and beginner-friendly opportunities, logs anonymous demand signals when students search, and gives senders a way to close the opportunity gap instead of guessing.

## Two Modes, One Engine

```text
Student searches -> anonymous demand signal -> sender sees gap -> sender submits opportunity -> reviewer approves -> student feed updates
```

Both modes share the same:

- `data/opportunities.json` opportunity store
- `matcher.py` scoring engine
- `validation.py` input gateway
- `storage.py` JSON File I/O helpers
- `models.py` classes
- `review_queue.py` approval gate for sender submissions

## Features

Opportunity Radar is organized into four layers rather than a pile of separate tools.

### Student Discovery

- Ranked, explained opportunity feed with cost/type/keyword/deadline filters.
- Closing-this-week view, match-improvement tips, first-timer guides, and opportunity-gap statistics.
- Application tracker, `.ics` calendar export, and shareable weekly digest.

### Sender Supply Loop

- Anonymous demand logging every time a student searches: level + interests + timestamp, no name.
- Demand gap radar so organizers can see where student interest is higher than current supply.
- Submission flow with impact preview, review queue, approval/rejection, live publishing, and announcement packet generation.

### Trust And Safety

- Transparent scoring breakdown for every recommendation.
- Invisible Starting-Line Simulation and bias self-audit to show how access assumptions affect rankings.
- Adaptive Naive Bayes spam-risk model, reviewer quality flags, and approval audit trail.
- Central validation gateway so bad input is handled gracefully.

### Advanced Intelligence

- Career impact simulator using weighted skill vectors and a sigmoid readiness curve.
- GraphRank hidden discovery using personalized PageRank-style graph ranking.
- Career pathway planner using `graphlib.TopologicalSorter`.
- Recursive interest taxonomy, optional SQLite FTS5 search index, pure-Python TF-IDF fallback, and RSS/Atom feed importer.
- Standard library only: no packages to install.

## How To Run

Requirements: Python 3.

```bash
python main.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Current verification: **130 unit tests pass**.

Optional feed import:

```bash
python import_feed.py <RSS-or-Atom-feed-URL>
```

## Menus

Top-level:

```text
1. Student / Opportunity Finder mode
2. Opportunity Sender mode
0. Quit
```

Student / Opportunity Finder mode:

```text
1. Profile
2. Discover opportunities
3. My applications and sharing
4. Equity and transparency lab
5. Career intelligence lab
6. Help and demo tools
0. Back to mode selection
```

Student features are grouped inside submenus:

```text
Discover opportunities:
1. View ranked + explained For You feed
2. Show full scoring breakdown
3. Closing this week

My applications and sharing:
1. Application tracker
2. Export tracker deadlines to .ics calendar
3. Generate shareable weekly digest

Equity and transparency lab:
1. Invisible starting-line simulation
2. Bias self-audit
3. Opportunity-gap statistics

Career intelligence lab:
1. Career impact simulator
2. Hidden opportunity graph discovery
3. Build my career pathway

Help and demo tools:
1. Load demo student
2. First-timer guide
```

Opportunity Sender mode:

```text
1. Demand gap radar
2. Submit a new opportunity for review
3. Review pending submissions
4. Live opportunities and announcements
5. Reviewer diagnostics
0. Back to mode selection
```

Sender support tools are grouped inside submenus:

```text
Live opportunities and announcements:
1. List live opportunities
2. Generate announcement for an opportunity

Reviewer diagnostics:
1. Model health and training audit
```

## File Structure

```text
bbb/
  main.py                 CLI entry point, two-mode routing, interactive flows
  career_model.py         ML-style career-readiness impact model
  spam_model.py           Trainable Naive Bayes spam-risk model
  graph_rank.py           Personalized graph-based hidden discovery
  pathway.py              Prerequisite-aware career pathway planner
  search_index.py         Optional SQLite FTS5 index with TF-IDF fallback
  review_queue.py         Pending submission approval workflow
  sender.py               Opportunity Sender mode helpers and announcements
  access.py               Invisible starting-line simulation
  matcher.py              Weighted scoring, filtering, explanations, urgent deadlines
  models.py               Opportunity, Student, and Application classes
  validation.py           Central input-validation gateway
  storage.py              Crash-resistant JSON load/save helpers
  interests.py            Recursive interest taxonomy expansion
  filters.py              Pure feed filtering and sorting helpers
  recommend.py            Interest suggestions to unlock more opportunities
  fairness.py             Bias/access self-audit against a neutral baseline
  stats.py                Opportunity-gap statistics and ASCII charts
  demand.py               Anonymous demand logging and demand-vs-supply gap rows
  tracker.py              Application tracker logic
  ics_export.py           RFC-5545 calendar export
  digest.py               Weekly digest text-file generator
  firsttimer.py           First-timer guides by opportunity type
  feeds.py                RSS/Atom parsing and opportunity conversion
  import_feed.py          Command-line feed import runner
  ui.py                   ANSI colors, aligned tables, countdown badges, bar charts

  data/
    opportunities.json    Curated seed and approved sender opportunities
    interests.json        Nested interest taxonomy
    student.json          Auto-created saved student profile
    searches.json         Auto-created anonymous student demand log
    submissions.json      Auto-created sender submission review queue

  tests/
    test_career_model.py  Career impact model tests
    test_spam_model.py    Trainable spam-risk model tests
    test_graph_rank.py    GraphRank discovery tests
    test_pathway.py       Career pathway planner tests
    test_search_index.py  SQLite/TF-IDF search index tests
    test_review_queue.py  Submission queue and approval tests
    test_sender.py        Sender mode helper tests
    test_access.py        Starting-line simulation tests
    test_matcher.py       Scoring, hard filters, equity ordering, fuzzy matching
    test_validation.py    Bad input rejection and valid input acceptance
    test_interests.py     Recursive taxonomy expansion
    test_filters.py       Feed filters and sorting
    test_recommend.py     Improve-your-match suggestions
    test_storage_student.py Student profile persistence
    test_tracker.py       Application tracker behavior
    test_ics.py           Calendar export structure
    test_digest.py        Weekly digest generation
    test_stats.py         Gap statistics
    test_fairness.py      Bias/access audit
    test_feeds.py         RSS/Atom parsing and deduplication
    test_demand.py        Demand log aggregation
```

## Code Spotlight

The strongest code spotlight uses four anchors: `matcher.py`, `access.py`, `sender.py` plus `review_queue.py`, and one advanced intelligence module such as `spam_model.py` or `graph_rank.py`.

`career_model.py` is the ML-style layer: it uses weighted skill vectors, a sigmoid readiness curve, event-type multipliers, and an opportunity-cost penalty to estimate whether one event increases, decreases, or does not change career-readiness alignment. It avoids fake hiring promises by reporting readiness movement, not real job probability.

`spam_model.py` is the second ML layer: it trains a Naive Bayes classifier from labeled legitimate/spam examples and real reviewer decisions, converts a submission into tokens, estimates spam probability, and shows the learned words that drove the risk score.

`graph_rank.py` is the hidden-discovery layer: it builds a graph across interests, careers, organizers, and opportunities, then runs personalized graph ranking to find bridge opportunities outside exact keyword matching.

`pathway.py` turns the career model into a sequence: foundation, practice, proof, and launch. It uses Python's `graphlib` so the order is validated by a real prerequisite graph.

`matcher.py` shows the concrete recommender:

```text
interest_score = shared_interests / max(1, student_interests) * 0.5
urgency_score  = (1 - clamp(days_left / 60, 0, 1)) * 0.2
equity_boost   = free boost + beginner-friendly boost
total          = interest_score + urgency_score + equity_boost
```

`access.py` makes the starting line visible: a strong opportunity can be a perfect fit and still be invisible if it travels through narrow information channels.

`sender.py` closes the loop: it turns anonymous student demand into organizer action and previews the likely access impact before anything is submitted.

`review_queue.py` is the deployment-hardening layer: it prevents unreviewed sender submissions from changing the live student feed, combines rule-based checks with the adaptive ML spam score, and keeps an approval/rejection audit trail using only JSON.

## Reflection

The hardest problem was making the project socially serious without turning the algorithm into a mysterious black box. The solution was to make every assumption visible: each recommendation carries its own reasons, the scoring screen prints the formula, the fairness audit compares a neutral baseline against the access-weighted ranking, and the starting-line simulation names exactly what it is estimating.

The second hardest problem was making the product feel two-sided and polished without needing a web server, database, or external package. The solution was to use structured JSON File I/O as the shared layer: student searches create demand records, senders read those records, submissions enter a review queue, and approved opportunities are published back into the same store.

With two more weeks, we would add reviewer accounts, a school-facing demand report, and a pilot with a real teacher or CCA lead. The student side would stay free.
