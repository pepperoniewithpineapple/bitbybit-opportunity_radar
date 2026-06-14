# Pitch Day Script - 15 Minutes

Format: Pitch 3 min, Demo 7 min, Code Spotlight 3 min, Q&A 2 min.

The demo should feel like one system becoming visible: a student reveals demand, the app reveals the access gap, a sender fills the gap, and review protects the live feed.

## Segment 1 - Pitch, 3 min

Open with:

> The gap is not a lack of opportunities. The gap is who hears in time.

Then:

> In Singapore, opportunities exist: hackathons, olympiads, scholarships, research attachments, workshops. But information about them travels through uneven networks: connected parents, plugged-in teachers, school chats, seniors, enrichment circles.
>
> Opportunity Radar is a two-sided access system. Students discover opportunities and reveal anonymous demand. Organizers see where opportunity supply is missing, submit opportunities, and review them before they become live. The ranking is transparent, because we do not want hidden assumptions deciding who gets seen.

Close:

> We are not claiming the algorithm is neutral. We make our assumptions visible, then measure whether they widen access.

## Segment 2 - Demo, 7 min

Run:

```bash
python main.py
```

### Beat 1 - Show the product shape, 20 sec

Point at the top-level menu:

```text
1. Student / Opportunity Finder mode
2. Opportunity Sender mode
```

Say:

> There are only two modes because the product loop is simple: students reveal demand, senders fill gaps.

### Beat 2 - Student creates demand, 75 sec

Choose `1` for Student / Opportunity Finder mode.

Choose `6` for Help and demo tools.

Choose `1` to load the demo student.

Choose `2` for Discover opportunities.

Choose `1` to view the ranked feed, then `0` to show results with default filters.

Say:

> Wei Ming is a JC student interested in coding, AI, and cybersecurity. When he searches, the app logs anonymous demand: level and interests only, no name, no school, no background.

Point to the ranked feed:

> The student sees eligible opportunities ranked by interest match, deadline urgency, and access weights for free and beginner-friendly opportunities.

### Beat 3 - The memorable access-gap moment, 90 sec

Back in Student mode, choose `4` for Equity and transparency lab.

Choose `1` for Invisible starting-line simulation.

Say:

> Same student. Same ability. Different information network.

Point at the before/after table.

> This is what we wanted to make visible. Before Radar, an outside-network student might hear about only a fraction of what they are eligible for. After Radar, the opportunity set becomes visible.

Land this line:

> The gap is not talent. The gap is who hears in time.

### Beat 4 - Sender closes the loop, 120 sec

Press `0` back to Student mode, then `0` back to mode selection.

Choose `2` for Opportunity Sender mode.

Choose `1` for Demand gap radar.

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

> The sender sees matching demand and an accessibility score before submitting. It does not become live yet, because a real product needs a gate before outside submissions reach students.

Confirm the submission.

Choose `3` to review pending submissions. Pick the new submission.

Say:

> The reviewer sees quality checks and the spam-risk layer inside the review flow. It is trust infrastructure, not a separate product.

Choose `approve`.

Say:

> Only after approval does the opportunity enter the live JSON store and become visible in Student Finder mode.

### Beat 5 - Transparency if time allows, 50 sec

Return to Student mode.

Choose `2` for Discover opportunities.

Choose `2` for scoring breakdown.

Say:

> The explanation is not generated after the fact. It comes from the same calculation that creates the score.

Point to:

```text
interest_score
urgency_score
equity_boost
total
```

## Segment 3 - Code Spotlight, 3 min

Do not tour every file. Show four anchors:

1. `matcher.py`: hard filters and transparent scoring.
2. `access.py`: starting-line simulation.
3. `sender.py` plus `review_queue.py`: demand to submission to approval.
4. One advanced depth module:
   - `spam_model.py`: adaptive Naive Bayes spam-risk classifier, or
   - `graph_rank.py`: PageRank-style hidden opportunity discovery.

Say:

> The advanced features are not random menu items. They are layers around one product loop: discovery, access transparency, sender supply, and trust.

Mention, without live-demoing:

- `career_model.py`: career-readiness impact model.
- `pathway.py`: prerequisite-aware career pathway planner.
- `search_index.py`: SQLite FTS5 search with TF-IDF fallback.
- `interests.py`: recursive taxonomy expansion.
- tracker, calendar export, digest, guides, and importer as polish.

Closing line:

> This project uses only standard-library Python: classes, dictionaries, File I/O, recursion, graph algorithms, statistics-style scoring, tests, and transparent logic. The impressive part is not a library. It is the model of the problem.

## Segment 4 - Q&A, 2 min

**Isn't the equity boost itself biased?**

Yes. We do not claim neutrality. We make a deliberate, visible access choice and measure its effect. Hidden bias is the problem; transparent weighting is the design.

**Why not use a web app or database?**

The brief rewards polished, explainable Python. We keep the product in Python and use JSON as the visible source of truth. The next standard-library step would be SQLite.

**Are the advanced features random extras?**

No. They are supporting layers. The core product loop is student demand to sender supply to reviewed publishing. GraphRank, career pathways, spam detection, and search make that loop smarter and safer.

**Does the career model predict jobs?**

No. It estimates readiness alignment, not actual hiring probability. That is intentional: the model is transparent and useful without pretending to know a student's future.

**Is the spam model real machine learning?**

Yes. It is a supervised Naive Bayes classifier trained from labeled examples and reviewer history. It produces a probability and learned signal words, then a human still makes the final decision.

**Is the graph discovery just keyword matching?**

No. It builds a typed graph and runs personalized graph ranking, so a student can discover bridge opportunities through related career skills and organizers even when the exact keyword match is weak.

**Did you write this yourselves?**

Every module is readable and explainable. Ask us about any file.

## Pre-Flight

- Run `python -m unittest discover -s tests`.
- Run `python main.py`.
- Rehearse the core arc: demo student, ranked feed, starting-line simulation, sender demand radar, submit, review, approve.
- Keep advanced features ready for Q&A, especially Career intelligence lab and Reviewer diagnostics.
- Prepare a backup screenshot or recording.
- Submit the public GitHub link by Thursday 19 June 2026, 23:59.
