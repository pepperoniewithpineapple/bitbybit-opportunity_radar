# Pitch Day Script — 15 Minutes

**Format:** Pitch 3 min · Demo 7 min · Code Spotlight 3 min · Q&A 2 min
**Judges:** Jing An Tew (Stick'em, technical + education-access founder) · Chris Soh (Entrepreneurship lecturer) · Zhen Xian Kee (organiser, National Cybersecurity Olympiad @ NUS) · Yaojie Xiao (Co-founder, Dibs)

Assign one speaker per segment, or rotate. Rehearse the full 15 minutes out loud at least twice. Have the backup video ready in case the laptop misbehaves.

---

## Segment 1 — Pitch (3 min) · the problem

> "In Singapore, the problem isn't a lack of opportunities — hackathons, scholarships, olympiads, competitions exist. The problem is **access to knowing about them**. That information travels through privileged networks: elite schools, connected parents, plugged-in teachers. A student without that network simply never hears about the competition that could have changed their trajectory.
>
> Dr. Teo You Yenn calls this the *different starting lines* problem — advantage compounds for those who are already plugged in. And when platforms try to fix it with recommendation algorithms, Dr. Jennifer Eberhardt warns they often amplify the same bias — ranking on prestige and popularity, on who-you-know.
>
> So we built **Opportunity Radar**: a tool that aggregates opportunities in one place, and matches each student to the ones they qualify for — ranked **only** on their interests, their eligibility, and the deadline. It never sees your school or your background. And it shows its work: every recommendation explains *why* it matched. It's free, it runs entirely offline, and it's built by students, for students like us."

Keep it to 3 minutes. Don't oversell. Land the one sentence: **"the gap isn't opportunities — it's access to knowing about them."**

---

## Segment 2 — Demo (7 min) · THE STAR. Don't rush.

Run `python main.py`. Move slowly, narrate every step.

**Beat 1 — Load the demo student (10 sec).** Use the "Load demo student" option (don't type live — protects against fat-fingering). Profile appears: Wei Ming, JC, interests coding / AI / cybersecurity.

**Beat 2 — The For You feed (90 sec).** Show the ranked, explained feed. Point at one row:
> "Notice every result tells you *why* — matched interests with ticks, eligibility, a deadline countdown badge. No black box."
Point out that expired and ineligible opportunities are already filtered out.

**Beat 3 — The judge sees himself (30 sec).** Scroll to the **National Cybersecurity Olympiad** entry.
> "This is a real opportunity — the National Cybersecurity Olympiad at NUS, open to pre-university students, free. Exactly the kind of thing a student outside the right network never hears about. Our tool surfaced it automatically."
(Mr Zhen Xian Kee organises this. He is watching his own event get matched to a student who needs it.)

**Beat 4 — The transparency screen (60 sec).** Open the full scoring breakdown for one result. Show the raw formula and numbers.
> "This is the Eberhardt answer made literal. A student can always see the exact weights. We are **not** claiming the algorithm is neutral — we're claiming it's *honest*. We deliberately give a small lift to free and beginner-friendly opportunities, and you can see that weight right here. We tuned it to widen access, not to maximise engagement."

**Beat 5 — The opportunity-gap stats (45 sec).** Open the stats view. Show free-vs-paid ratio, deadline pressure, and the **unmet interests** — interests with few or no matching opportunities.
> "This near-empty line *is* the data. This is where the opportunity gap actually is — and it's the first thing a school or a funder would want to see."

**Beat 6 — Terminal reaches the real world (60 sec).** Add the NCO to the tracker, then export the `.ics` file. Open it / import to a phone calendar held up to the room (or show the QR / pre-recorded clip if no AirDrop).
> "A beginner Python program just put a real deadline into a real calendar on a real phone."

**Beat 7 — The torture test (60 sec).** This is what wins on the rubric. Go to any input and abuse it: press Enter on empty, type letters where a number is expected, type a nonsense date.
> "We assumed users would do their worst. Every single input in the entire app flows through one validation gateway. Nothing crashes — every error message is human."
(The brief says verbatim: *judges notice error handling.* This beat is worth real points.)

**Buffer:** ~30 sec spare. If short on time, cut Beat 5, never Beat 7.

---

## Segment 3 — Code Spotlight (3 min) · aimed at the CTO

Pick **`matcher.py` — the scoring function** (Jing An Tew is a software engineer; show him real logic).

Walk through, slowly:
1. The hard filter (eligibility + expired) — "we never rank something you can't enter."
2. The three weighted components — interest overlap, urgency, equity boost — and how they sum to one score.
3. The recursive interest-taxonomy expansion — "if you pick 'Technology', this function recurses through the category tree and matches every sub-interest under it, at any depth."
4. That each score carries its own list of human reasons — "the explanation isn't generated separately; it falls out of the same code that computes the score, so it can never lie about the ranking."

One sentence to close: **"No external libraries. Every line here is ours, and any of us can derive it on a whiteboard."**

---

## Segment 4 — Q&A (2 min) · anticipated questions + crisp answers

**Yaojie Xiao / Jing An Tew (algorithm fairness):** *"Your equity boost is itself a bias — how is that fair?"*
> "Agreed — it's not neutral, and we don't claim it is. Neutral ranking would just reproduce the existing advantage, because well-marketed elite-circuit events would always win. We made a deliberate, transparent choice to lift free and beginner-friendly opportunities, and every weight is visible on screen. The honesty is the feature."

**Jing An Tew (technical / scale):** *"JSON flat files won't scale."*
> "Correct, for a single-user CLI MVP they're perfect and crash-resistant. The migration path is SQLite — still standard library — then Postgres if it ever goes multi-user."

**Chris Soh (entrepreneurship):** *"Who are your first users and how do you reach them?"*
> "Our own JC cohort first. The shareable digest is built to be pasted into class group chats — the product spreads through exactly the peer networks it's trying to open up. Our one north-star metric is first-timer conversion: students who applied to their first-ever opportunity because of us."

**Chris Soh (marketplace skeptic):** *"Two-sided platforms die of cold start."*
> "Agreed — which is why this isn't a two-sided platform yet. It delivers value to a single student on day one with curated supply. We'd only let organisations post after we've proven there's demand."

**Zhen Xian Kee (reach / authenticity):** *"Does this actually reach disadvantaged students?"*
> "That's the whole point and also our hardest open problem. The tool is free and offline so cost and connectivity aren't barriers. Distribution is the unsolved part — honestly, that's where we'd spend the next two weeks."

**General (AI use):** *"Did you write this yourselves?"*
> "We used AI the way professionals do — to think and debug. Every module we can explain cold. Ask us about any file." (Then be able to do it.)

---

## Pre-flight checklist
- [ ] Confirm group size is allowed (brief max is 4 — ask a tutor).
- [ ] Public GitHub repo created, all teammates added as collaborators, link submitted to the Google Form **by Thu 19 June 23:59**.
- [ ] README.md complete and pushed.
- [ ] `python main.py` and `python -m unittest discover -s tests` both run clean on the demo laptop.
- [ ] Backup video of the full demo recorded (in case the laptop/internet fails).
- [ ] Demo rehearsed out loud twice, with each person's lines assigned.
