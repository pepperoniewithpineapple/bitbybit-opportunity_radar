# Opportunity Radar

Opportunity Radar is a two-mode terminal Python product for Singapore students and opportunity organizers. Students use **Student / Opportunity Finder mode** to discover hackathons, olympiads, scholarships, workshops, and programmes they might never hear about through ordinary networks. Organizers use **Opportunity Sender mode** to see demand gaps and submit new opportunities into a review queue before they reach the live student feed.

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
- `spam_model.py` trainable ML spam-risk layer

## Features

- **Student / Opportunity Finder mode**: ranked, explained opportunity feed for a student profile.
- **Opportunity Sender mode**: organizer-facing flow for viewing demand gaps, submitting new opportunities, reviewing pending submissions, listing live supply, and generating a student-facing announcement.
- **Demand gap radar**: every student feed search writes an anonymous demand signal: level + interests + timestamp, no name.
- **Sender impact preview**: before submitting, organizers see matching demand, deadline pressure, eligible levels, and an accessibility score.
- **Trainable ML spam-risk layer**: a standard-library Naive Bayes classifier trains on labeled examples, then scores each submission before manual review.
- **Submission review queue**: sender submissions are saved as pending records in `data/submissions.json`; they do not appear for students until approved.
- **Reviewer quality checks**: the queue flags duplicate titles, closed or urgent deadlines, weak URLs, access friction, spam risk, and submissions with no current demand match.
- **Explainable spam signals**: high-risk submissions show the learned tokens that pushed the model toward spam, such as prize, guaranteed, crypto, or click.
- **Approval audit trail**: approved and rejected submissions keep status, review time, and reviewer notes, which is closer to how a deployed product would protect the live feed.
- **Career impact simulator**: a transparent ML-style model estimates whether joining a specific event increases, decreases, or does not change a student's career-readiness alignment for a chosen goal.
- **Invisible Starting-Line Simulation**: estimates how many suitable opportunities the same student might hear about through different information networks, then shows what Radar recovers.
- **Transparent scoring breakdown**: shows the exact formula and numbers behind any recommendation.
- **Bias self-audit**: compares rankings with and without the access boost and reports the measured lift toward free opportunities.
- **Recursive interest taxonomy**: broad interests like `Technology` expand into deeper leaf interests such as `algorithms`, `machine learning`, and `cybersecurity`.
- **Advanced feed controls**: filter by cost, type, keyword, deadline window, and sort by score, deadline, or title.
- **Improve-your-match suggestions**: recommends interests that would unlock more eligible opportunities.
- **Application tracker**: saves status and notes for opportunities the student wants to pursue.
- **Calendar export**: writes a real `.ics` file for tracked deadlines.
- **Shareable weekly digest**: writes `weekly_digest.txt`, formatted for a class group chat.
- **Sender announcement packet**: writes `opportunity_sender_packet.txt`, formatted for school or CCA chats.
- **Opportunity-gap statistics**: shows supply by interest, free-vs-paid ratio, deadline pressure, and thin-supply interests using ASCII charts.
- **First-timer guides**: explains what to expect for hackathons, competitions, scholarships, workshops, and olympiads.
- **Structured feed importer**: optionally imports RSS or Atom feeds using only `urllib` and `xml.etree`.
- **Central validation gateway**: all interactive input goes through `validation.py`, so bad input is handled gracefully.
- **Standard library only**: no packages to install. Every line can be explained from Python basics.

## How To Run

Requirements: Python 3.

```bash
python main.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Current verification: **116 unit tests pass**.

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
1.  Set/edit student profile
2.  View ranked + explained For You feed
3.  Show full scoring breakdown (transparency screen)
4.  Application tracker
5.  Export tracker deadlines to .ics calendar
6.  First-timer guide
7.  Opportunity-gap statistics
8.  Generate shareable weekly digest
9.  Load demo student (quick-start for demo)
10. Bias self-audit (does the equity weighting work?)
11. Closing this week (urgent deadlines)
12. Invisible starting-line simulation
13. Career impact simulator
0.  Back to mode selection
```

Opportunity Sender mode:

```text
1. View demand gap radar
2. Submit a new opportunity for review
3. Review pending submissions
4. List live opportunities
5. Generate announcement for an opportunity
0. Back to mode selection
```

## File Structure

```text
bbb/
  main.py                 CLI entry point, two-mode routing, interactive flows
  career_model.py         ML-style career-readiness impact model
  spam_model.py           Trainable Naive Bayes spam-risk model
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

The best code spotlight is `career_model.py`, `spam_model.py`, `matcher.py`, `access.py`, `sender.py`, and `review_queue.py`.

`career_model.py` is the ML-style layer: it uses weighted skill vectors, a sigmoid readiness curve, event-type multipliers, and an opportunity-cost penalty to estimate whether one event increases, decreases, or does not change career-readiness alignment. It avoids fake hiring promises by reporting readiness movement, not real job probability.

`spam_model.py` is the second ML layer: it trains a Naive Bayes classifier from labeled legitimate/spam examples, converts a submission into tokens, estimates spam probability, and shows the learned words that drove the risk score.

`matcher.py` shows the concrete recommender:

```text
interest_score = shared_interests / max(1, student_interests) * 0.5
urgency_score  = (1 - clamp(days_left / 60, 0, 1)) * 0.2
equity_boost   = free boost + beginner-friendly boost
total          = interest_score + urgency_score + equity_boost
```

`access.py` makes the starting line visible: a strong opportunity can be a perfect fit and still be invisible if it travels through narrow information channels.

`sender.py` closes the loop: it turns anonymous student demand into organizer action and previews the likely access impact before anything is submitted.

`review_queue.py` is the deployment-hardening layer: it prevents unreviewed sender submissions from changing the live student feed, combines rule-based checks with the ML spam score, and keeps an approval/rejection audit trail using only JSON.

## Reflection

The hardest problem was making the project socially serious without turning the algorithm into a mysterious black box. The solution was to make every assumption visible: each recommendation carries its own reasons, the scoring screen prints the formula, the fairness audit compares a neutral baseline against the access-weighted ranking, and the starting-line simulation names exactly what it is estimating.

The second hardest problem was making the product feel two-sided and polished without needing a web server, database, or external package. The solution was to use structured JSON File I/O as the shared layer: student searches create demand records, senders read those records, submissions enter a review queue, and approved opportunities are published back into the same store.

With two more weeks, we would add reviewer accounts, a school-facing demand report, and a pilot with a real teacher or CCA lead. The student side would stay free.
