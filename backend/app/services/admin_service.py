import re

"""
Admin Service — Business logic for Admin Control Center.
Handles platform stats, user management, audit logs, system health, and AI usage metrics.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from bson import ObjectId

from app.core.mongodb import (
    get_activity_collection,
    get_audit_logs_collection,
    get_candidates_collection,
    get_users_collection,
)

# Default service ports / URLs
DEFAULT_BACKEND_URL = "http://localhost:8000"
DEFAULT_PROMETHEUS_URL = "http://prometheus:9090/-/healthy"
DEFAULT_GRAFANA_URL = "http://grafana:3000/api/health"
DEFAULT_MLFLOW_URL = "http://mlflow:5000/health"

# Health check constants
HEALTH_PING_TIMEOUT = 3
GITHUB_API_TIMEOUT = 5
GITHUB_RUNS_PER_PAGE = 1
MONGO_HEALTHY_CODE = 200


# ====================================
# Audit Logging
# ====================================


def log_admin_action(
    admin_email: str, action: str, target: str = "", details: str = ""
):
    """Write an admin audit log entry."""
    try:
        col = get_audit_logs_collection()
        col.insert_one(
            {
                "admin_email": admin_email,
                "action": action,
                "target": target,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as e:
        print(f"Failed to log admin action: {e}")


# ====================================
# Platform Statistics
# ====================================


def get_platform_stats() -> Dict[str, Any]:
    """Return platform-wide KPI counts."""
    users_col = get_users_collection()
    candidates_col = get_candidates_collection()
    activity_col = get_activity_collection()

    total_users = users_col.count_documents({})
    total_hr = users_col.count_documents({"role": "hr"})
    total_jobseekers = users_col.count_documents({"role": "jobseeker"})
    total_admins = users_col.count_documents({"role": "admin"})

    total_candidates = candidates_col.count_documents({})
    total_hired = candidates_col.count_documents({"status": "hired"})
    total_interview = candidates_col.count_documents({"status": "interview"})
    total_talent_pool = candidates_col.count_documents({"status": "talent_pool"})

    # CV analyses = activity log entries with action "added"
    total_cv_analyses = activity_col.count_documents({"action": "added"})

    return {
        "total_users": total_users,
        "total_hr": total_hr,
        "total_jobseekers": total_jobseekers,
        "total_admins": total_admins,
        "total_candidates": total_candidates,
        "total_hired": total_hired,
        "total_interviews": total_interview,
        "total_talent_pool": total_talent_pool,
        "total_cv_analyses": total_cv_analyses,
    }


# ====================================
# User Management
# ====================================


def get_all_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """Return paginated list of users with optional filters."""
    users_col = get_users_collection()
    query = {}

    if role and role != "all":
        query["role"] = role

    if status and status != "all":
        if status == "active":
            query["$or"] = [{"disabled": {"$exists": False}}, {"disabled": False}]
        elif status == "disabled":
            query["disabled"] = True

    if search:
        query["$or"] = [
            {"name": {"$regex": re.escape(search), "$options": "i"}},
            {"email": {"$regex": re.escape(search), "$options": "i"}},
        ]

    total = users_col.count_documents(query)
    users_cursor = (
        users_col.find(query, {"password": 0})
        .skip(skip)
        .limit(limit)
        .sort("created_at", -1)
    )

    users = []
    for u in users_cursor:
        users.append(
            {
                "id": str(u["_id"]),
                "name": u.get("name", ""),
                "email": u.get("email", ""),
                "role": u.get("role", ""),
                "provider": u.get("provider", "email"),
                "created_at": u.get("created_at", ""),
                "last_login": u.get("last_login", ""),
                "disabled": u.get("disabled", False),
            }
        )

    return {"users": users, "total": total, "skip": skip, "limit": limit}


def update_user(
    user_id: str, role: Optional[str] = None, disabled: Optional[bool] = None
) -> Dict[str, Any]:
    """Update a user's role or disabled status."""
    users_col = get_users_collection()
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        return {"success": False, "detail": "Invalid user ID"}

    update_fields = {}
    if role is not None:
        update_fields["role"] = role
    if disabled is not None:
        update_fields["disabled"] = disabled

    if not update_fields:
        return {"success": False, "detail": "No fields to update"}

    result = users_col.update_one({"_id": obj_id}, {"$set": update_fields})
    if result.matched_count == 0:
        return {"success": False, "detail": "User not found"}

    return {"success": True, "updated": update_fields}


def delete_user(user_id: str) -> Dict[str, Any]:
    """Hard delete a user by ID."""
    users_col = get_users_collection()
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        return {"success": False, "detail": "Invalid user ID"}

    result = users_col.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        return {"success": False, "detail": "User not found"}

    return {"success": True}


# ====================================
# Audit Logs
# ====================================


def get_audit_logs(
    keyword: Optional[str] = None, skip: int = 0, limit: int = 100
) -> Dict[str, Any]:
    """Return paginated and searchable admin audit logs."""
    col = get_audit_logs_collection()
    query = {}

    if keyword:
        query["$or"] = [
            {"admin_email": {"$regex": re.escape(keyword), "$options": "i"}},
            {"action": {"$regex": re.escape(keyword), "$options": "i"}},
            {"target": {"$regex": re.escape(keyword), "$options": "i"}},
            {"details": {"$regex": re.escape(keyword), "$options": "i"}},
        ]

    total = col.count_documents(query)
    logs_cursor = (
        col.find(query, {"_id": 0}).skip(skip).limit(limit).sort("timestamp", -1)
    )

    return {
        "logs": list(logs_cursor),
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ====================================
# System Health
# ====================================


def _ping_service(url: str, timeout: int = HEALTH_PING_TIMEOUT) -> Dict[str, Any]:
    """Ping a service URL and return health status."""
    try:
        start = datetime.now()
        resp = requests.get(url, timeout=timeout)
        elapsed = round((datetime.now() - start).total_seconds() * 1000)
        if resp.status_code < 400:
            return {
                "status": "healthy",
                "response_ms": elapsed,
                "code": resp.status_code,
            }
        else:
            return {
                "status": "warning",
                "response_ms": elapsed,
                "code": resp.status_code,
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "response_ms": None,
            "code": None,
            "detail": "Connection refused",
        }
    except requests.exceptions.Timeout:
        return {
            "status": "warning",
            "response_ms": None,
            "code": None,
            "detail": "Timeout",
        }
    except Exception as e:
        return {"status": "error", "response_ms": None, "code": None, "detail": str(e)}


def _check_backend_health() -> Dict[str, Any]:
    """Check Backend API health."""
    backend_url = os.getenv("BACKEND_INTERNAL_URL", DEFAULT_BACKEND_URL)
    health = _ping_service(f"{backend_url}/")
    health["name"] = "Backend API"
    health["icon"] = "server"
    return health


def _check_mongodb_health() -> Dict[str, Any]:
    """Check MongoDB health via ping command."""
    try:
        from app.core.mongodb import db

        db.command("ping")
        health = {"status": "healthy", "response_ms": None, "code": MONGO_HEALTHY_CODE}
    except Exception as e:
        health = {
            "status": "error",
            "response_ms": None,
            "code": None,
            "detail": str(e),
        }
    health["name"] = "MongoDB"
    health["icon"] = "database"
    return health


def _check_prometheus_health() -> Dict[str, Any]:
    """Check Prometheus health."""
    url = os.getenv("PROMETHEUS_URL", DEFAULT_PROMETHEUS_URL)
    health = _ping_service(url)
    health["name"] = "Prometheus"
    health["icon"] = "chart"
    return health


def _check_grafana_health() -> Dict[str, Any]:
    """Check Grafana health."""
    url = os.getenv("GRAFANA_URL", DEFAULT_GRAFANA_URL)
    health = _ping_service(url)
    health["name"] = "Grafana"
    health["icon"] = "graph"
    return health


def _check_mlflow_health() -> Dict[str, Any]:
    """Check MLflow health."""
    url = os.getenv("MLFLOW_URL", DEFAULT_MLFLOW_URL)
    health = _ping_service(url)
    health["name"] = "MLflow"
    health["icon"] = "experiment"
    return health


def _check_github_health() -> Dict[str, Any]:
    """Check GitHub Actions CI health via the GitHub API."""
    github_token = os.getenv("GITHUB_TOKEN", "")
    github_repo = os.getenv("GITHUB_REPO", "")

    if not (github_token and github_repo):
        health = {
            "status": "unknown",
            "detail": "GITHUB_TOKEN/GITHUB_REPO not configured",
            "response_ms": None,
        }
        health["name"] = "GitHub Actions"
        health["icon"] = "ci"
        return health

    try:
        resp = requests.get(
            f"https://api.github.com/repos/{github_repo}/actions/runs?per_page={GITHUB_RUNS_PER_PAGE}",
            headers={"Authorization": f"Bearer {github_token}"},
            timeout=GITHUB_API_TIMEOUT,
        )
        if resp.status_code == 200:
            runs = resp.json().get("workflow_runs", [])
            conclusion = runs[0].get("conclusion", "unknown") if runs else "unknown"
            if conclusion == "success":
                gh_status = "healthy"
            elif conclusion in ("failure", "cancelled"):
                gh_status = "error"
            else:
                gh_status = "warning"
            health = {"status": gh_status, "detail": conclusion, "response_ms": None}
        else:
            health = {
                "status": "warning",
                "detail": f"HTTP {resp.status_code}",
                "response_ms": None,
            }
    except Exception as e:
        health = {"status": "error", "detail": str(e), "response_ms": None}

    health["name"] = "GitHub Actions"
    health["icon"] = "ci"
    return health


def _compute_overall_status(services: List[Dict[str, Any]]) -> str:
    """Compute overall system health from individual service statuses."""
    healthy_count = sum(1 for s in services if s["status"] == "healthy")
    if healthy_count == len(services):
        return "healthy"
    return "warning" if healthy_count > 0 else "error"


def get_system_health() -> Dict[str, Any]:
    """Check all service endpoints and return health status."""
    services = [
        _check_backend_health(),
        _check_mongodb_health(),
        _check_prometheus_health(),
        _check_grafana_health(),
        _check_mlflow_health(),
        _check_github_health(),
    ]

    return {
        "overall": _compute_overall_status(services),
        "services": services,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


# ====================================
# AI Usage Metrics
# ====================================


def get_ai_usage() -> Dict[str, Any]:
    """
    Return AI feature usage counts by reading Prometheus metrics endpoint.
    Falls back to activity log counts if Prometheus is unavailable.
    """
    prometheus_base = os.getenv("PROMETHEUS_URL", DEFAULT_PROMETHEUS_URL)
    # Remove /-/healthy suffix for query API
    prometheus_base = prometheus_base.replace("/-/healthy", "").rstrip("/")

    def query_prometheus(metric_name: str) -> int:
        try:
            resp = requests.get(
                f"{prometheus_base}/api/v1/query",
                params={"query": f"sum({metric_name})"},
                timeout=HEALTH_PING_TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("data", {}).get("result", [])
                if results:
                    return int(float(results[0]["value"][1]))
        except Exception:
            pass
        return 0

    # Prometheus metric names from app/core/metrics.py
    cv_analyses = query_prometheus("cv_match_analysis_total")
    semantic_searches = query_prometheus("semantic_search_total")
    hr_rankings = query_prometheus("scrape_recommend_total")

    # Resume advisor — track from audit logs since it is not in Prometheus
    audit_col = get_audit_logs_collection()
    advisor_requests = audit_col.count_documents({"action": "resume_advisor_request"})

    # Average match score from candidates
    candidates_col = get_candidates_collection()
    scores = [
        c["match_score"]
        for c in candidates_col.find({}, {"match_score": 1})
        if "match_score" in c
    ]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    return {
        "cv_analysis_requests": cv_analyses,
        "resume_advisor_requests": advisor_requests,
        "semantic_search_requests": semantic_searches,
        "hr_ranking_requests": hr_rankings,
        "average_match_score": avg_score,
        "total_candidates_analyzed": len(scores),
    }


# ====================================
# Recruitment Overview
# ====================================


def get_recruitment_overview() -> Dict[str, Any]:
    """Return recruitment funnel totals and hiring rate."""
    candidates_col = get_candidates_collection()

    total = candidates_col.count_documents({})
    hired = candidates_col.count_documents({"status": "hired"})
    interview = candidates_col.count_documents({"status": "interview"})
    rejected = candidates_col.count_documents({"status": "rejected"})
    talent_pool = candidates_col.count_documents({"status": "talent_pool"})

    hiring_rate = round((hired / total * 100), 1) if total > 0 else 0.0

    # Pipeline by month (last 6 months)
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        if i > 0:
            month_end = (now - timedelta(days=30 * (i - 1))).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        else:
            month_end = now

        m_start_iso = month_start.isoformat()
        m_end_iso = month_end.isoformat()

        month_total = candidates_col.count_documents(
            {"created_at": {"$gte": m_start_iso, "$lt": m_end_iso}}
        )
        month_hired = candidates_col.count_documents(
            {"status": "hired", "created_at": {"$gte": m_start_iso, "$lt": m_end_iso}}
        )

        monthly_data.append(
            {
                "month": month_start.strftime("%b %Y"),
                "applications": month_total,
                "hired": month_hired,
            }
        )

    return {
        "total_applications": total,
        "total_interviews": interview,
        "total_hired": hired,
        "total_rejected": rejected,
        "total_talent_pool": talent_pool,
        "hiring_rate": hiring_rate,
        "monthly_trend": monthly_data,
    }
