from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from app.core.mongodb import get_candidates_collection, get_activity_collection

def parse_iso_date(date_str: str) -> Optional[datetime]:
    try:
        # Try parsing standard ISO format
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        try:
            # Fallback for date-only formats YYYY-MM-DD
            return datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            return None

def build_filter_query(start_date: Optional[str] = None, end_date: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
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

def calculate_trend(status: str, query_base: Dict[str, Any]) -> str:
    candidates_col = get_candidates_collection()
    now = datetime.now(timezone.utc)
    
    seven_days_ago = (now - timedelta(days=7)).isoformat()
    fourteen_days_ago = (now - timedelta(days=14)).isoformat()
    
    # Build query for last 7 days
    q_curr = query_base.copy()
    if status != "total":
        q_curr["status"] = status
    
    # Merge date range for current 7 days
    if "created_at" in q_curr:
        if isinstance(q_curr["created_at"], dict):
            # Intersect with last 7 days
            existing_gte = q_curr["created_at"].get("$gte", fourteen_days_ago)
            q_curr["created_at"] = {
                "$gte": max(existing_gte, seven_days_ago),
                "$lte": q_curr["created_at"].get("$lte", now.isoformat())
            }
    else:
        q_curr["created_at"] = {"$gte": seven_days_ago}
        
    # Build query for previous 7 days
    q_prev = query_base.copy()
    if status != "total":
        q_prev["status"] = status
        
    if "created_at" in q_prev:
        if isinstance(q_prev["created_at"], dict):
            existing_gte = q_prev["created_at"].get("$gte", fourteen_days_ago)
            q_prev["created_at"] = {
                "$gte": max(existing_gte, fourteen_days_ago),
                "$lt": seven_days_ago
            }
    else:
        q_prev["created_at"] = {
            "$gte": fourteen_days_ago,
            "$lt": seven_days_ago
        }
        
    try:
        curr_count = candidates_col.count_documents(q_curr)
        prev_count = candidates_col.count_documents(q_prev)
    except Exception:
        return "0%"
        
    if prev_count == 0:
        return f"+{curr_count * 100}%" if curr_count > 0 else "0%"
        
    diff_pct = int(((curr_count - prev_count) / prev_count) * 100)
    if diff_pct >= 0:
        return f"+{diff_pct}%"
    return f"{diff_pct}%"

def get_recruitment_stats(start_date: Optional[str] = None, end_date: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
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
    scores = [c["match_score"] for c in candidates_col.find(query, {"match_score": 1}) if "match_score" in c]
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
            "rejected": stats_data["rejected"]
        },
        "trends": {
            "total_candidates": trends["total"],
            "screening": trends["screening"],
            "talent_pool": trends["talent_pool"],
            "interview": trends["interview"],
            "hired": trends["hired"],
            "rejected": trends["rejected"]
        },
        "scores": {
            "average": avg_score,
            "highest": highest_score,
            "lowest": lowest_score
        }
    }

def get_candidate_funnel(start_date: Optional[str] = None, end_date: Optional[str] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
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
    q_screening["status"] = {"$in": ["screening", "talent_pool", "interview", "hired", "rejected"]}
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
        {"stage": "Screening", "count": screening, "percentage": round((screening / applicants * 100), 1) if applicants > 0 else 0.0},
        {"stage": "Talent Pool", "count": talent_pool, "percentage": round((talent_pool / applicants * 100), 1) if applicants > 0 else 0.0},
        {"stage": "Interview", "count": interview, "percentage": round((interview / applicants * 100), 1) if applicants > 0 else 0.0},
        {"stage": "Hired", "count": hired, "percentage": round((hired / applicants * 100), 1) if applicants > 0 else 0.0}
    ]

def get_top_skills(start_date: Optional[str] = None, end_date: Optional[str] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
    candidates_col = get_candidates_collection()
    query = build_filter_query(start_date, end_date, domain)
    
    pipeline = [
        {"$match": query},
        {
            "$project": {
                "skills": {
                    "$concatArrays": [
                        {"$ifNull": ["$matched_skills", []]},
                        {"$ifNull": ["$missing_skills", []]}
                    ]
                }
            }
        },
        {"$unwind": "$skills"},
        {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    try:
        results = list(candidates_col.aggregate(pipeline))
        return [{"skill": r["_id"], "count": r["count"]} for r in results]
    except Exception:
        return []

def get_job_categories(start_date: Optional[str] = None, end_date: Optional[str] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
    candidates_col = get_candidates_collection()
    query = build_filter_query(start_date, end_date, domain)
    
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    try:
        results = list(candidates_col.aggregate(pipeline))
        # Map domain code to label
        domain_labels = {
            "general": "General", "it": "IT", "hr": "HR", "finance": "Finance",
            "creative": "Creative", "sales": "Sales", "legal": "Legal", "pr": "PR",
            "ga": "GA", "cs": "Customer Service", "operational": "Operational"
        }
        return [
            {
                "category": domain_labels.get(r["_id"], str(r["_id"]).capitalize()) if r["_id"] else "General",
                "count": r["count"]
            }
            for r in results
        ]
    except Exception:
        return []

def get_activity_timeline(start_date: Optional[str] = None, end_date: Optional[str] = None, domain: Optional[str] = None) -> List[Dict[str, Any]]:
    activity_col = get_activity_collection()
    
    # Filter on activity logs
    # To support job domain filter, we need to join or match the candidate's domain.
    # Since activity logs store simple details, let's match domain using candidate database references if domain is set.
    match_query = {}
    if start_date or end_date:
        date_q = {}
        if start_date:
            date_q["$gte"] = start_date
        if end_date:
            date_q["$lte"] = end_date
        match_query["timestamp"] = date_q
        
    if domain and domain.strip() and domain.lower() != "all":
        # Get candidate IDs matching the domain
        candidates_col = get_candidates_collection()
        candidate_ids = [str(c["_id"]) for c in candidates_col.find({"domain": domain}, {"_id": 1})]
        match_query["candidate_id"] = {"$in": candidate_ids}
        
    pipeline = [
        {"$match": match_query},
        {
            "$project": {
                "day": {"$substr": ["$timestamp", 0, 10]}, # Group by YYYY-MM-DD
                "action": "$action"
            }
        },
        {
            "$group": {
                "_id": {"day": "$day", "action": "$action"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.day": 1}}
    ]
    
    try:
        results = list(activity_col.aggregate(pipeline))
        
        # Format:
        # Group by day, showing count for each activity action
        timeline_map = {}
        action_mapping = {
            "added": "Candidates Added",
            "talent_pool": "Talent Pool Transfers",
            "interview": "Interview Transfers",
            "interview_scheduled": "Interview Scheduled",
            "hired": "Hiring Decisions",
            "rejected": "Rejection Decisions"
        }
        
        for r in results:
            day = r["_id"]["day"]
            action = r["_id"]["action"]
            action_label = action_mapping.get(action, action.replace("_", " ").capitalize())
            count = r["count"]
            
            if day not in timeline_map:
                timeline_map[day] = {
                    "date": day,
                    "added": 0,
                    "talent_pool": 0,
                    "interview": 0,
                    "hired": 0,
                    "rejected": 0
                }
            
            # Map database action string to frontend keys
            key = action
            if action == "interview_scheduled":
                # merge with interview or keep separate
                key = "interview"
            
            if key in timeline_map[day]:
                timeline_map[day][key] += count
                
        # Fill missing dates to make line chart continuous if it is empty, or sort
        timeline_list = sorted(timeline_map.values(), key=lambda x: x["date"])
        
        # If no activities, return dummy template or empty list
        return timeline_list
    except Exception:
        return []
