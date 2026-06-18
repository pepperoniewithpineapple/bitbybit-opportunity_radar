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
    - Upgrade personalisation algorithm
    - Decide whether to add feature to allow users to create applications to post opportunities

# 16/6/26: 6.25pm
- Added career_goals: list[str] to Student model and applied_for: list[OpportunityID]
- Added "I'm applying" button to opportunity cards that marks the application as applied
- TODO:
    - My Opportunities page (opportunities tracker)
        - Implement sorting (oldest, deadline passed) and state management (Applied, In Progress, Completed) in the tracker
    - My Portfolio page
        - Create schemas for VJC portal-style fields (Competitions, VIA, etc.)
        - Implement portfolio
        - Build the "My Portfolio" board layout
    - Update the web scraper to support dynamic opportunity types
    - Implement the personalisation algorithm and market intelligence features

# 18/6/26: 8.52pm
- Updated cordy scraper to find the opportunity types and interests
- Finished the personalisation algorithm
    - Uses Groq to get a summary of the user's profile based on the user's set profile and interactions
    - Then, uses TF-IDF to score the opportunities based on the profile summary
- Some UI changes, including showing the personalisation scoring when sorted by Recommended and shows the interests of the opportunities as 'Categories' tags in the opportunities