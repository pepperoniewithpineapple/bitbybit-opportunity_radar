# SPEC-MVP.md — Opportunity Radar (working name)

Python CLI. **Stdlib only** (`json`, `datetime`, `os`, `sys`, `unittest`). No external libraries — every line explainable by a beginner. Curated JSON data seed (no live scraping).

Graded for: **code quality + live pitch.** So the code must be clean and the demo must land.

---

## Social thesis (LOCKED framing — say it this way)

- **Teo You Yenn (inequality):** opportunities travel through privileged networks. We open-aggregate so access no longer depends on who you know.
- **Jennifer Eberhardt (bias):** the matcher is **interest-first and transparent** — every ranked result prints its reasons. We do **NOT** claim "unbiased." We claim: *"not neutral — honestly and visibly weighted toward access. You can see every weight."* This resolves the contradiction a sharp judge would catch.

## Scope

- **MVP-1 (build NOW):** student profile → ranked + explained opportunity feed. Runnable, testable, demoable.
- **MVP-2 (after MVP-1 works):** application tracker, `.ics` export, ANSI table/badge polish, weekly digest, stats view.
- **CUT / reframed:** live scraping → curated seed only. Data flywheel → instrumented but framed "designed, populates at scale," never faked live. Segment-map → dropped (so we CAN honestly claim "never sees your school").

## File layout

```
bbb/
  data/opportunities.json     # curated seed, ~15-20 real-ish SG opportunities
  models.py                   # Opportunity, Student, Application classes
  validation.py               # central input gateway (the "one hardened helper")
  storage.py                  # JSON load/save
  matcher.py                  # scoring + explanation + ranking
  main.py                     # menu loop wiring it together
  tests/test_matcher.py       # unittest
  tests/test_validation.py    # unittest
```

## Data model

- **Opportunity:** `id, title, type, interests[], eligible_levels[], cost("free"|"paid"), beginner_friendly(bool), deadline("YYYY-MM-DD"), url, organizer`
- **Student:** `name, level, interests[]`
- **Application:** `opp_id, status, notes` (MVP-2)

## Matcher — the whiteboard model (the real flex)

1. **Hard filter** out: ineligible (`student.level not in opp.eligible_levels`) and expired (`deadline < today`).
2. **Score** each surviving opportunity:
   - `interest_score = shared_interests / max(1, len(student.interests)) * 0.5`
   - `urgency_score  = (1 - clamp(days_left / 60, 0, 1)) * 0.2`  (sooner = higher, never negative)
   - `equity_boost   = (0.10 if free) + (0.05 if beginner_friendly)`
   - `total = interest_score + urgency_score + equity_boost`
3. **Rank** with stdlib `sorted(..., reverse=True)`. Hand-write the **scoring**, not the sort — reinventing sort is a negative signal to a real engineer; the model is the defensible part.
4. **Explain** every result: list of reason strings printed with badges, e.g.
   `Matched: AI, coding (✓✓ 2 shared) · open to JC (✓) · closes in 9 days (⚠) · free (+access)`

## Validation gateway (`validation.py`)

Every input in the whole app flows through here. Each loops until valid with a human error message:
- `get_valid_int(prompt, lo, hi)`
- `get_valid_choice(prompt, options)`
- `get_valid_date(prompt)`
- `nonempty(prompt)`

## Tests

- `test_matcher`: scoring math, eligibility filter drops ineligible/expired, ordering is correct, equity boost actually changes order.
- `test_validation`: rejects junk (letters for int, empty, bad date), accepts good input.

## Pitch reframes (LOCKED)

- **Equity:** "interest-first ranking with a transparent access weight — not neutral, honest."
- **Flywheel:** "instrumented; surfaces the gap at scale" — never fake live data in the demo.
- **Privacy:** MVP collects no school → we honestly claim "never sees your school." (That's why segment-map is cut.)
- **Sort:** hand-written *scoring function*, stdlib sort.
- **`.ics` demo:** fallback = QR code or pre-recorded clip, not AirDrop-only (AirDrop is Apple-only, dies on a strange projector).
- **Sustainability line:** civic infrastructure; later a B2B opportunity-gap dataset for schools funds the permanently-free student side.
- **Seeding judges' events:** seed several well-known real SG events so *someone* in the room connects — don't bet on one guessed judge.
