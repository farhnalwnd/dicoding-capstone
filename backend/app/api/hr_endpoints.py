from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.parser import extract_text, extract_candidate_name
from app.services.nlp import cluster_documents
from app.services.nlp import get_similarity_score


router = APIRouter()

@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general")
):
    candidates = []
    
    for cv in cvs:
        file_bytes = await cv.read()
        cv_text = extract_text(file_bytes, cv.filename)
        
        # Extract candidate name
        candidate_name = extract_candidate_name(cv_text, cv.filename)
        
        # Calculate similarity score
        similarity_score = get_similarity_score(cv_text, job_description)
        
        candidates.append({
            "name": candidate_name,
            "score": similarity_score,
            "filename": cv.filename
        })
    
    # Sort by score descending
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
