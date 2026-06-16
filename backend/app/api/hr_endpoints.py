from fastapi import APIRouter, UploadFile, File, Form, Body
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio
from app.services.parser import extract_text, extract_candidate_name, clean_text
import time
from app.services.nlp import cluster_documents, get_similarity_score, match_cv_jd_hybrid, extract_jd_target_skills

router = APIRouter()

class QuestionRequest(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]

@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general")
):
    start_total = time.time()
    candidates = []
    
    # Clean job description to remove HTML tags, URLs, and noise
    t0 = time.time()
    jd_clean = clean_text(job_description)
    precomputed_target_skills = extract_jd_target_skills(jd_clean, domain)
    t1 = time.time()
    print(f"[TIMING] JD Processing & Skill Extraction: {t1 - t0:.2f}s")
    print(f"[INFO] Target Skills found in JD: {precomputed_target_skills}")
    
    for cv in cvs:
        cv_start = time.time()
        await asyncio.sleep(0.01) # Yield to event loop to prevent blocking
        
        # 1. Read PDF
        t_read = time.time()
        file_bytes = await cv.read()
        filename = cv.filename
        cv_text = extract_text(file_bytes, filename)
        candidate_name = extract_candidate_name(cv_text, filename, file_bytes)
        t_extract = time.time()
        print(f"[TIMING] {filename} - PDF Extraction: {t_extract - t_read:.2f}s")
        
        # 2. Semantic Score (Bi-Encoder overall similarity)
        t_sem_start = time.time()
        semantic_score = get_similarity_score(cv_text, jd_clean)
        t_sem_end = time.time()
        print(f"[TIMING] {filename} - Bi-Encoder Overall Similarity: {t_sem_end - t_sem_start:.2f}s")
        
        # 3. Domain Skills Analysis (Hybrid Match)
        t_match_start = time.time()
        matched_skills, missing_skills, skill_scores = match_cv_jd_hybrid(
            cv_text, jd_clean, domain, precomputed_target_skills=precomputed_target_skills
        )
        t_match_end = time.time()
        print(f"[TIMING] {filename} - Domain Skills Hybrid Match: {t_match_end - t_match_start:.2f}s")
        
        total_target_skills = len(matched_skills) + len(missing_skills)
        domain_skill_score = (
            round((len(matched_skills) / total_target_skills) * 100, 2)
            if total_target_skills > 0
            else 0.0
        )
        final_score = round((semantic_score * 0.85) + (domain_skill_score * 0.15), 2)
        
        candidates.append({
            "name": candidate_name,
            "score": final_score,
            "semantic_score": semantic_score,
            "domain_skill_score": domain_skill_score,
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_scores": skill_scores,
            "domain": domain,
            "filename": filename
        })
        print(f"[TIMING] {filename} - Total Process Time: {time.time() - cv_start:.2f}s\n")
    
    # Sort by bi-encoder score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Add rank
    for i, candidate in enumerate(candidates, 1):
        candidate["rank"] = i
        
    print(f"[TIMING] Total /hr/rank Endpoint Execution Time: {time.time() - start_total:.2f}s")
            
    return candidates

@router.post("/hr/cluster")
async def cluster_candidates(
    cvs: List[UploadFile] = File(...),
    num_clusters: int = Form(3)
):
    texts = []
    filenames = []
    
    for cv in cvs:
        await asyncio.sleep(0.01)
        file_bytes = await cv.read()
        filename = cv.filename
        
        cv_text = extract_text(file_bytes, filename)
        texts.append(cv_text)
        filenames.append(filename)
        
    await asyncio.sleep(0.01)
    clusters = cluster_documents(texts, filenames, num_clusters)
    return clusters

@router.post("/hr/generate-questions")
async def generate_interview_questions(req: QuestionRequest):
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
