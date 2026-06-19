# Opportunity Radar

Opportunity Radar is a Python + NiceGUI app that helps students find opportunities and consolidate their portfolio. It is built as a clean dashboard instead of a long terminal menu.
Note: This project is Singapore-based.

## Features
### Discover
Browse opportunities ranging from competitions, programs, events, and more, scraped from across the web.

Search opportunities via **TF-IDF search** to find opportunities catored to you.

Don't know what to search for? After browsing for a while, the system uses LLM and TF-IDF to recommend you opportunities it thinks you will be interested in - just sort by Recommeneded.

There's even a manual **Refresh** button to stay up to date with the opportunities out there.

Clicking "I'm Applying!" puts these opportunities in the **My Opportunities** page.

### My Opportunities
After labelling some opportunities as you're applying, they are consolidated in this tab, where you can see if you're trying too hard to portfolio farm and manage your time.

You can edit the status of these opportunities, whether it is Pending, Rejected, Ongoing or Completed.

Marking opportunities as Completed automatically brings them to the **My Portfolio** page.

### My Portfolio
My Portfolio isn't just a list. It is an easy board view to see all that you have done. This creates the Opportunity Radar pipeline:
```
[Browse] -> [Apply] -> [Send to Portfolio]
```

---

## Quick Start
**Python Version**: 3.12+

1. Download the files:
```
git clone https://github.com/pepperoniewithpineapple/bitbybit-opportunity_radar
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the app with `python main.py`

4. Edit your profile
Running the program should have opened a window with the app. If not, navigate to http://127.0.0.1:8000 in your browser. In the top right corner, click on Profile and edit your profile.

5. Start Browsing!

---