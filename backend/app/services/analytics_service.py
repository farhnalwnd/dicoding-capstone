from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.mongodb import get_activity_collection, get_candidates_collection

# Trend calculation constants
TREND_CURRENT_DAYS = 7
TREND_PREVIOUS_DAYS = 14
PERCENTAGE_MULTIPLIER = 100

# Aggregation limits
TOP_SKILLS_LIMIT = 10
DATE_SUBSTR_LENGTH = 10

# Action label mapping for activity timeline
ACTION_LABEL_MAP = {
    "added": "Candidates Added",
    "talent_pool": "Talent Pool Transfers",
    "interview": "Interview Transfers",
    "interview_scheduled": "Interview Scheduled",
    "hired": "Hiring Decisions",
    "rejected": "Rejection Decisions",
}


def parse_iso_date(date_str: str) -> Optional[datetime]:
    try:
        # Try parsing standard ISO format
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        try:
            # Fallback for date-only formats YYYY-MM-DD
            return datetime.strptime(date_str[:10], "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except Exception:
            return None


def build_filter_query(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    domain: Optional[str] = None,
) -> Dict[str, Any]:  # noqa: E501
    query = {}

    # Domain filter
    if domain and domain.strip() and domain.lower() != "all":
        query["domain"] = domain.strip()

    # Date filter on created_at
    date_query = {}
    if start_date:
        date_query["$gte"] = start_date
    if end_date:
        date_query["$lte"] = end_date

    if date_query:
        query["created_at"] = date_query

    return query


def _build_period_query(
    query_base: Dict[str, Any],
    status: str,
    period_start: str,
    period_end: str,
    fallback_gte: str,
    use_lt: bool = False,
) -> Dict[str, Any]:
    """Build a date-filtered query for a specific time period."""
    q = query_base.copy()
    if status != "total":
        q["status"] = status

    if "created_at" in q and isinstance(q["created_at"], dict):
        existing_gte = q["created_at"].get("$gte", fallback_gte)
        if use_lt:
            q["created_at"] = {
                "$gte": max(existing_gte, period_start),
                "$lt": period_end,
            }
        else:
            q["created_at"] = {
                "$gte": max(existing_gte, period_start),
                "$lte": period_end,
            }
    else:
        if use_lt:
            q["created_at"] = {"$gte": period_start, "$lt": period_end}
        else:
            q["created_at"] = {"$gte": period_start}

    return q


def _format_trend_percentage(curr_count: int, prev_count: int) -> str:
    """Format a trend percentage string from two period counts.

    - If previous period had 0 records and current has some, return 'New'
      (avoids misleading +14800% style numbers).
    - Caps displayed percentage at ±999% to keep UI readable.
    - Returns '0%' if both periods are zero.
    """
    if prev_count == 0:
        if curr_count == 0:
            return "0%"
        return "New"  # First time data appears — cleaner than +∞%

    diff_pct = int(((curr_count - prev_count) / prev_count) * PERCENTAGE_MULTIPLIER)

    # Cap to ±999 so the UI never shows absurdly large percentages
    diff_pct = max(-999, min(999, diff_pct))

    if diff_pct >= 0:
        return f"+{diff_pct}%"
    return f"{diff_pct}%"


def calculate_trend(status: str, query_base: Dict[str, Any]) -> str:
    candidates_col = get_candidates_collection()
    now = datetime.now(timezone.utc)

    seven_days_ago = (now - timedelta(days=TREND_CURRENT_DAYS)).isoformat()
    fourteen_days_ago = (now - timedelta(days=TREND_PREVIOUS_DAYS)).isoformat()

    q_curr = _build_period_query(
        query_base, status, seven_days_ago, now.isoformat(), fourteen_days_ago
    )
    q_prev = _build_period_query(
        query_base,
        status,
        fourteen_days_ago,
        seven_days_ago,
        fourteen_days_ago,
        use_lt=True,
    )

    try:
        curr_count = candidates_col.count_documents(q_curr)
        prev_count = candidates_col.count_documents(q_prev)
    except Exception:
        return "0%"

    return _format_trend_percentage(curr_count, prev_count)


def get_recruitment_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    domain: Optional[str] = None,
) -> Dict[str, Any]:  # noqa: E501
    candidates_col = get_candidates_collection()
    query = build_filter_query(start_date, end_date, domain)

    total = candidates_col.count_documents(query)

    statuses = ["screening", "talent_pool", "interview", "hired", "rejected"]
    stats_data = {"total": total}
    trends = {"total": calculate_trend("total", query)}

    for s in statuses:
        s_query = query.copy()
        s_query["status"] = s
        stats_data[s] = candidates_col.count_documents(s_query)
        trends[s] = calculate_trend(s, query)

    # Calculate score metrics across filtered candidates
    scores = [
        c["match_score"]
        for c in candidates_col.find(query, {"match_score": 1})
        if "match_score" in c
    ]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    highest_score = round(max(scores), 1) if scores else 0.0
    lowest_score = round(min(scores), 1) if scores else 0.0

    return {
        "counts": {
            "total_candidates": total,
            "screening": stats_data["screening"],
            "talent_pool": stats_data["talent_pool"],
            "interview": stats_data["interview"],
            "hired": stats_data["hired"],
            "rejected": stats_data["rejected"],
        },
        "trends": {
            "total_candidates": trends["total"],
            "screening": trends["screening"],
            "talent_pool": trends["talent_pool"],
            "interview": trends["interview"],
            "hired": trends["hired"],
            "rejected": trends["rejected"],
        },
        "scores": {
            "average": avg_score,
            "highest": highest_score,
            "lowest": lowest_score,
        },
    }


def get_candidate_funnel(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    domain: Optional[str] = None,
) -> List[Dict[str, Any]]:  # noqa: E501
    candidates_col = get_candidates_collection()
    query = build_filter_query(start_date, end_date, domain)

    # Funnel stages are cumulative:
    # 1. Applicants: Everyone
    # 2. Screening: Status in ['screening', 'talent_pool', 'interview', 'hired', 'rejected']
    # 3. Talent Pool: Status in ['talent_pool', 'interview', 'hired']
    # 4. Interview: Status in ['interview', 'hired']
    # 5. Hired: Status in ['hired']

    q_all = query.copy()
    applicants = candidates_col.count_documents(q_all)

    q_screening = query.copy()
    q_screening["status"] = {
        "$in": ["screening", "talent_pool", "interview", "hired", "rejected"]
    }
    screening = candidates_col.count_documents(q_screening)

    q_tp = query.copy()
    q_tp["status"] = {"$in": ["talent_pool", "interview", "hired"]}
    talent_pool = candidates_col.count_documents(q_tp)

    q_int = query.copy()
    q_int["status"] = {"$in": ["interview", "hired"]}
    interview = candidates_col.count_documents(q_int)

    q_hired = query.copy()
    q_hired["status"] = "hired"
    hired = candidates_col.count_documents(q_hired)

    return [
        {"stage": "Applicants", "count": applicants, "percentage": 100.0},
        {
            "stage": "Screening",
            "count": screening,
            "percentage": (
                round((screening / applicants * 100), 1) if applicants > 0 else 0.0
            ),
        },
        {
            "stage": "Talent Pool",
            "count": talent_pool,
            "percentage": (
                round((talent_pool / applicants * 100), 1) if applicants > 0 else 0.0
            ),
        },
        {
            "stage": "Interview",
            "count": interview,
            "percentage": (
                round((interview / applicants * 100), 1) if applicants > 0 else 0.0
            ),
        },
        {
            "stage": "Hired",
            "count": hired,
            "percentage": (
                round((hired / applicants * 100), 1) if applicants > 0 else 0.0
            ),
        },
    ]


def get_top_skills(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    domain: Optional[str] = None,
) -> List[Dict[str, Any]]:  # noqa: E501
    candidates_col = get_candidates_collection()
    query = build_filter_query(start_date, end_date, domain)

    pipeline = [
        {"$match": query},
        {
            "$project": {
                "skills": {
                    "$concatArrays": [
                        {"$ifNull": ["$matched_skills", []]},
                        {"$ifNull": ["$missing_skills", []]},
                    ]
                }
            }
        },
        {"$unwind": "$skills"},
        {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": TOP_SKILLS_LIMIT},
    ]

    try:
        results = list(candidates_col.aggregate(pipeline))
        return [{"skill": r["_id"], "count": r["count"]} for r in results]
    except Exception:
        return []


def get_job_categories(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    domain: Optional[str] = None,
) -> List[Dict[str, Any]]:  # noqa: E501
    candidates_col = get_candidates_collection()
    query = build_filter_query(start_date, end_date, domain)

    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    try:
        results = list(candidates_col.aggregate(pipeline))
        # Map domain code to label
        domain_labels = {
            "general": "General",
            "it": "IT",
            "hr": "HR",
            "finance": "Finance",
            "creative": "Creative",
            "sales": "Sales",
            "legal": "Legal",
            "pr": "PR",
            "ga": "GA",
            "cs": "Customer Service",
            "operational": "Operational",
        }
        return [
            {
                "category": (
                    domain_labels.get(r["_id"], str(r["_id"]).capitalize())
                    if r["_id"]
                    else "General"
                ),
                "count": r["count"],
            }
            for r in results
        ]
    except Exception:
        return []


def _build_activity_match_query(
    start_date: Optional[str], end_date: Optional[str], domain: Optional[str]
) -> Dict[str, Any]:
    """Build the $match query for activity timeline aggregation."""
    match_query = {}
    if start_date or end_date:
        date_q = {}
        if start_date:
            date_q["$gte"] = start_date
        if end_date:
            date_q["$lte"] = end_date
        match_query["timestamp"] = date_q

    if domain and domain.strip() and domain.lower() != "all":
        candidates_col = get_candidates_collection()
        candidate_ids = [
            str(c["_id"]) for c in candidates_col.find({"domain": domain}, {"_id": 1})
        ]
        match_query["candidate_id"] = {"$in": candidate_ids}

    return match_query


def _build_activity_pipeline(match_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build the aggregation pipeline for activity timeline."""
    return [
        {"$match": match_query},
        {
            "$project": {
                "day": {"$substr": ["$timestamp", 0, DATE_SUBSTR_LENGTH]},
                "action": "$action",
            }
        },
        {"$group": {"_id": {"day": "$day", "action": "$action"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.day": 1}},
    ]


def _format_timeline_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group aggregation results by day and map action keys."""
    timeline_map = {}

    for r in results:
        day = r["_id"]["day"]
        action = r["_id"]["action"]
        count = r["count"]

        if day not in timeline_map:
            timeline_map[day] = {
                "date": day,
                "added": 0,
                "talent_pool": 0,
                "interview": 0,
                "hired": 0,
                "rejected": 0,
            }

        key = "interview" if action == "interview_scheduled" else action

        if key in timeline_map[day]:
            timeline_map[day][key] += count

    return sorted(timeline_map.values(), key=lambda x: x["date"])


def get_activity_timeline(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    domain: Optional[str] = None,
) -> List[Dict[str, Any]]:  # noqa: E501
    activity_col = get_activity_collection()
    match_query = _build_activity_match_query(start_date, end_date, domain)
    pipeline = _build_activity_pipeline(match_query)

    try:
        results = list(activity_col.aggregate(pipeline))
        return _format_timeline_results(results)
    except Exception:
        return []
