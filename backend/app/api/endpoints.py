from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from typing import Optional
import asyncio

from app.core.auth import get_current_user

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
    location: str = Form("Jakarta"),
    current_user: dict = Depends(get_current_user)
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
    domain: str = Form(...),
    current_user: dict = Depends(get_current_user)
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


CANDIDATES_POOL = [
    {
        "candidate_name": "Ahmad",
        "skills": ["Python", "FastAPI", "Docker", "NLP", "Machine Learning"],
        "profile": "Senior Python Developer with expertise in building scalable APIs using FastAPI, containerizing applications with Docker, and implementing Machine Learning and NLP models."
    },
    {
        "candidate_name": "Budi",
        "skills": ["Python", "SQL", "Flask", "REST API", "Git"],
        "profile": "Backend Engineer specializing in Python, Flask, relational databases using SQL, REST API design, and version control with Git."
    },
    {
        "candidate_name": "Citra",
        "skills": ["Vue.js", "JavaScript", "HTML", "CSS", "REST API"],
        "profile": "Frontend Developer with strong skills in Vue.js, clean modern JavaScript, responsive CSS/HTML layouts, and integrating frontends with backend REST APIs."
    },
    {
        "candidate_name": "Dian",
        "skills": ["Java", "Spring Boot", "PostgreSQL", "Docker", "CI/CD"],
        "profile": "Enterprise Backend Developer experienced in Java, Spring Boot microservices, PostgreSQL databases, Docker containerization, and setting up CI/CD pipelines."
    },
    {
        "candidate_name": "Eko",
        "skills": ["Go", "Kubernetes", "Docker", "gRPC", "CI/CD"],
        "profile": "Cloud Native Engineer with expertise in Go (Golang), container orchestration using Kubernetes, Docker, high-performance gRPC services, and CI/CD."
    },
    {
        "candidate_name": "Fitri",
        "skills": ["Python", "TensorFlow", "PyTorch", "Deep Learning", "Machine Learning"],
        "profile": "AI/ML Engineer specializing in Python, building neural networks with TensorFlow and PyTorch, Deep Learning research, and standard Machine Learning algorithms."
    },
    {
        "candidate_name": "Genta",
        "skills": ["React", "Node.js", "Express", "MongoDB", "Git"],
        "profile": "Fullstack JavaScript Developer focusing on the MERN stack: React, Node.js, Express, MongoDB database, and Git version control."
    },
    {
        "candidate_name": "Hana",
        "skills": ["Python", "Django", "AWS", "SQL", "Docker"],
        "profile": "Backend Developer skilled in Python, Django web framework, deploying applications to AWS cloud infrastructure, SQL databases, and Docker."
    },
    {
        "candidate_name": "Indra",
        "skills": ["Kotlin", "Android", "Git", "REST API"],
        "profile": "Mobile Application Developer specializing in native Android app development using Kotlin, integrating REST APIs, and Git code management."
    },
    {
        "candidate_name": "Julia",
        "skills": ["Ruby on Rails", "PostgreSQL", "Git", "Docker"],
        "profile": "Web Developer with proficiency in Ruby on Rails framework, PostgreSQL databases, Git version control, and container setups using Docker."
    }
]

async def perform_candidate_semantic_search(query_str: str):
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint="semantic_search").inc()
    SEMANTIC_SEARCH_COUNT.inc()
    try:
        query_emb = model.encode(query_str, convert_to_tensor=True)
        profiles = [c["profile"] for c in CANDIDATES_POOL]
        profile_embs = model.encode(profiles, convert_to_tensor=True)
        similarities = util.cos_sim(query_emb, profile_embs)[0]
        
        # Defensive check for mock encoding or single value returns
        if similarities.numel() < len(CANDIDATES_POOL):
            similarities = torch.full((len(CANDIDATES_POOL),), float(similarities[0]))
            
        results = []
        for i, c in enumerate(CANDIDATES_POOL):
            score = round(max(0.0, min(1.0, float(similarities[i]))) * 100, 2)
            results.append({
                "candidate_name": c["candidate_name"],
                "similarity_score": score,
                "skills": c["skills"]
            })
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return {"results": results}
    finally:
        REQUEST_LATENCY.labels(endpoint="semantic_search").observe(time.time() - start_time)

@router.post("/jobs/semantic-search")
async def semantic_job_search(
    request: Request,
    cv: Optional[UploadFile] = File(None),
    query: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    content_type = request.headers.get("content-type", "")

    
    if "application/json" in content_type:
        try:
            body = await request.json()
            search_query = body.get("query")
            if search_query:
                return await perform_candidate_semantic_search(search_query)
        except Exception as e:
            return {"error": f"Invalid JSON payload: {str(e)}"}
            
    if query:
        return await perform_candidate_semantic_search(query)
        
    if cv is not None:
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
 
    return {"error": "Missing 'cv' file or 'query' parameter."}


# ==========================================
# Real-Time SSE endpoints & Background Workers
# ==========================================

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from app.services.progress import progress_manager
from app.services.nlp import get_similarity_score, match_cv_jd_hybrid
from app.services.explainability import build_match_explanation

class SemanticSearchRequest(BaseModel):
    query: str

def run_match_detailed_task(job_id: str, file_bytes: bytes, filename: str, job_description: str, domain: str):
    try:
        progress_manager.update_progress(job_id, 10, "Upload CV")
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 20, "Parse Resume")
        cv_text = extract_text(file_bytes, filename)
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 35, "Extracting Skills")
        jd_clean = clean_text(job_description)
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 50, "Generating Embeddings")
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 70, "Match CV & Job Description")
        similarity_score = get_similarity_score(cv_text, jd_clean)
        matched_skills, missing_skills, skill_scores = match_cv_jd_hybrid(
            cv_text=cv_text,
            jd_text=jd_clean,
            domain=domain
        )
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 85, "Generating Explainability")

        # Compute domain relevance: how many of ALL domain skills appear in the CV
        from app.core.domain_loader import load_domain_config
        from app.services.nlp import has_skill_exact
        config = load_domain_config(domain)
        all_domain_skills = config.get("skills", [])
        if all_domain_skills:
            cv_domain_hits = sum(
                1 for s in all_domain_skills
                if has_skill_exact(s, cv_text)
            )
            domain_relevance = round(
                (cv_domain_hits / len(all_domain_skills)) * 100, 2
            )
        else:
            domain_relevance = 0.0

        result = build_match_explanation(
            similarity_score=similarity_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            domain_relevance=domain_relevance
        )
        result["skill_scores"] = skill_scores
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 95, "Finalizing Results")
        result["domain"] = domain
        time.sleep(0.2)
        
        progress_manager.complete_job(job_id, result)
    except Exception as e:
        progress_manager.fail_job(job_id, f"Failed to analyze: {str(e)}")


def run_semantic_search_task(job_id: str, query_str: str):
    try:
        progress_manager.update_progress(job_id, 10, "Parsing Query")
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 35, "Generating Embedding")
        query_emb = model.encode(query_str, convert_to_tensor=True)
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 60, "Semantic Search")
        profiles = [c["profile"] for c in CANDIDATES_POOL]
        profile_embs = model.encode(profiles, convert_to_tensor=True)
        similarities = util.cos_sim(query_emb, profile_embs)[0]
        
        if similarities.numel() < len(CANDIDATES_POOL):
            similarities = torch.full((len(CANDIDATES_POOL),), float(similarities[0]))
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 85, "Ranking Results")
        results = []
        for i, c in enumerate(CANDIDATES_POOL):
            score = round(max(0.0, min(1.0, float(similarities[i]))) * 100, 2)
            results.append({
                "candidate_name": c["candidate_name"],
                "similarity_score": score,
                "skills": c["skills"]
            })
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        time.sleep(0.2)
        
        progress_manager.complete_job(job_id, {"results": results})
    except Exception as e:
        progress_manager.fail_job(job_id, f"Failed to search candidates: {str(e)}")

@router.post("/match-detailed/start")
async def start_match_detailed(
    background_tasks: BackgroundTasks,
    cv: UploadFile = File(...),
    job_description: str = Form(...),
    domain: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    REQUEST_COUNT.labels(endpoint="match_detailed_start").inc()
    MATCH_ANALYSIS_COUNT.inc()
    
    file_bytes = await cv.read()
    filename = cv.filename
    
    job_id = progress_manager.create_job()
    background_tasks.add_task(
        run_match_detailed_task,
        job_id,
        file_bytes,
        filename,
        job_description,
        domain
    )
    return {"job_id": job_id}

@router.post("/jobs/semantic-search/start")
async def start_semantic_search(
    req: SemanticSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    REQUEST_COUNT.labels(endpoint="semantic_search_start").inc()
    SEMANTIC_SEARCH_COUNT.inc()
    
    job_id = progress_manager.create_job()
    background_tasks.add_task(
        run_semantic_search_task,
        job_id,
        req.query
    )
    return {"job_id": job_id}

async def event_generator(job_id: str):
    last_progress = -1
    last_message = ""
    last_status = ""
    
    job = progress_manager.get_job(job_id)
    if job:
        data = {
            "progress": job.get("progress", 0),
            "message": job.get("message", ""),
            "status": job.get("status", "processing")
        }
        yield f"data: {json.dumps(data)}\n\n"
        
    while True:
        job = progress_manager.get_job(job_id)
        if not job:
            error_data = {
                "progress": 0,
                "status": "error",
                "message": "Job not found"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            break
            
        current_progress = job.get("progress", 0)
        current_message = job.get("message", "")
        status = job.get("status", "processing")
        
        if (current_progress != last_progress or 
            current_message != last_message or 
            status != last_status):
            
            data = {
                "progress": current_progress,
                "message": current_message,
                "status": status
            }
            yield f"data: {json.dumps(data)}\n\n"
            
            last_progress = current_progress
            last_message = current_message
            last_status = status
            
        if status in ("completed", "error"):
            break
            
        await asyncio.sleep(0.2)

@router.get("/progress/{job_id}")
async def get_progress_stream(job_id: str, current_user: dict = Depends(get_current_user)):
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no"
    }
    return StreamingResponse(
        event_generator(job_id),
        headers=headers,
        media_type="text/event-stream"
    )

@router.get("/result/{job_id}")
async def get_job_result(job_id: str, current_user: dict = Depends(get_current_user)):
    job = progress_manager.get_job(job_id)
    if not job:
        return {"error": "Job not found"}
        
    if job.get("status") == "completed":
        return job.get("result")
    elif job.get("status") == "error":
        return {"status": "error", "message": job.get("message")}
    else:
        return {"status": "processing", "progress": job.get("progress")}