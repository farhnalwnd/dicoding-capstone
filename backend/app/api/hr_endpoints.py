import asyncio
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from bson import ObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
)
from pydantic import BaseModel, Field

from app.core.auth import require_role
from app.core.domain_loader import load_domain_config
from app.core.file_validation import sanitize_filename, validate_upload_file
from app.core.metrics import HR_RANKING_COUNT, REQUEST_COUNT, REQUEST_LATENCY
from app.core.mongodb import get_candidates_collection, log_activity
from app.services.nlp import (
    extract_jd_target_skills,
    get_similarity_score,
    has_skill_exact,
    match_cv_jd_hybrid,
)
from app.services.parser import clean_text, extract_candidate_name, extract_text
from app.services.progress import progress_manager

# --------------- Constants ---------------
MAX_PERCENTAGE = 100.0
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_BAD_REQUEST = 400
MAX_EXPERIENCE_YEARS = 10
JOB_TITLE_MAX_LENGTH = 100
_YEAR_PATTERN = re.compile(r"(\d+)\s*(?:\+\s*)?(?:years?|tahun|th)")

router = APIRouter()


class QuestionRequest(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]


def compute_candidate_score(
    semantic_score: float,
    matched_skills: list,
    missing_skills: list,
    cv_text: str,
    domain: str,
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
        (len(matched_skills) / total_skills) * MAX_PERCENTAGE
        if total_skills > 0
        else 0.0
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
            1 for s in all_domain_skills if has_skill_exact(s, cv_text)
        )
        domain_relevance = round(
            (cv_domain_hits / len(all_domain_skills)) * MAX_PERCENTAGE, 2
        )
    else:
        domain_relevance = 0.0

    final_score = round(
        (semantic_score * 0.70)
        + (effective_coverage * 0.10)
        + (domain_relevance * 0.20),
        2,
    )

    return final_score, round(coverage_ratio, 2), domain_relevance


def _process_single_candidate(
    cv_text: str,
    filename: str,
    jd_clean: str,
    domain: str,
    precomputed_target_skills,
    candidate_name: str,
) -> dict:
    """Score a single candidate CV against the cleaned job description."""
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
        domain=domain,
    )

    # Compute additional radar dimensions
    experience_depth, skill_breadth = _compute_radar_dimensions(
        cv_text, matched_skills, missing_skills
    )

    return {
        "name": candidate_name,
        "score": final_score,
        "semantic_score": semantic_score,
        "domain_skill_score": coverage_ratio,
        "domain_relevance": domain_relevance,
        "experience_depth": experience_depth,
        "skill_breadth": skill_breadth,
        "matched_skills_count": len(matched_skills),
        "missing_skills_count": len(missing_skills),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_scores": skill_scores,
        "domain": domain,
        "filename": filename,
    }


def _compute_radar_dimensions(
    cv_text: str, matched_skills: list, missing_skills: list
) -> tuple:
    """Compute experience depth and skill breadth radar dimensions."""
    # Experience Depth: heuristic based on years/experience mentions in CV
    year_mentions = _YEAR_PATTERN.findall(cv_text.lower())
    max_years = max([int(y) for y in year_mentions], default=0)
    experience_depth = min(
        MAX_PERCENTAGE, round((max_years / MAX_EXPERIENCE_YEARS) * MAX_PERCENTAGE, 2)
    )  # 10+ years = 100%

    # Skill Breadth: how many unique skills the candidate has relative to matched + missing
    total_skills = len(matched_skills) + len(missing_skills)
    skill_breadth = min(
        MAX_PERCENTAGE,
        round((len(matched_skills) / max(total_skills, 1)) * MAX_PERCENTAGE, 2),
    )
    return experience_depth, skill_breadth


def _extract_job_title(job_description: str) -> str:
    """Extract a job title from the first line of a job description."""
    first_line = job_description.strip().split("\n")[0].strip()
    job_title = (
        first_line[:JOB_TITLE_MAX_LENGTH]
        if len(first_line) > JOB_TITLE_MAX_LENGTH
        else first_line
    )
    return job_title if job_title else "Unknown Position"


def _save_ranked_candidates(candidates: list, job_title: str, log_fn=None):
    """Assign ranks, persist candidates to DB, and optionally log activity.

    Duplicate detection: a candidate is considered a duplicate if the same
    filename was already uploaded for the same job_title. Duplicates are
    skipped (not re-inserted) and the existing document ID is reused.
    """
    candidates_col = get_candidates_collection()
    for i, candidate in enumerate(candidates, start=1):
        candidate["rank"] = i

        # --- Duplicate detection ---
        existing = candidates_col.find_one(
            {"filename": candidate["filename"], "job_title": job_title}
        )
        if existing:
            # Reuse the existing record — do not insert a duplicate
            candidate["id"] = str(existing["_id"])
            candidate["duplicate"] = True
            continue
        # --------------------------

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
            "filename": candidate["filename"],
        }

        result = candidates_col.insert_one(candidate_doc)
        candidate["id"] = str(result.inserted_id)
        candidate["duplicate"] = False

        if log_fn:
            log_fn(candidate, job_title)


@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general"),
    current_user: dict = Depends(require_role("hr")),
):
    start_time = time.time()

    REQUEST_COUNT.labels(endpoint="hr_rank").inc()

    HR_RANKING_COUNT.inc()

    try:
        candidates = []

        # Clean job description to remove HTML tags, URLs, and noise
        jd_clean = clean_text(job_description)
        precomputed_target_skills = extract_jd_target_skills(jd_clean, domain)

        for cv in cvs:
            await asyncio.sleep(0.01)  # Yield to event loop to prevent blocking

            file_bytes = await cv.read()
            validate_upload_file(cv.filename, file_bytes)
            safe_filename = sanitize_filename(cv.filename)
            cv_text = extract_text(file_bytes, safe_filename)
            candidate_name = extract_candidate_name(cv_text, safe_filename, file_bytes)

            candidate = _process_single_candidate(
                cv_text,
                cv.filename,
                jd_clean,
                domain,
                precomputed_target_skills,
                candidate_name,
            )
            candidates.append(candidate)

        # Sort descending by score
        candidates.sort(key=lambda x: x["score"], reverse=True)

        job_title = _extract_job_title(job_description)

        # Add ranking and save to DB
        _save_ranked_candidates(candidates, job_title)

        return candidates

    finally:
        REQUEST_LATENCY.labels(endpoint="hr_rank").observe(time.time() - start_time)


# ==========================================
# Real-Time SSE endpoints & Background Workers
# ==========================================


def run_hr_rank_task(
    job_id: str, cv_files: List[Tuple[bytes, str]], job_description: str, domain: str
):
    try:
        progress_manager.update_progress(job_id, 10, "Parsing CVs")
        jd_clean = clean_text(job_description)
        precomputed_target_skills = extract_jd_target_skills(jd_clean, domain)

        # Keep file_bytes alongside cv_text so PyMuPDF name extraction can run
        parsed_cvs = []  # List of (cv_text, filename, file_bytes)
        for file_bytes, filename in cv_files:
            cv_text = extract_text(file_bytes, filename)
            parsed_cvs.append((cv_text, filename, file_bytes))
        time.sleep(0.3)

        progress_manager.update_progress(job_id, 30, "Extracting Skills")
        candidates = []
        for cv_text, filename, file_bytes in parsed_cvs:
            candidate_name = extract_candidate_name(cv_text, filename, file_bytes)
            candidate = _process_single_candidate(
                cv_text,
                filename,
                jd_clean,
                domain,
                precomputed_target_skills,
                candidate_name,
            )
            candidates.append(candidate)
        time.sleep(0.3)

        progress_manager.update_progress(job_id, 50, "Embedding Generation")
        time.sleep(0.3)

        progress_manager.update_progress(job_id, 75, "Ranking Candidates")
        candidates.sort(key=lambda x: x["score"], reverse=True)

        job_title = _extract_job_title(job_description)

        def _log_candidate_activity(candidate, title):
            log_activity(
                candidate_id=candidate["id"],
                candidate_name=candidate["name"],
                action="added",
                details=f"Candidate added from Bulk CV Ranking for position: {title}",
            )

        _save_ranked_candidates(candidates, job_title, log_fn=_log_candidate_activity)

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
    current_user: dict = Depends(require_role("hr")),
):
    REQUEST_COUNT.labels(endpoint="hr_rank_start").inc()
    HR_RANKING_COUNT.inc()

    cv_files = []
    for cv in cvs:
        await asyncio.sleep(0.01)
        file_bytes = await cv.read()
        validate_upload_file(cv.filename, file_bytes)
        safe_filename = sanitize_filename(cv.filename)
        cv_files.append((file_bytes, safe_filename))

    job_id = progress_manager.create_job()
    background_tasks.add_task(
        run_hr_rank_task, job_id, cv_files, job_description, domain
    )
    return {"job_id": job_id}


def _build_interview_questions(matched_skills: list, missing_skills: list) -> list:
    """Generate exactly 3 short, simple interview questions in Indonesian.

    Priority:
      - Q1: based on top matched skill (candidate's strength)
      - Q2: based on top missing skill (candidate's gap)
      - Q3: generic motivation / adaptability question
    Falls back to generic questions when skills lists are empty.
    """
    questions = []

    # Q1 — strength (matched skill)
    if matched_skills:
        skill = matched_skills[0]
        questions.append(
            f"Ceritakan pengalaman kamu menggunakan {skill} di pekerjaan atau proyek sebelumnya."
        )
    else:
        questions.append(
            "Ceritakan proyek atau pengalaman kerja yang paling relevan dengan posisi ini."
        )

    # Q2 — gap (missing skill)
    if missing_skills:
        skill = missing_skills[0]
        questions.append(
            f"Posisi ini membutuhkan {skill}. Bagaimana cara kamu mempelajari atau mengatasinya?"
        )
    else:
        questions.append(
            "Apa skill baru yang sedang kamu pelajari dan bagaimana cara kamu mempelajarinya?"
        )

    # Q3 — generic motivation / fit
    questions.append(
        "Mengapa kamu tertarik dengan posisi ini dan apa yang membuat kamu cocok untuk peran tersebut?"
    )

    return questions  # always exactly 3


@router.post("/hr/generate-questions")
async def generate_interview_questions(
    req: QuestionRequest, current_user: dict = Depends(require_role("hr"))
):
    questions = _build_interview_questions(req.matched_skills, req.missing_skills)
    return {"questions": questions}


class StatusUpdate(BaseModel):
    status: str = Field(
        ..., pattern="^(screening|talent_pool|interview|hired|rejected)$"
    )


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
    results = list(
        candidates_col.find({"status": "talent_pool"}).sort(
            [("match_score", -1), ("created_at", -1)]
        )
    )
    for r in results:
        r["id"] = str(r["_id"])
        del r["_id"]
    return results


@router.patch("/candidates/{id}/status")
async def update_candidate_status(
    id: str = Path(..., description="The ID of the candidate"),
    status_update: StatusUpdate = Body(...),
    current_user: dict = Depends(require_role("hr")),
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=HTTP_STATUS_BAD_REQUEST, detail="Invalid candidate ID format"
        )

    candidates_col = get_candidates_collection()
    candidate = candidates_col.find_one({"_id": obj_id})
    if not candidate:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Candidate not found"
        )

    candidates_col.update_one(
        {"_id": obj_id}, {"$set": {"status": status_update.status}}
    )

    log_activity(
        candidate_id=id,
        candidate_name=candidate.get("candidate_name", "Unknown"),
        action=status_update.status,
        details=f"Status updated from {candidate.get('status', 'unknown')} to {status_update.status}",
    )

    return {
        "status": "success",
        "message": f"Candidate status updated to {status_update.status}",
    }


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
        "hired": hired,
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
    current_user: dict = Depends(require_role("hr")),
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=HTTP_STATUS_BAD_REQUEST, detail="Invalid candidate ID format"
        )

    candidates_col = get_candidates_collection()
    candidate = candidates_col.find_one({"_id": obj_id, "status": "interview"})
    if not candidate:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail="Candidate not found or status is not 'interview'",
        )

    candidates_col.update_one(
        {"_id": obj_id, "status": "interview"},
        {
            "$set": {
                "interview_status": "scheduled",
                "interview_date": req.date,
                "interview_time": req.time,
                "meeting_link": req.meeting_link,
            }
        },
    )

    log_activity(
        candidate_id=id,
        candidate_name=candidate.get("candidate_name", "Unknown"),
        action="interview_scheduled",
        details=f"Interview scheduled for {req.date} at {req.time}. Meeting link: {req.meeting_link}",
    )

    return {"status": "success", "message": "Interview scheduled successfully"}


@router.post("/candidates/{id}/generate-questions")
async def generate_candidate_questions(
    id: str = Path(..., description="The ID of the candidate"),
    current_user: dict = Depends(require_role("hr")),
):
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=HTTP_STATUS_BAD_REQUEST, detail="Invalid candidate ID format"
        )

    candidates_col = get_candidates_collection()
    candidate = candidates_col.find_one({"_id": obj_id})
    if not candidate:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Candidate not found"
        )

    matched_skills = candidate.get("matched_skills", [])
    missing_skills = candidate.get("missing_skills", [])

    questions = _build_interview_questions(matched_skills, missing_skills)

    candidates_col.update_one(
        {"_id": obj_id}, {"$set": {"interview_questions": questions}}
    )

    return {"questions": questions}
