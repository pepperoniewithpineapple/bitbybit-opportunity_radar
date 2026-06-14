# Pitch Day Script - 15 Minutes

Format: Pitch 3 min, Demo 7 min, Code Spotlight 3 min, Q&A 2 min.

The demo should feel like a hidden system becoming visible: students reveal demand, senders fill gaps, and the terminal proves the loop.

## Segment 1 - Pitch, 3 min

Open with:

> The gap is not a lack of opportunities. The gap is who hears in time.

Then:

> In Singapore, opportunities exist: hackathons, olympiads, scholarships, research attachments, workshops. But information about them travels through uneven networks: connected parents, plugged-in teachers, school chats, seniors, enrichment circles.
>
> Opportunity Radar has two modes. Students use Finder mode to discover and understand opportunities. Organizers use Sender mode to see demand gaps, submit opportunities, and review them before they become live. Same data store. Same scoring engine. No external libraries.

Close:

> We are not claiming the algorithm is neutral. We make our assumptions visible, then measure whether they widen access.

## Segment 2 - Demo, 7 min

Run:

```bash
python main.py
```

### Beat 1 - Show the two-mode product, 20 sec

Point at the top-level menu:

```text
1. Student / Opportunity Finder mode
2. Opportunity Sender mode
```

Say:

> This is not just a recommendation list. It is a tiny two-sided opportunity system with a review gate before new supply reaches students.

### Beat 2 - Student creates demand, 70 sec

Choose `1` for Student / Opportunity Finder mode.

Choose `9` to load demo student.

Choose `2` to view the feed, then `0` to show results with default filters.

Say:

> Wei Ming is a JC student interested in coding, AI, and cybersecurity. When he searches, the app logs anonymous demand: level and interests only, no name, no school, no background.

Point to the ranked feed:

> The student sees eligible opportunities ranked by interest match, deadline urgency, and transparent access weights.

### Beat 3 - The awe moment: invisible starting-line simulation, 80 sec

Choose `12`.

Say:

> Same student. Same ability. Different information network.

Point at the before/after table.

> This is what we wanted to make visible. Before Radar, an outside-network student might hear about only a fraction of what they are eligible for. After Radar, the opportunity set becomes visible.

Land this line:

> The gap is not talent. The gap is who hears in time.

### Beat 4 - Sender closes the loop, 90 sec

Press `0` to return to mode selection.

Choose `2` for Opportunity Sender mode.

Choose `1` to view demand gap radar.

Say:

> Now we switch perspectives. The sender does not guess what students need. They see demand against current supply.

Choose `2` to submit a new opportunity for review.

Suggested demo values:

```text
Title: JC AI for Public Good Sprint
Organizer: Demo School Innovation Lab
Type: workshop
Interests: AI, coding, public good
Eligible levels: 2
Cost: free
Beginner-friendly: yes
Deadline: 2026-08-20
URL: https://example.com/ai-public-good
```

At the impact preview, say:

> The sender sees matching demand and an accessibility score before submitting. It does not become live yet, because a deployed product needs a gate before outside submissions reach students.

Confirm the submission.

Then choose `3` to review pending submissions. Pick the new submission.

Say:

> The reviewer sees quality checks: duplicate title blockers, deadline risk, URL issues, access friction, and whether current demand actually matches the opportunity.

Choose `approve`.

Say:

> Only after approval does the opportunity enter the live JSON store and become visible in Student Finder mode. This is still pure Python, but it behaves more like a real product.

Mention that `opportunity_sender_packet.txt` is generated for a school or CCA chat after approval.

### Beat 5 - Transparency screen, 50 sec

Return to Student Finder mode, choose `3`, and open a result.

Say:

> The explanation is not generated after the fact. It comes from the same calculation that creates the score.

Point to:

```text
interest_score
urgency_score
equity_boost
total
```

### Beat 6 - Career impact simulator, 45 sec

Choose `13`.

Pick a career goal such as `cybersecurity analyst`, then choose the National Cybersecurity Olympiad or DSTA BrainHack result.

Say:

> This is the ML-style layer. It does not claim to predict a real job offer. It estimates whether this event increases, decreases, or does not change career-readiness alignment for a chosen goal.

Point at the before/after score and delta.

> The model uses weighted skill vectors, a sigmoid readiness curve, event-type multipliers, and an opportunity-cost penalty. The math is still explainable.

### Beat 7 - Bias self-audit, 30 sec

Choose `10`.

Say:

> We compare our access-weighted ranking against a neutral baseline. We do not just say the design widens access. We measure it.

### Beat 8 - Error handling, 25 sec

At any prompt, type bad input.

Say:

> Every input goes through one validation gateway. The app does not crash when a user behaves like a real user.

## Segment 3 - Code Spotlight, 3 min

Show:

1. `main.py`: two modes, one shared store.
2. `career_model.py`: ML-style career-readiness impact model.
3. `matcher.py`: hard filters and transparent scoring.
4. `access.py`: starting-line simulation.
5. `demand.py`: anonymous demand records.
6. `sender.py`: demand radar, submission drafting, impact preview, announcement generation.
7. `review_queue.py`: approval gate, quality flags, audit trail.
8. `interests.py`: recursive taxonomy expansion.

Closing line:

> This project uses only standard-library Python: classes, lists, dictionaries, File I/O, recursion, tests, and transparent logic. The impressive part is not a library. It is the model of the problem.

## Segment 4 - Q&A, 2 min

**Isn't the equity boost itself biased?**

Yes. We do not claim neutrality. We make a deliberate, visible access choice and measure its effect. Hidden bias is the problem; transparent weighting is the design.

**Why not use a web app or database?**

The brief rewards polished, explainable Python. We keep the product in Python and use JSON instead of adding a web layer. The review queue shows how deployment logic can still be modeled with standard-library Python. The next standard-library step would be SQLite.

**Does sender mode prove real organizers will post?**

No. It proves the product can connect student demand to organizer action. The next step is piloting it with real teachers, CCAs, or programme leads.

**Does the career model predict jobs?**

No. It estimates readiness alignment, not actual hiring probability. That is intentional: the model is transparent and useful without pretending to know a student's future.

**Did you write this yourselves?**

Every module is readable and explainable. Ask us about any file.

## Pre-Flight

- Run `python -m unittest discover -s tests`.
- Run `python main.py`.
- Rehearse both modes: student search, starting-line simulation, sender demand radar.
- Rehearse submitting and approving one demo opportunity.
- Prepare a backup screenshot or recording.
- Submit the public GitHub link by Thursday 19 June 2026, 23:59.
