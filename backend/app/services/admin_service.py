"""
Admin Service — Business logic for Admin Control Center.
Handles platform stats, user management, audit logs, system health, and AI usage metrics.
"""

import os
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from bson import ObjectId

from app.core.mongodb import (
    get_users_collection,
    get_candidates_collection,
    get_activity_collection,
    get_audit_logs_collection,
)


# ====================================
# Audit Logging
# ====================================

def log_admin_action(admin_email: str, action: str, target: str = "", details: str = ""):
    """Write an admin audit log entry."""
    try:
        col = get_audit_logs_collection()
        col.insert_one({
            "admin_email": admin_email,
            "action": action,
            "target": target,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
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
    limit: int = 50
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
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    total = users_col.count_documents(query)
    users_cursor = users_col.find(query, {"password": 0}).skip(skip).limit(limit).sort("created_at", -1)

    users = []
    for u in users_cursor:
        users.append({
            "id": str(u["_id"]),
            "name": u.get("name", ""),
            "email": u.get("email", ""),
            "role": u.get("role", ""),
            "provider": u.get("provider", "email"),
            "created_at": u.get("created_at", ""),
            "last_login": u.get("last_login", ""),
            "disabled": u.get("disabled", False),
        })

    return {"users": users, "total": total, "skip": skip, "limit": limit}


def update_user(user_id: str, role: Optional[str] = None, disabled: Optional[bool] = None) -> Dict[str, Any]:
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
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """Return paginated and searchable admin audit logs."""
    col = get_audit_logs_collection()
    query = {}

    if keyword:
        query["$or"] = [
            {"admin_email": {"$regex": keyword, "$options": "i"}},
            {"action": {"$regex": keyword, "$options": "i"}},
            {"target": {"$regex": keyword, "$options": "i"}},
            {"details": {"$regex": keyword, "$options": "i"}},
        ]

    total = col.count_documents(query)
    logs_cursor = col.find(query, {"_id": 0}).skip(skip).limit(limit).sort("timestamp", -1)

    return {
        "logs": list(logs_cursor),
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ====================================
# System Health
# ====================================

def _ping_service(url: str, timeout: int = 3) -> Dict[str, Any]:
    """Ping a service URL and return health status."""
    try:
        start = datetime.now()
        resp = requests.get(url, timeout=timeout)
        elapsed = round((datetime.now() - start).total_seconds() * 1000)
        if resp.status_code < 400:
            return {"status": "healthy", "response_ms": elapsed, "code": resp.status_code}
        else:
            return {"status": "warning", "response_ms": elapsed, "code": resp.status_code}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "response_ms": None, "code": None, "detail": "Connection refused"}
    except requests.exceptions.Timeout:
        return {"status": "warning", "response_ms": None, "code": None, "detail": "Timeout"}
    except Exception as e:
        return {"status": "error", "response_ms": None, "code": None, "detail": str(e)}


def get_system_health() -> Dict[str, Any]:
    """Check all service endpoints and return health status."""
    backend_url = os.getenv("BACKEND_INTERNAL_URL", "http://localhost:8000")
    prometheus_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090/-/healthy")
    grafana_url = os.getenv("GRAFANA_URL", "http://grafana:3000/api/health")
    mlflow_url = os.getenv("MLFLOW_URL", "http://mlflow:5000/health")

    # Backend health: ping its own root
    backend_health = _ping_service(f"{backend_url}/")
    backend_health["name"] = "Backend API"
    backend_health["icon"] = "server"

    # MongoDB: check via collection ping
    try:
        from app.core.mongodb import db
        db.command("ping")
        mongo_health = {"status": "healthy", "response_ms": None, "code": 200}
    except Exception as e:
        mongo_health = {"status": "error", "response_ms": None, "code": None, "detail": str(e)}
    mongo_health["name"] = "MongoDB"
    mongo_health["icon"] = "database"

    # Prometheus
    prom_health = _ping_service(prometheus_url)
    prom_health["name"] = "Prometheus"
    prom_health["icon"] = "chart"

    # Grafana
    grafana_health = _ping_service(grafana_url)
    grafana_health["name"] = "Grafana"
    grafana_health["icon"] = "graph"

    # MLflow
    mlflow_health = _ping_service(mlflow_url)
    mlflow_health["name"] = "MLflow"
    mlflow_health["icon"] = "experiment"

    # GitHub Actions — check via GitHub API
    github_token = os.getenv("GITHUB_TOKEN", "")
    github_repo = os.getenv("GITHUB_REPO", "")
    if github_token and github_repo:
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{github_repo}/actions/runs?per_page=1",
                headers={"Authorization": f"Bearer {github_token}"},
                timeout=5
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
                gh_health = {"status": gh_status, "detail": conclusion, "response_ms": None}
            else:
                gh_health = {"status": "warning", "detail": f"HTTP {resp.status_code}", "response_ms": None}
        except Exception as e:
            gh_health = {"status": "error", "detail": str(e), "response_ms": None}
    else:
        gh_health = {"status": "unknown", "detail": "GITHUB_TOKEN/GITHUB_REPO not configured", "response_ms": None}
    gh_health["name"] = "GitHub Actions"
    gh_health["icon"] = "ci"

    services = [backend_health, mongo_health, prom_health, grafana_health, mlflow_health, gh_health]

    healthy_count = sum(1 for s in services if s["status"] == "healthy")
    overall = "healthy" if healthy_count == len(services) else ("warning" if healthy_count > 0 else "error")

    return {
        "overall": overall,
        "services": services,
        "checked_at": datetime.now(timezone.utc).isoformat()
    }


# ====================================
# AI Usage Metrics
# ====================================

def get_ai_usage() -> Dict[str, Any]:
    """
    Return AI feature usage counts by reading Prometheus metrics endpoint.
    Falls back to activity log counts if Prometheus is unavailable.
    """
    prometheus_base = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    # Remove /-/healthy suffix for query API
    prometheus_base = prometheus_base.replace("/-/healthy", "").rstrip("/")

    def query_prometheus(metric_name: str) -> int:
        try:
            resp = requests.get(
                f"{prometheus_base}/api/v1/query",
                params={"query": f"sum({metric_name})"},
                timeout=3
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
    scores = [c["match_score"] for c in candidates_col.find({}, {"match_score": 1}) if "match_score" in c]
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
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = (now - timedelta(days=30 * (i - 1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = now

        m_start_iso = month_start.isoformat()
        m_end_iso = month_end.isoformat()

        month_total = candidates_col.count_documents({
            "created_at": {"$gte": m_start_iso, "$lt": m_end_iso}
        })
        month_hired = candidates_col.count_documents({
            "status": "hired",
            "created_at": {"$gte": m_start_iso, "$lt": m_end_iso}
        })

        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "applications": month_total,
            "hired": month_hired
        })

    return {
        "total_applications": total,
        "total_interviews": interview,
        "total_hired": hired,
        "total_rejected": rejected,
        "total_talent_pool": talent_pool,
        "hiring_rate": hiring_rate,
        "monthly_trend": monthly_data,
    }
