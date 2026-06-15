"""
Web scraper for app.cordy.sg
-> returns Opportunity objects
"""
import re
import json
import time
import datetime
import requests
from bs4 import BeautifulSoup

from models import Opportunity


def clean_json_string(raw_str: str) -> str:
    if not raw_str:
        return ""
    if raw_str.startswith("$n") or raw_str.startswith("$D"):
        raw_str = raw_str[2:]
    return raw_str.strip()


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

            title_node = parent_container.find('h2') #  Finding the label (i.e. the title) of the card
            if not title_node: #  Invalid
                continue
            
            title = title_node.get_text().strip()
            organizer = "CORDY Host"
            org_node = title_node.find_next('p')
            if org_node:
                organizer = org_node.get_text().strip()
            
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
            
            opp = Opportunity(
                id=f"cordy-dom-{current_total + idx}",
                title=title,
                type="Competition",
                interests=["Science & Tech"],
                eligible_levels=["Secondary", "JC", "Polytechnic", "University"],
                cost=0,
                beginner_friendly=True, #  TODO
                deadline=deadline_str,
                url=url,
                organizer=organizer
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
    seen_titles = set()
    page = 1
    max_empty_pages = 1
    empty_page_count = 0
    
    print("Initializing complete Cordy multi-page data stream extraction...")
    
    while True:
        # Append the specific index query argument targeting pagination nodes
        params = {"page": page}
        try:
            print(f"Requesting data matrix chunk from page {page}...")
            response = requests.get(base_url, headers=headers, params=params, timeout=12)
            
            # If a page returns an error state or doesn't exist, we've broken the catalog barrier
            if response.status_code != 200:
                print(f"➔ Received status code {response.status_code}. Breaking iterator loop.")
                break
                
            response.raise_for_status()
            
            page_items = parse_cordy_html_page(response.text, len(all_opportunities))
            
            # Filter and deduplicate items discovered in this specific pass loop
            new_items_found = 0
            for item in page_items:
                title_key = item.title.lower().strip()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_opportunities.append(item)
                    new_items_found += 1
            
            print(f"-> Processed page {page}. Discovered {len(page_items)} listings ({new_items_found} new records).")
            
            # If an entire step yields zero brand-new updates, terminate pagination safely
            if new_items_found == 0:
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
    catalog = scrape_cordy()
    if catalog:
        print(f"\nSample payload from index array [Total entries: {len(catalog)}]:")
        for idx, item in enumerate(catalog[:3]):
            print(f"{idx+1}. {item.title} by {item.organizer} (Deadline: {item.deadline})")