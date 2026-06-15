# 15/6/26: 8.28pm
OVERVIEW: Re did frontend and code structure, set up the basis of the project; just have to fill in the gaps.
- Redone UI, non-AI, clean and easier to read and use
- Split files up for better code comprehension
- Started devlog.md
- TODO: 
    - Take data from scrapers
    - Add database and implement sender code
    - Implement ML logic in display

# 16/6/26: 1.13am
OVERVIEW: Connected scraper to frontend, implemented search and sort.
- App initially boots up and fetches data from scraper
- Also checks if data is outdated on app open and fetches from scraper again
- Search algorithm from intelligence.py implemented
- Some sort options implemented
- Manual refresh button added to asynchronously fetch data from scrapers
- TODO:
    - Portfolio portion
    - Decide whether to add feature to allow users to create applications to post opportunities
