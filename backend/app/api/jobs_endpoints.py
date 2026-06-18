from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.mongodb import get_jobs_collection

router = APIRouter()


@router.get("/jobs")
def get_jobs(current_user: dict = Depends(get_current_user)):
    collection = get_jobs_collection()
    jobs = list(
        collection.find(
            {},
            {
                "_id": 0,
                "title": 1,
                "company": 1,
                "location": 1,
                "url": 1,
                "keyword_searched": 1,
            },
        )
    )  # noqa: E501
    return {"items": jobs, "total": len(jobs)}


@router.delete("/jobs/clear")
def clear_jobs(current_user: dict = Depends(get_current_user)):
    collection = get_jobs_collection()
    result = collection.delete_many({})
    return {"deleted_count": result.deleted_count}
