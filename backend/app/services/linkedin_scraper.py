import requests
from bs4 import BeautifulSoup
import time
import random
import os
from pymongo import MongoClient
import urllib.parse

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.cv_matcher
jobs_collection = db.linkedin_jobs

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def scrape_linkedin_jobs(keyword: str, location: str):
    print(f"Scraping jobs for {keyword} in {location}...")
    encoded_keyword = urllib.parse.quote(keyword)
    encoded_location = urllib.parse.quote(location)
    
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_keyword}&location={encoded_location}&start=0"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all("li")
        
        scraped_count = 0
        for card in job_cards:
            try:
                title_elem = card.find("h3", class_="base-search-card__title")
                company_elem = card.find("h4", class_="base-search-card__subtitle")
                location_elem = card.find("span", class_="job-search-card__location")
                url_elem = card.find("a", class_="base-card__full-link")
                
                if not all([title_elem, company_elem, location_elem, url_elem]):
                    continue
                    
                title = title_elem.text.strip()
                company = company_elem.text.strip()
                loc = location_elem.text.strip()
                job_url = url_elem["href"].split("?")[0] # clean URL
                
                job_data = {
                    "title": title,
                    "company": company,
                    "location": loc,
                    "url": job_url,
                    "keyword_searched": keyword,
                    "scraped_at": time.time()
                }
                
                # Upsert based on URL to prevent duplicates
                jobs_collection.update_one(
                    {"url": job_url},
                    {"$set": job_data},
                    upsert=True
                )
                scraped_count += 1
                
            except Exception as e:
                print(f"Error parsing card: {e}")
                continue
                
        print(f"Successfully scraped and stored {scraped_count} jobs.")
        time.sleep(random.uniform(2, 5)) # Polite scraping
        return scraped_count
        
    except Exception as e:
        print(f"Scraping failed: {e}")
        return 0

if __name__ == "__main__":
    scrape_linkedin_jobs("Software Engineering", "indonesia")
