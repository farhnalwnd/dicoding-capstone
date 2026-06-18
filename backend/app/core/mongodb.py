import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.cv_matcher

def get_jobs_collection():
    return db.linkedin_jobs

def get_users_collection():
    """Get the users collection with a unique index on email."""
    collection = db.users
    collection.create_index("email", unique=True)
    return collection

def get_candidates_collection():
    """Get the candidates collection for Talent Pool Management."""
    return db.candidates

def get_activity_collection():
    """Get the activity log collection for Recruitment Analytics."""
    return db.activity_log

def get_audit_logs_collection():
    """Get the audit logs collection for Admin tracking."""
    return db.audit_logs

def log_activity(candidate_id: str, candidate_name: str, action: str, details: str = None):
    """Log candidate activity for recruitment timeline statistics."""
    from datetime import datetime, timezone
    try:
        activity_col = get_activity_collection()
        activity_col.insert_one({
            "candidate_id": str(candidate_id),
            "candidate_name": candidate_name,
            "action": action, # added, talent_pool, interview, interview_scheduled, hired, rejected
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or ""
        })
    except Exception as e:
        print(f"Failed to log activity: {e}")


