from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.parser import extract_text, extract_candidate_name
from app.services.nlp import cluster_documents, get_similarity_score, rerank_with_cross_encoder

router = APIRouter()

@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general"),
    use_cross_encoder: bool = Form(False)
):
    candidates = []
    
    for cv in cvs:
        file_bytes = await cv.read()
        cv_text = extract_text(file_bytes, cv.filename)
        candidate_name = extract_candidate_name(cv_text, cv.filename)
        similarity_score = get_similarity_score(cv_text, job_description)
        
        candidates.append({
            "name": candidate_name,
            "score": similarity_score,
            "filename": cv.filename,
            "cv_text": cv_text  # store for cross-encoder
        })
    
    if use_cross_encoder:
        # Re-rank using Cross-Encoder
        # Construct candidate dicts matching expected structure in rerank_with_cross_encoder
        formatted_candidates = [
            {"name": c["name"], "score": c["score"], "filename": c["filename"], "description": job_description}
            for c in candidates
        ]
        
        # Use the first candidate's CV text (or map correctly)
        # Wait, rerank_with_cross_encoder expects (cv_text, candidates_list) where candidates_list has descriptions.
        # But we want to compare each CV to the same JD!
        # Let's write a loop or fix the helper.
        # In our case, we have ONE JD and MULTIPLE CVs.
        # So we want pairs: [(cv_text_1, JD), (cv_text_2, JD), ...]
        # Let's compute Cross-Encoder scores for all CVs.
        from app.services.nlp import cross_encoder
        if cross_encoder:
            try:
                pairs = [[c["cv_text"], job_description] for c in candidates]
                scores = cross_encoder.predict(pairs)
                for i, score in enumerate(scores):
                    # CrossEncoder outputs single logits. We convert to 0-100 range.
                    # Typically, CrossEncoder output for classification can be Sigmoid-activated.
                    # Min/Max normalization or simple raw score mapping depending on training labels.
                    # Our labels were 0.0 to 1.0 (float). So Sigmoid is perfect.
                    raw_score = float(score[0]) if hasattr(score, "__len__") else float(score)
                    # Convert to percentage and bound to [0, 100]
                    percentage_score = round(max(0.0, min(1.0, raw_score)) * 100, 2)
                    candidates[i]["cross_encoder_score"] = percentage_score
            except Exception as e:
                print(f"[NLP] Cross-Encoder ranking failed: {e}")
                for c in candidates:
                    c["cross_encoder_score"] = c["score"]
        else:
            for c in candidates:
                c["cross_encoder_score"] = c["score"]
                
        # Sort by cross-encoder score descending
        candidates.sort(key=lambda x: x.get("cross_encoder_score", x["score"]), reverse=True)
    else:
        # Sort by bi-encoder score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Add rank and clean up sensitive fields
    for i, candidate in enumerate(candidates, 1):
        candidate["rank"] = i
        if "cv_text" in candidate:
            del candidate["cv_text"]
            
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
