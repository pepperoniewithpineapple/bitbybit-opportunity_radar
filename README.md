# Opportunity Radar

Opportunity Radar is a Python + NiceGUI app that helps students find opportunities and helps organizers submit better ones. It is built as a clean dashboard instead of a long terminal menu.

## What It Does

- **Student discovery:** profile-based ranking, transparent scoring, deadline filters, application tracking, weekly digest, and calendar export.
- **Sender supply loop:** demand gap radar, opportunity submission, manual review, live announcements, and duplicate/deadline checks.
- **Trust and safety:** adaptive spam-risk model trained from seed examples plus reviewer history before submissions reach manual review.
- **Advanced intelligence:** career impact simulator, graph-based hidden opportunity discovery, equity audit, and career pathway planner.

## How To Run

```bash
python -m pip install -r requirements.txt
python main.py
```

Then open:

```text
http://127.0.0.1:8080
```

## How To Test

```bash
python -m unittest discover -s tests
python -m py_compile main.py core.py intelligence.py tests/test_app.py
```

## File Structure

```text
main.py              NiceGUI interface
core.py              data, ranking, tracker, review workflow
intelligence.py      spam model, graph discovery, equity, career planning
tests/test_app.py    focused regression tests
data/                JSON source of truth
```

JSON stays as the main database. NiceGUI is the only app dependency.
