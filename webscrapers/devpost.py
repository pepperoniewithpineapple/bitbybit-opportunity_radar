"""
Web scraper for devpost.com/hackathons
-> returns Opportunity objects
"""
import time
import uuid
import datetime
import requests
from models import Opportunity


def parse_devpost_api_response(api_json: dict) -> list[Opportunity]:
    opportunities = []
    hackathons = api_json.get('hackathons', [])
    
    for idx, hackathon in enumerate(hackathons):
        title = hackathon.get('title', '').strip()
        if not title:
            continue
            
        #  Extract fields cleanly from JSON keys
        url = hackathon.get('public_url') or hackathon.get('url') or "https://devpost.com/hackathons"
        organiser = hackathon.get('organization_name') or hackathon.get('host') or "Devpost Host"
        organiser = organiser.strip()
        
        #  Calculate deadline from text descriptor (e.g., "5 days left")
        status_text = hackathon.get('submission_period_description', '').lower()
        today = datetime.date.today()
        if "day" in status_text:
            try:
                digits = [int(s) for s in status_text.split() if s.isdigit()]
                if digits:
                    deadline_date = today + datetime.timedelta(days=digits[0])
                    deadline = deadline_date.strftime("%Y-%m-%d")
                else:
                    deadline = (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            except Exception:
                deadline = (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        else:
            deadline = (today + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

        #  Gather theme tags
        interests = ["Hackathon", "Technology"]
        themes = hackathon.get('themes', [])
        for theme in themes:
            tag_name = theme.get('name', '').strip() if isinstance(theme, dict) else str(theme).strip()
            if tag_name and tag_name not in interests:
                interests.append(tag_name)
                
        opportunity = Opportunity(
            id=f"devpost_{str(uuid.uuid4())}",
            title=title,
            type="Hackathon",
            interests=interests,
            eligible_levels=["University", "Open"],
            beginner_friendly="beginner" in title.lower() or "student" in title.lower(),
            deadline=deadline,
            url=url,
            organiser=organiser
        )
        opportunities.append(opportunity)
        
    return opportunities


async def scrape_devpost() -> list[Opportunity]:
    #  Target the API endpoint directly
    api_url = "https://devpost.com/api/hackathons"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    all_scraped_opportunities: list[Opportunity] = []
    page = 1
    max_safety_pages = 20  #  Safeguard against infinite looping

    print("Querying Devpost native API pagination loop...")

    while page <= max_safety_pages:
        params = {
            "open_to[]": "public",
            "status[]": "open",
            "page": page
        }
        
        try:
            print(f"Fetching page {page}...")
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            api_data = response.json()
            hackathons_list = api_data.get('hackathons', [])
            
            #  Stop condition: If a page comes back empty, we've successfully reached the end of active listings
            if not hackathons_list:
                print(f"-> Page {page} returned 0 results. Reached the end of the live catalog.")
                break
                
            page_opportunities = parse_devpost_api_response(api_data)
            all_scraped_opportunities.extend(page_opportunities)
            
            print(f"Processed {len(page_opportunities)} hackathons from page {page}.")
            page += 1
            
            #  Polite rate-limiting delay between requests
            time.sleep(1.5)
            
        except requests.exceptions.RequestException as e:
            print(f"X Network issue or bad status code encountered on page {page}: {e}")
            break
        except ValueError:
            print("X Server response wasn't valid JSON formatting structure.")
            break

    print(f"\nSuccessfully captured a total of {len(all_scraped_opportunities)} hackathons.")
    return all_scraped_opportunities
    

if __name__ == "__main__":
    opportunities = scrape_devpost()
    if opportunities:
        print(f"\nSample payload from index array [Total entries: {len(opportunities)}]:")
        for idx, item in enumerate(opportunities[:3]):
            print(f"{idx+1}. {item.title} by {item.organiser} (Deadline: {item.deadline})")

    