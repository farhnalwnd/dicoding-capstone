from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.parser import extract_text, extract_candidate_name, clean_text
from app.services.nlp import cluster_documents, get_similarity_score, match_cv_jd_hybrid

router = APIRouter()

@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general")
):
    candidates = []
    
    # Clean job description to remove HTML tags, URLs, and noise
    jd_clean = clean_text(job_description)
    
    for cv in cvs:
        file_bytes = await cv.read()
        cv_text = extract_text(file_bytes, cv.filename)
        candidate_name = extract_candidate_name(cv_text, cv.filename)
        semantic_score = get_similarity_score(cv_text, jd_clean)
        matched_skills, missing_skills = match_cv_jd_hybrid(cv_text, jd_clean, domain)
        total_target_skills = len(matched_skills) + len(missing_skills)
        domain_skill_score = (
            round((len(matched_skills) / total_target_skills) * 100, 2)
            if total_target_skills > 0
            else 0.0
        )
        final_score = round((semantic_score * 0.7) + (domain_skill_score * 0.3), 2)
        
        candidates.append({
            "name": candidate_name,
            "score": final_score,
            "semantic_score": semantic_score,
            "domain_skill_score": domain_skill_score,
            "matched_skills_count": len(matched_skills),
            "missing_skills_count": len(missing_skills),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "domain": domain,
            "filename": cv.filename
        })
    
    # Sort by bi-encoder score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Add rank
    for i, candidate in enumerate(candidates, 1):
        candidate["rank"] = i
            
    return candidates

@router.post("/hr/cluster")
async def cluster_candidates(
    cvs: List[UploadFile] = File(...),
    num_clusters: int = Form(3)
):
    texts = []
    filenames = []
    
    for cv in cvs:
        file_bytes = await cv.read()
        cv_text = extract_text(file_bytes, cv.filename)
        texts.append(cv_text)
        filenames.append(cv.filename)
        
    clusters = cluster_documents(texts, filenames, num_clusters)
    return clusters
