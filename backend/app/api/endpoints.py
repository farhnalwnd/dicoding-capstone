from fastapi import APIRouter, UploadFile, File, Form
from app.services.parser import extract_text
from app.services.nlp import get_similarity_score, extract_keywords

router = APIRouter()

@router.post("/match")
async def match_cv_to_job(
    cv: UploadFile = File(...),
    job_description: str = Form(...)
):
    file_bytes = await cv.read()
    cv_text = extract_text(file_bytes, cv.filename)
    
    similarity_score = get_similarity_score(cv_text, job_description)
    
    combined_text = cv_text + " " + job_description
    insights = extract_keywords(combined_text)
    
    return {
        "similarity_score": similarity_score,
        "insights": insights
    }
