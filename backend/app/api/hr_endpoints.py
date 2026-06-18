from fastapi import APIRouter, UploadFile, File, Form, Body, BackgroundTasks, Depends, Path, HTTPException
from typing import List, Tuple, Dict, Any
from pydantic import BaseModel, Field
from app.core.auth import require_role
import time
import asyncio
from sentence_transformers import util
from bson import ObjectId
from datetime import datetime, timezone

from app.services.parser import extract_text, extract_candidate_name, clean_text
from app.services.nlp import (
    get_similarity_score,
    match_cv_jd_hybrid,
    extract_phrases,
    get_skill_embeddings_for_skills,
    model,
    has_skill_exact,
    extract_jd_target_skills
)
from app.core.domain_loader import load_domain_config
from app.core.mongodb import get_candidates_collection, log_activity
from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    HR_RANKING_COUNT
)
from app.services.progress import progress_manager


router = APIRouter()

class QuestionRequest(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]


def compute_candidate_score(
    semantic_score: float,
    matched_skills: list,
    missing_skills: list,
    cv_text: str,
    domain: str
) -> tuple:
    """
    Compute final match score using the same formula as build_match_explanation.
    Formula: 70% Semantic + 10% Coverage (reliability-adjusted) + 20% Domain Relevance

    Rules:
    - IT CV + IT JD  → highest score (domain relevance bonus)
    - IT CV + HR JD  → lower score  (0 domain relevance)
    - HR CV + IT JD  → lower score  (0 domain relevance for IT domain)
    - JDs with < 8 skills get a reliability penalty on coverage
    """
    total_skills = len(matched_skills) + len(missing_skills)
    coverage_ratio = (
        (len(matched_skills) / total_skills) * 100
        if total_skills > 0 else 0.0
    )

    # Skill reliability penalty: JDs with few skills get less coverage bonus
    MIN_RELIABLE_SKILLS = 8
    skill_reliability = min(1.0, total_skills / MIN_RELIABLE_SKILLS)
    effective_coverage = coverage_ratio * skill_reliability

    # Domain relevance: how many of ALL domain skills appear in the CV
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

    final_score = round(
        (semantic_score * 0.70)
        + (effective_coverage * 0.10)
        + (domain_relevance * 0.20),
        2
    )

    return final_score, round(coverage_ratio, 2), domain_relevance


@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general"),
    current_user: dict = Depends(require_role("hr"))
):
    start_time = time.time()

    REQUEST_COUNT.labels(
        endpoint="hr_rank"
    ).inc()

    HR_RANKING_COUNT.inc()

    try:
        candidates = []

        # Clean job description to remove HTML tags, URLs, and noise
        jd_clean = clean_text(job_description)
        precomputed_target_skills = extract_jd_target_skills(jd_clean, domain)

        for cv in cvs:
            await asyncio.sleep(0.01)  # Yield to event loop to prevent blocking

            file_bytes = await cv.read()
            cv_text = extract_text(file_bytes, cv.filename)
            candidate_name = extract_candidate_name(cv_text, cv.filename, file_bytes)

            semantic_score = get_similarity_score(cv_text, jd_clean)

            matched_skills, missing_skills, skill_scores = match_cv_jd_hybrid(
                cv_text, jd_clean, domain, precomputed_target_skills=precomputed_target_skills
            )

            # Use Tito's compute_candidate_score formula
            final_score, coverage_ratio, domain_relevance = compute_candidate_score(
                semantic_score=semantic_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                cv_text=cv_text,
                domain=domain
            )

            candidates.append({
                "name": candidate_name,
                "score": final_score,
                "semantic_score": semantic_score,
                "domain_skill_score": coverage_ratio,
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "skill_scores": skill_scores,
                "domain": domain,
                "filename": cv.filename
            })

        # Sort descending by score
        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # Job title from job_description
        first_line = job_description.strip().split('\n')[0].strip()
        job_title = first_line[:100] if len(first_line) > 100 else first_line
        if not job_title:
            job_title = "Unknown Position"

        # Add ranking and save to DB
        candidates_col = get_candidates_collection()
        for i, candidate in enumerate(
            candidates,
            start=1
        ):
            candidate["rank"] = i
            
            candidate_doc = {
                "candidate_name": candidate["name"],
                "match_score": candidate["score"],
                "job_title": job_title,
                "status": "screening",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "semantic_score": candidate["semantic_score"],
                "domain_skill_score": candidate["domain_skill_score"],
                "matched_skills_count": candidate["matched_skills_count"],
                "missing_skills_count": candidate["missing_skills_count"],
                "matched_skills": candidate["matched_skills"],
                "missing_skills": candidate["missing_skills"],
                "skill_scores": candidate["skill_scores"],
                "domain": candidate["domain"],
                "filename": candidate["filename"]
            }
            
            result = candidates_col.insert_one(candidate_doc)
            candidate["id"] = str(result.inserted_id)

        return candidates

    finally:
        REQUEST_LATENCY.labels(
            endpoint="hr_rank"
        ).observe(
            time.time() - start_time
        )



# ==========================================
# Real-Time SSE endpoints & Background Workers
# ==========================================

def run_hr_rank_task(job_id: str, cv_files: List[Tuple[bytes, str]], job_description: str, domain: str):
    try:
        progress_manager.update_progress(job_id, 10, "Parsing CVs")
        jd_clean = clean_text(job_description)
        precomputed_target_skills = extract_jd_target_skills(jd_clean, domain)
        
        parsed_cvs = []
        for file_bytes, filename in cv_files:
            cv_text = extract_text(file_bytes, filename)
            parsed_cvs.append((cv_text, filename))
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 30, "Extracting Skills")
        candidates = []
        for cv_text, filename in parsed_cvs:
            candidate_name = extract_candidate_name(cv_text, filename)
            semantic_score = get_similarity_score(cv_text, jd_clean)
            matched_skills, missing_skills, skill_scores = match_cv_jd_hybrid(
                cv_text, jd_clean, domain, precomputed_target_skills=precomputed_target_skills
            )

            final_score, coverage_ratio, domain_relevance = compute_candidate_score(
                semantic_score=semantic_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                cv_text=cv_text,
                domain=domain
            )

            candidates.append({
                "name": candidate_name,
                "score": final_score,
                "semantic_score": semantic_score,
                "domain_skill_score": coverage_ratio,
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "skill_scores": skill_scores,
                "domain": domain,
                "filename": filename
            })
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 50, "Embedding Generation")
        time.sleep(0.3)
        
        progress_manager.update_progress(job_id, 75, "Ranking Candidates")
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Job title from job_description
        first_line = job_description.strip().split('\n')[0].strip()
        job_title = first_line[:100] if len(first_line) > 100 else first_line
        if not job_title:
            job_title = "Unknown Position"

        candidates_col = get_candidates_collection()
        for i, candidate in enumerate(candidates, start=1):
            candidate["rank"] = i
            
            candidate_doc = {
                "candidate_name": candidate["name"],
                "match_score": candidate["score"],
                "job_title": job_title,
                "status": "screening",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "semantic_score": candidate["semantic_score"],
                "domain_skill_score": candidate["domain_skill_score"],
                "matched_skills_count": candidate["matched_skills_count"],
                "missing_skills_count": candidate["missing_skills_count"],
                "matched_skills": candidate["matched_skills"],
                "missing_skills": candidate["missing_skills"],
                "skill_scores": candidate["skill_scores"],
                "domain": candidate["domain"],
                "filename": candidate["filename"]
            }
            
            result = candidates_col.insert_one(candidate_doc)
            candidate["id"] = str(result.inserted_id)
            log_activity(
                candidate_id=candidate["id"],
                candidate_name=candidate["name"],
                action="added",
                details=f"Candidate added from Bulk CV Ranking for position: {job_title}"
            )

        time.sleep(0.2)
        progress_manager.complete_job(job_id, candidates)
    except Exception as e:
        progress_manager.fail_job(job_id, f"Failed to rank: {str(e)}")


@router.post("/hr/rank/start")
async def start_rank_candidates(
    background_tasks: BackgroundTasks,
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general"),
    current_user: dict = Depends(require_role("hr"))
):
    REQUEST_COUNT.labels(endpoint="hr_rank_start").inc()
    HR_RANKING_COUNT.inc()
    
    cv_files = []
    for cv in cvs:
        await asyncio.sleep(0.01)
        file_bytes = await cv.read()
        cv_files.append((file_bytes, cv.filename))
        
    job_id = progress_manager.create_job()
    background_tasks.add_task(
        run_hr_rank_task,
        job_id,
        cv_files,
        job_description,
        domain
    )
    return {"job_id": job_id}



@router.post("/hr/generate-questions")
async def generate_interview_questions(
    req: QuestionRequest,
    current_user: dict = Depends(require_role("hr"))
):
    questions = []
    
    for skill in req.matched_skills[:3]:
        questions.append(f"You have experience with {skill}. Can you describe a challenging project where you successfully utilized it?")
        questions.append(f"What were some of the common issues you faced when working with {skill}, and how did you resolve them?")
        
    for skill in req.missing_skills[:3]:
        questions.append(f"The role requires familiarity with {skill}, which isn't prominent in your CV. How would you approach learning or applying it?")
        questions.append(f"Have you worked with any technologies or concepts similar to {skill}?")
        
    if not questions:
        questions.append("Can you walk me through your most recent relevant project?")
        questions.append("How do you handle learning new technologies on the job?")
        
    return {"questions": questions}


class StatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(screening|talent_pool|interview|hired|rejected)$")


@router.get("/candidates", response_model=List[Dict[str, Any]])
async def get_candidates(current_user: dict = Depends(require_role("hr"))):
    candidates_col = get_candidates_collection()
    results = list(candidates_col.find().sort("created_at", -1))
    for r in results:
        r["id"] = str(r["_id"])
        del r["_id"]
    return results


@router.get("/talent-pool", response_model=List[Dict[str, Any]])
async def get_talent_pool(current_user: dict = Depends(require_role("hr"))):
    candidates_col = get_candidates_collection()
    results = list(candidates_col.find({"status": "talent_pool"}).sort([
        ("match_score", -1),
        ("created_at", -1)
    ]))
    for r in results:
        r["id"] = str(r["_id"])
        del r["_id"]
    return results


@router.patch("/candidates/{id}/status")
async def update_candidate_status(
    id: str = Path(..., description="The ID of the candidate"),
    status_update: StatusUpdate = Body(...),
    current_user: dict = Depends(require_role("hr"))
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")
        
    candidates_col = get_candidates_collection()
    candidate = candidates_col.find_one({"_id": obj_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    result = candidates_col.update_one(
        {"_id": obj_id},
        {"$set": {"status": status_update.status}}
    )
    
    log_activity(
        candidate_id=id,
        candidate_name=candidate.get("candidate_name", "Unknown"),
        action=status_update.status,
        details=f"Status updated from {candidate.get('status', 'unknown')} to {status_update.status}"
    )
    
    return {"status": "success", "message": f"Candidate status updated to {status_update.status}"}


@router.get("/dashboard/hr-stats")
async def get_hr_stats(current_user: dict = Depends(require_role("hr"))):
    candidates_col = get_candidates_collection()
    
    total = candidates_col.count_documents({})
    screening = candidates_col.count_documents({"status": "screening"})
    talent_pool = candidates_col.count_documents({"status": "talent_pool"})
    interview = candidates_col.count_documents({"status": "interview"})
    rejected = candidates_col.count_documents({"status": "rejected"})
    hired = candidates_col.count_documents({"status": "hired"})
    
    return {
        "total_candidates": total,
        "screening": screening,
        "talent_pool": talent_pool,
        "interview": interview,
        "rejected": rejected,
        "hired": hired
    }


class InterviewScheduleRequest(BaseModel):
    date: str = Field(..., example="2026-06-20")
    time: str = Field(..., example="10:00 AM")
    meeting_link: str = Field(..., example="https://meet.google.com/abc-defg-hij")


@router.get("/interviews", response_model=List[Dict[str, Any]])
async def get_interviews(current_user: dict = Depends(require_role("hr"))):
    candidates_col = get_candidates_collection()
    results = list(candidates_col.find({"status": "interview"}).sort("created_at", -1))
    for r in results:
        r["id"] = str(r["_id"])
        del r["_id"]
        if "interview_status" not in r:
            r["interview_status"] = "pending"
    return results


@router.post("/candidates/{id}/schedule")
async def schedule_candidate_interview(
    id: str = Path(..., description="The ID of the candidate"),
    req: InterviewScheduleRequest = Body(...),
    current_user: dict = Depends(require_role("hr"))
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")
        
    candidates_col = get_candidates_collection()
    candidate = candidates_col.find_one({"_id": obj_id, "status": "interview"})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found or status is not 'interview'")
        
    result = candidates_col.update_one(
        {"_id": obj_id, "status": "interview"},
        {
            "$set": {
                "interview_status": "scheduled",
                "interview_date": req.date,
                "interview_time": req.time,
                "meeting_link": req.meeting_link
            }
        }
    )
    
    log_activity(
        candidate_id=id,
        candidate_name=candidate.get("candidate_name", "Unknown"),
        action="interview_scheduled",
        details=f"Interview scheduled for {req.date} at {req.time}. Meeting link: {req.meeting_link}"
    )
    
    return {"status": "success", "message": "Interview scheduled successfully"}


@router.post("/candidates/{id}/generate-questions")
async def generate_candidate_questions(
    id: str = Path(..., description="The ID of the candidate"),
    current_user: dict = Depends(require_role("hr"))
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")
        
    candidates_col = get_candidates_collection()
    candidate = candidates_col.find_one({"_id": obj_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    matched_skills = candidate.get("matched_skills", [])
    missing_skills = candidate.get("missing_skills", [])
    
    questions = []
    for skill in matched_skills[:3]:
        questions.append(f"You have experience with {skill}. Can you describe a challenging project where you successfully utilized it?")
        questions.append(f"What were some of the common issues you faced when working with {skill}, and how did you resolve them?")
        
    for skill in missing_skills[:3]:
        questions.append(f"The role requires familiarity with {skill}, which isn't prominent in your CV. How would you approach learning or applying it?")
        questions.append(f"Have you worked with any technologies or concepts similar to {skill}?")
        
    if not questions:
        questions.append("Can you walk me through your most recent relevant project?")
        questions.append("How do you handle learning new technologies on the job?")
        
    candidates_col.update_one(
        {"_id": obj_id},
        {"$set": {"interview_questions": questions}}
    )
    
    return {"questions": questions}



