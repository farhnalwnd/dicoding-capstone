from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import require_role
from app.services import analytics_service

router = APIRouter()


@router.get("/hr-dashboard/stats", response_model=Dict[str, Any])
async def get_stats(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    domain: Optional[str] = Query(None, description="Filter candidates by job domain"),
    current_user: dict = Depends(require_role("hr")),
):
    return analytics_service.get_recruitment_stats(start_date, end_date, domain)


@router.get("/hr-dashboard/funnel", response_model=List[Dict[str, Any]])
async def get_funnel(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    domain: Optional[str] = Query(None, description="Filter candidates by job domain"),
    current_user: dict = Depends(require_role("hr")),
):
    return analytics_service.get_candidate_funnel(start_date, end_date, domain)


@router.get("/hr-dashboard/skills", response_model=List[Dict[str, Any]])
async def get_skills(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    domain: Optional[str] = Query(None, description="Filter candidates by job domain"),
    current_user: dict = Depends(require_role("hr")),
):
    return analytics_service.get_top_skills(start_date, end_date, domain)


@router.get("/hr-dashboard/categories", response_model=List[Dict[str, Any]])
async def get_categories(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    domain: Optional[str] = Query(None, description="Filter candidates by job domain"),
    current_user: dict = Depends(require_role("hr")),
):
    return analytics_service.get_job_categories(start_date, end_date, domain)


@router.get("/hr-dashboard/timeline", response_model=List[Dict[str, Any]])
async def get_timeline(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    domain: Optional[str] = Query(None, description="Filter candidates by job domain"),
    current_user: dict = Depends(require_role("hr")),
):
    return analytics_service.get_activity_timeline(start_date, end_date, domain)
