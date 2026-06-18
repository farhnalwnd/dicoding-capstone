from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.services.resume_advisor_service import (
    generate_advisor_pdf,
    generate_advisor_recommendations,
)

router = APIRouter()


class ResumeAdvisorRequest(BaseModel):
    match_score: float = Field(..., description="The current similarity/match score")
    matched_skills: List[str] = Field(default=[], description="List of skills matched")
    missing_skills: List[str] = Field(default=[], description="List of skills missing")
    recommendation: str = Field(..., description="Current recommendation level")
    job_description: str = Field(
        ..., description="Raw text of job description requirements"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "match_score": 44.91,
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["Docker", "Kubernetes", "CI/CD"],
                "recommendation": "Moderate Match",
                "job_description": "Looking for a backend engineer with Python, FastAPI, Docker and Kubernetes.",
            }
        }
    }


class LearningPlanItem(BaseModel):
    duration: str
    tasks: List[str]


class CareerRecommendations(BaseModel):
    career_suitability: str
    recommended_roles: List[str]
    recommended_technologies: List[str]


class ResumeAdvisorResponse(BaseModel):
    current_score: float
    estimated_score: float
    missing_skills_summary: str
    learning_plan: List[LearningPlanItem]
    resume_tips: List[str]
    interview_tips: List[str]
    career_recommendations: CareerRecommendations


@router.post("", response_model=ResumeAdvisorResponse)
async def get_advisor_advice(
    payload: ResumeAdvisorRequest, current_user: dict = Depends(get_current_user)
):
    """
    Get AI-driven CV recommendations and custom learning roadmap based on CV-JD analysis.
    Only accessible to Job Seekers.
    """
    if current_user.get("role") != "jobseeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Job Seekers can access the Resume Advisor.",
        )

    result = generate_advisor_recommendations(
        match_score=payload.match_score,
        matched_skills=payload.matched_skills,
        missing_skills=payload.missing_skills,
        recommendation=payload.recommendation,
        job_description=payload.job_description,
    )

    return result


@router.post("/export")
async def export_advisor_pdf_report(
    recommendations: Dict[str, Any], current_user: dict = Depends(get_current_user)
):
    """
    Export the advisor's recommendations as a downloadable PDF report.
    Only accessible to Job Seekers.
    """
    if current_user.get("role") != "jobseeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Job Seekers can export reports.",
        )

    try:
        pdf_bytes = generate_advisor_pdf(recommendations)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=AI_Resume_Advisor_Report.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(e)}",
        )
