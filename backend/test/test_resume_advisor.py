import pytest
from app.core.auth import get_current_user
from app.main import app
from app.services.resume_advisor_service import generate_mock_recommendations, generate_advisor_pdf

def test_generate_mock_recommendations():
    res = generate_mock_recommendations(
        match_score=44.91,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Docker", "Kubernetes", "CI/CD"],
        job_description="Looking for an engineer with Python, FastAPI, Docker, Kubernetes, and CI/CD."
    )
    
    assert res["current_score"] == 44.91
    assert res["estimated_score"] > 44.91
    assert len(res["learning_plan"]) > 0
    assert len(res["resume_tips"]) > 0
    assert len(res["interview_tips"]) > 0
    assert "Docker" in res["missing_skills_summary"]
    assert len(res["career_recommendations"]["recommended_roles"]) > 0

def test_generate_pdf_report():
    rec = generate_mock_recommendations(
        match_score=44.91,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Docker", "Kubernetes", "CI/CD"],
        job_description="Looking for an engineer with Python, FastAPI, Docker, Kubernetes, and CI/CD."
    )
    pdf_bytes = generate_advisor_pdf(rec)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF magic bytes checking
    assert pdf_bytes.startswith(b"%PDF")

def test_advisor_endpoint_role_protection(client):
    # Active user default in fixture is "hr"
    payload = {
        "match_score": 44.91,
        "matched_skills": ["Python"],
        "missing_skills": ["Docker"],
        "recommendation": "Moderate Match",
        "job_description": "Wanted developer with Docker"
    }
    
    # Assert HR user is blocked
    res = client.post("/api/resume-advisor", json=payload)
    assert res.status_code == 403
    
    # Assert HR user is blocked from export
    res_export = client.post("/api/resume-advisor/export", json={})
    assert res_export.status_code == 403

def test_advisor_endpoint_success_for_jobseeker(client):
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "mock_jobseeker_id",
        "name": "Mock Jobseeker",
        "email": "seeker@example.com",
        "role": "jobseeker",
        "provider": "email"
    }
    
    try:
        payload = {
            "match_score": 44.91,
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Docker", "Kubernetes", "CI/CD"],
            "recommendation": "Moderate Match",
            "job_description": "Looking for an engineer with Python, FastAPI, Docker, Kubernetes, and CI/CD."
        }
        
        # Test main recommendations endpoint
        response = client.post("/api/resume-advisor", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["current_score"] == 44.91
        assert "learning_plan" in data
        assert len(data["learning_plan"]) > 0
        
        # Test PDF export endpoint
        response_export = client.post("/api/resume-advisor/export", json=data)
        assert response_export.status_code == 200
        assert response_export.headers["content-type"] == "application/pdf"
        assert response_export.content.startswith(b"%PDF")
        
    finally:
        # Reset to default override or remove override
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
