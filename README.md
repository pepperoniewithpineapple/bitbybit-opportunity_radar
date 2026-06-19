# Opportunity Radar

Opportunity Radar is a Python + NiceGUI app that helps students find opportunities and consolidate their portfolio. It is built as a clean dashboard instead of a long terminal menu.
Note: This project is Singapore-based.

---

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

3. Create a Groq API key at https://console.groq.com/keys
Create a file in the same directory as the code `.env` with the following contents:
```
GROQ_API_KEY={your_api_key}
```

4. Run the app with `python main.py`

5. Edit your profile
Navigate to http://127.0.0.1:8000 in your browser. In the top right corner, click on Profile and edit your profile.

6. Start Browsing!

---

## File Structure
```
.
├── data/
│   ├── certificates/
│   ├── my_opportunities.json
│   ├── opportunities.json
│   ├── portfolio.json
│   └── student.json
├── pages/
│   ├── applied_opportunity.py
│   ├── explore.py
│   └── portfolio.py
├── webscrapers/
│   ├── cordy.py
│   └── devpost.py
├── .gitignore
├── .last_pulled_timestamp
├── .env
├── intelligence.py
├── main.py
├── models.py
├── personalisation.py
├── README.md
├── requirements.txt
├── storage.py
└── theme.py
```

---

## Reflections
- The hardest problem we faced is learning. While we are proficient in Python itself, mixing with unfamiliar libraries like NiceGUI and LangChain made doing this project more difficult. Moreover, NiceGUI relies on Quasar and Tailwind CSS under the hood. So there was a lot of back-and-forth between documentation, and trying how we can use these things. 
    - Through patience reading documentation and a lot of searching, we slowly got the hang of it. This was also thanks to code examples and tutorials from other people online.

### Features Wishlist
If we had more time to do this project we would definitely like to add more features:
- Bookmarking opportunities
    - Right now, the state is Applying or Not applying. A way to bookmark pages and see them later would be fantastic for the UX. Moreover, this adds to our personalisation data collection, making the personalisation algorithm slightly more tuned.
- Filters
    - Unfortunately, this basic feature got cut due to time constraints. A search bar in combination with a filter (e.g., by type) would help users find the opportunities that suite them better.
- Posting Opportunities
    - If this were to be put into full production, there should be a system that allows organisations to submit requests to post opportunities on our platform. Currently, opportunities are just scraped from the web. This makes the selection of opportunities limited and hard to add on because we need to make a dedicated scraper.
- Career Viability Scoring
    - This would be a feature on the My Portfolio page that would look at the current job market and make a score of how good an opportunity is for the user's career path.
    - Users can then sort by this score and prioritise opportunities that are more likely to help them in their careers.

---

## How it works
- Search on Discover Page
    - This uses a TF-IDF algorithm to match user search queries with opportunities in our database. 
- Scrapers
    - The DevPost scraper uses the DevPost API to directly get the hackathon listings.
    - The Cordy scraper uses BeautifulSoup4 to get the information from the website.
- Personalisation algorithm
    - This uses Groq to get a personsalisation profile summary and then uses TF-IDF to match the user with opportunities. This provides a good mix of both understanding the user and matching them with relevant opportunities.
    
---