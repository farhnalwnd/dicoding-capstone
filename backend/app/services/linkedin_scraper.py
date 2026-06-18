import random
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

from app.core.mongodb import get_jobs_collection as _get_jobs_collection

# Collection will be fetched lazily inside the function

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",  # noqa: E501
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

_model = None


def get_model():
    global _model
    if _model is None:
        try:
            # Share the model instance if imported inside the app to save memory
            from app.services.nlp import model as app_model

            _model = app_model
        except ImportError:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def scrape_job_description(job_url: str) -> str:
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",  # noqa: E501
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(job_url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            desc_elem = soup.find(
                "div", class_="show-more-less-html__markup"
            ) or soup.find("section", class_="description")
            if desc_elem:
                return desc_elem.text.strip()
    except Exception as e:
        print(f"Failed to fetch job description: {e}")
    return ""


def scrape_linkedin_jobs(keyword: str, location: str, time_range: str = "1w"):
    print(f"Scraping jobs for {keyword} in {location} with time range {time_range}...")
    encoded_keyword = urllib.parse.quote(keyword)
    encoded_location = urllib.parse.quote(location)

    tpr_map = {"1w": "r604800", "1m": "r2592000", "2m": "r5184000", "3m": "r7776000"}
    f_tpr = tpr_map.get(time_range, "r604800")

    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={encoded_keyword}&location={encoded_location}&f_TPR={f_tpr}&start=0"  # noqa: E501

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",  # noqa: E501
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("li")

        scraped_count = 0
        model = get_model()

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
                job_url = url_elem["href"].split("?")[0]  # clean URL

                # Fetch detailed job description with random politeness sleep
                time.sleep(random.uniform(1, 2))
                description = scrape_job_description(job_url)

                if not description:
                    # Fallback description
                    description = f"Looking for a qualified {title} to join {company} in {loc}. The ideal candidate has experience in software development, team collaboration, and relevant industry skills."  # noqa: E501

                # Clean job description before encoding to keep embeddings clean
                from app.services.parser import clean_text

                cleaned_desc = clean_text(description)

                # Generate dynamic description embedding for vector search
                description_embedding = model.encode(cleaned_desc).tolist()

                job_data = {
                    "title": title,
                    "company": company,
                    "location": loc,
                    "url": job_url,
                    "description": description,
                    "description_embedding": description_embedding,
                    "keyword_searched": keyword,
                    "time_range": time_range,
                    "scraped_at": time.time(),
                }

                # Upsert based on URL to prevent duplicates
                jobs_collection = _get_jobs_collection()
                jobs_collection.update_one(
                    {"url": job_url}, {"$set": job_data}, upsert=True
                )
                scraped_count += 1

            except Exception as e:
                print(f"Error parsing card: {e}")
                continue

        print(f"Successfully scraped and stored {scraped_count} jobs.")
        return scraped_count

    except Exception as e:
        print(f"Scraping failed: {e}")
        return 0


if __name__ == "__main__":
    scrape_linkedin_jobs("Python Developer", "Jakarta", "1w")
