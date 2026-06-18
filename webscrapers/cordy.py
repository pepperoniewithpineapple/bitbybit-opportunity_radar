"""
Web scraper for app.cordy.sg
-> returns Opportunity objects
"""
import re
import time
import asyncio
import datetime
import requests
from bs4 import BeautifulSoup

from models import Opportunity


OPPORTUNITY_TYPE_PRIORITY = {
    "Competition": 10,
    "Internship": 10,
    "Volunteer": 10,
    "Conference": 8,
    "Seminar": 7,
    "Exhibition": 6,
    "Convention": 5,
    "Hackathon": 3,
    "Fellowship": 2,
    "Leadership Programme": 2,
    "Leadership": 2,
    "Mentorship": 2,
    "Workshop": 1,
    "Resource": 1,
    "Grant": 1,
}


seen_opportunities = set()


def parse_cordy_html_page(html_content: str, current_total: int) -> list[Opportunity]:
    """
    Parses a single HTML payload chunk from Cordy, utilizing regex-targeted 
    JSON hydration parsing alongside DOM selectors.
    """
    opportunities = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    if not opportunities:
        #  Finds in the <a> tag in the html for any opportunity labels 
        #  - e.g. href="/opportunities/illustration-arts-festival-iaf-2026"
        cards = soup.find_all('a', href=re.compile(r'/opportunities/[a-zA-Z0-9_-]+'))
        
        for idx, card in enumerate(cards):
            parent_container = card.find_parent('div', class_=re.compile(r'(group|relative)')) or card.parent #  Container of the card

            #  -- Title and organiser --
            title_node = parent_container.find('h2') #  Finding the label (i.e. the title) of the card
            if not title_node: #  Invalid
                continue
            
            title = title_node.get_text().strip()
            organiser = "CORDY Host"
            org_node = title_node.find_next('p')
            if org_node:
                organiser = org_node.get_text().strip()

            if f"{title}-{organiser}" in seen_opportunities:
                continue

            seen_opportunities.add(f"{title}-{organiser}")

            # -- Opportunity type & Interests --
            
            target_container = parent_container.select_one('div.md\:flex') #  Extract div containing types and interests
            #  In this container there are multiple spans:
            #  - spans with whitespace-nowrap contains the opportunity types
            #  - spans with an aria-label contains the interests in the aria-labels
            # print(target_container) #  DEBUG
            
            types = []
            interests = []
            # print(f"\n{title}: {organiser}") #  DEBUG
            
            #  Extract all types listed
            if target_container:
                #  Opportunity types
                type_nodes = target_container.find_all('span', class_=re.compile(r'whitespace-nowrap'))
                # print("type_nodes:", type_nodes) #  DEBUG
                for node in type_nodes:
                    if "/" in (node_type := node.get_text().strip()):
                        types.extend([t.strip() for t in node_type.split("/")])
                    else:
                        types.append(node_type)

                #  Sort types based on priority to label it as its main type
                types = sorted(types, key=lambda x: OPPORTUNITY_TYPE_PRIORITY.get(x, 0), reverse=True)

                #  Interests
                interest_nodes = target_container.find_all('span', attrs={"aria-label": True})
                for node in interest_nodes:
                    interest_text = node["aria-label"].strip()
                    if interest_text: #  Fail-safe if for some reason aria-label is empty
                        interests.append(interest_text)

            #  Cordy has a featured section that are duplicates and also appear different in the html so let's just exclude them
            if not types or not interests:
                continue
            # print("TYPES:", types) #  DEBUG
            # print("INTERESTS:", interests) #  DEBUG
            
            opportunity_type = types[0]
            # print("CHOSEN OPP TYPE:", opportunity_type) #  DEBUG
            
            #  -- Opportunity deadline --

            href = card.get('href', '')
            url = f"https://app.cordy.sg{href}" if href.startswith('/') else href

            date_node = parent_container.find(
                "p",
                string=re.compile(r'(\d+)\s+days?\s+left')
            )

            deadline_str = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            if date_node:
                match = re.search(r'(\d+)\s+days?\s+left', date_node.get_text(strip=True))
                if match:
                    days_left = int(match.group(1))
                    deadline_str = (datetime.date.today() + datetime.timedelta(days=days_left)).strftime("%Y-%m-%d")
            
            #  Consolidate
            opp = Opportunity(
                id=f"cordy-dom-{current_total + idx}",
                title=title,
                type=opportunity_type,
                interests=interests,
                eligible_levels=["Secondary", "JC", "Polytechnic", "University"],
                beginner_friendly=True,
                deadline=deadline_str,
                url=url,
                organiser=organiser
            )
            opportunities.append(opp)
            
    return opportunities


async def scrape_cordy() -> list[Opportunity]:
    """
    Loops sequentially through paginated parameters to extract all opportunities
    without triggering full selenium browser execution instances.
    """
    base_url = "https://app.cordy.sg/opportunities"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://app.cordy.sg/"
    }
    
    all_opportunities = []
    page = 1
    max_empty_pages = 1
    empty_page_count = 0
    
    print("Initializing complete Cordy multi-page data stream extraction...")
    
    while True:
        #  Append the specific index query argument targeting pagination nodes
        params = {"page": page}
        try:
            print(f"Requesting data matrix chunk from page {page}...")
            response = requests.get(base_url, headers=headers, params=params, timeout=12)
            
            #  If a page returns an error state or doesn't exist, we've broken the catalog barrier
            if response.status_code != 200:
                print(f"➔ Received status code {response.status_code}. Breaking iterator loop.")
                break
                
            response.raise_for_status()
            
            page_items = parse_cordy_html_page(response.text, len(all_opportunities))
            all_opportunities.extend(page_items)
            
            
            print(f"-> Processed page {page}. Discovered {len(page_items)} listings.")
            
            # If an entire step yields zero brand-new updates, terminate pagination safely
            if len(page_items) == 0:
                empty_page_count += 1
                if empty_page_count >= max_empty_pages:
                    print("-> No novel records discovered on recent sequences. Catalog extraction complete.")
                    break
            else:
                empty_page_count = 0
                
            page += 1
            time.sleep(1.2)  # Polite sleep gap to avoid tripping rate limiters
            
        except requests.exceptions.RequestException as e:
            print(f"X Connection sequence dropped on sequence page {page}: {e}")
            break
            
    print(f"\nCompilation complete. Aggregated {len(all_opportunities)} database rows from Cordy.")
    return all_opportunities

if __name__ == "__main__":
    catalog = asyncio.run(scrape_cordy())
    if catalog:
        print(f"\nSample payload from index array [Total entries: {len(catalog)}]:")
        for idx, item in enumerate(catalog[:10]):
            print(f"{idx+1}. {item.title} by {item.organiser} (Deadline: {item.deadline}, Type: {item.type}, Interests: {', '.join(item.interests)})")