from fastapi import APIRouter, UploadFile, File, Form
from app.services.parser import extract_text, clean_text
from app.services.nlp import (
    analyze_cv_jd,
    model
)
from app.services.linkedin_scraper import scrape_linkedin_jobs
from app.core.mongodb import get_jobs_collection
from sentence_transformers import util
import torch
import time

from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    MATCH_ANALYSIS_COUNT,
    SEMANTIC_SEARCH_COUNT,
    SCRAPE_RECOMMEND_COUNT
)
router = APIRouter()
@router.post("/scrape-recommend")
async def scrape_and_recommend(
    time_range: str = Form("1w"),
    keyword: str = Form("Python Developer"),
    location: str = Form("Jakarta")
):
    start_time = time.time()

    REQUEST_COUNT.labels(
        endpoint="scrape_recommend"
    ).inc()
    SCRAPE_RECOMMEND_COUNT.inc()

    try:
        # Step 1: Scrape jobs
        scraped_count = scrape_linkedin_jobs(
            keyword,
            location,
            time_range
        )

        # Step 2: Get jobs from MongoDB
        jobs_collection = get_jobs_collection()

        jobs = list(
            jobs_collection.find(
                {
                    "keyword_searched": keyword,
                    "location": location
                }
            )
            .sort("scraped_at", -1)
            .limit(20)
        )

        job_results = []

        for job in jobs:

            job_results.append({
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "url": job["url"]
            })

        return {
            "scraped_count": scraped_count,
            "recommendations": job_results
        }

    finally:

        REQUEST_LATENCY.labels(
            endpoint="scrape_recommend"
        ).observe(
            time.time() - start_time
        )

@router.post("/match-detailed")
async def match_cv_to_job_detailed(
    cv: UploadFile = File(...),
    job_description: str = Form(...),
    domain: str = Form(...)
):
    start_time = time.time()

    REQUEST_COUNT.labels(
        endpoint="match_detailed"
    ).inc()

    MATCH_ANALYSIS_COUNT.inc()

    try:
        file_bytes = await cv.read()

        cv_text = extract_text(
            file_bytes,
            cv.filename
        )

        jd_clean = clean_text(
            job_description
        )

        result = analyze_cv_jd(
            cv_text=cv_text,
            jd_text=jd_clean,
            domain=domain
        )

        result["domain"] = domain

        return result

    finally:
        REQUEST_LATENCY.labels(
            endpoint="match_detailed"
        ).observe(
            time.time() - start_time
        )


@router.post("/jobs/semantic-search")
async def semantic_job_search(
    cv: UploadFile = File(...)
):
    start_time = time.time()

    REQUEST_COUNT.labels(
        endpoint="semantic_search"
    ).inc()

    SEMANTIC_SEARCH_COUNT.inc()

    try:

        file_bytes = await cv.read()
        cv_text = extract_text(file_bytes, cv.filename)

        query_emb = model.encode(
            cv_text,
            convert_to_tensor=True
        )

        jobs_collection = get_jobs_collection()

        jobs = list(
            jobs_collection.find(
                {
                    "description_embedding": {
                        "$exists": True
                    }
                }
            )
        )

        if not jobs:
            return []

        desc_embs = torch.tensor(
            [
                job["description_embedding"]
                for job in jobs
            ]
        )

        similarities = util.cos_sim(
            query_emb,
            desc_embs
        )[0]

        results = []

        for i, job in enumerate(jobs):

            score = round(
                max(
                    0.0,
                    min(
                        1.0,
                        float(similarities[i])
                    )
                ) * 100,
                2
            )

            results.append({
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "url": job["url"],
                "score": score
            })

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:10]

    finally:

        REQUEST_LATENCY.labels(
            endpoint="semantic_search"
        ).observe(
            time.time() - start_time
        )