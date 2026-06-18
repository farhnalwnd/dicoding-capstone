import os

from pymongo import MongoClient

_client = None
_db = None


def _get_db():
    """Lazy-connect to MongoDB.

    The connection is deferred until the first collection accessor is called,
    so the module can be imported safely in environments without a real
    MONGO_URI (e.g. CI test runners that mock the database layer).
    """
    global _client, _db
    if _db is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError(
                "MONGO_URI environment variable is required. "
                "Set it before starting the server."
            )
        _client = MongoClient(uri)
        _db = _client.cv_matcher
    return _db


def get_jobs_collection():
    return _get_db().linkedin_jobs


def get_users_collection():
    """Get the users collection with a unique index on email."""
    collection = _get_db().users
    collection.create_index("email", unique=True)
    return collection


def get_candidates_collection():
    """Get the candidates collection for Talent Pool Management."""
    return _get_db().candidates


def get_activity_collection():
    """Get the activity log collection for Recruitment Analytics."""
    return _get_db().activity_log


def get_audit_logs_collection():
    """Get the audit logs collection for Admin tracking."""
    return _get_db().audit_logs


def log_activity(
    candidate_id: str, candidate_name: str, action: str, details: str = None
):
    """Log candidate activity for recruitment timeline statistics."""
    from datetime import datetime, timezone

    try:
        activity_col = get_activity_collection()
        activity_col.insert_one(
            {
                "candidate_id": str(candidate_id),
                "candidate_name": candidate_name,
                "action": action,  # added, talent_pool, interview, interview_scheduled, hired, rejected
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details or "",
            }
        )
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(
            "Failed to log activity: %s", type(e).__name__
        )
