"""
Admin API Endpoints.
All routes are protected by require_role("admin").
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.auth import require_role
from app.services import admin_service

router = APIRouter()


# ====================================
# Request Models
# ====================================


class UpdateUserRequest(BaseModel):
    role: Optional[str] = None  # "hr", "jobseeker", "admin"
    disabled: Optional[bool] = None


# ====================================
# Platform Statistics
# ====================================


@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(require_role("admin"))):
    """Return platform-wide KPI statistics."""
    return admin_service.get_platform_stats()


# ====================================
# User Management
# ====================================


@router.get("/users")
async def list_users(
    role: Optional[str] = Query(
        None, description="Filter by role: hr, jobseeker, admin"
    ),
    status: Optional[str] = Query(
        None, description="Filter by status: active, disabled"
    ),
    search: Optional[str] = Query(None, description="Search by name or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_role("admin")),
):
    """Return paginated list of all platform users."""
    return admin_service.get_all_users(
        role=role, status=status, search=search, skip=skip, limit=limit
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    current_user: dict = Depends(require_role("admin")),
):
    """Update a user's role or disabled status."""
    if payload.role and payload.role not in ("hr", "jobseeker", "admin"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="role must be one of: hr, jobseeker, admin",
        )

    result = admin_service.update_user(
        user_id=user_id, role=payload.role, disabled=payload.disabled
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("detail", "Update failed"),
        )

    # Log the action
    action = []
    if payload.role is not None:
        action.append(f"role → {payload.role}")
    if payload.disabled is not None:
        action.append("disabled" if payload.disabled else "enabled")

    admin_service.log_admin_action(
        admin_email=current_user["email"],
        action="user_update",
        target=user_id,
        details=", ".join(action),
    )

    return result


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str, current_user: dict = Depends(require_role("admin"))
):
    """Hard delete a user by ID."""
    # Prevent admin from deleting themselves
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )

    result = admin_service.delete_user(user_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("detail", "Delete failed"),
        )

    admin_service.log_admin_action(
        admin_email=current_user["email"],
        action="user_delete",
        target=user_id,
        details="User permanently deleted",
    )

    return {"message": "User deleted successfully"}


# ====================================
# Audit Logs
# ====================================


@router.get("/audit-logs")
async def get_audit_logs(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(require_role("admin")),
):
    """Return searchable admin audit logs."""
    return admin_service.get_audit_logs(keyword=keyword, skip=skip, limit=limit)


# ====================================
# System Health
# ====================================


@router.get("/system-health")
async def get_system_health(current_user: dict = Depends(require_role("admin"))):
    """Return health status of all platform services."""
    return admin_service.get_system_health()


# ====================================
# AI Usage Analytics
# ====================================


@router.get("/ai-usage")
async def get_ai_usage(current_user: dict = Depends(require_role("admin"))):
    """Return AI feature usage metrics."""
    return admin_service.get_ai_usage()


# ====================================
# Recruitment Overview
# ====================================


@router.get("/recruitment-overview")
async def get_recruitment_overview(current_user: dict = Depends(require_role("admin"))):
    """Return recruitment funnel overview with monthly trend."""
    return admin_service.get_recruitment_overview()
