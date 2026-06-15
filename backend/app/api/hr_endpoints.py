from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.parser import extract_text, extract_candidate_name, clean_text
from app.services.nlp import cluster_documents, get_similarity_score, match_cv_jd_hybrid
from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    HR_RANKING_COUNT,
    CLUSTERING_COUNT
)

import time
router = APIRouter()

@router.post("/hr/rank")
async def rank_candidates(
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general")
):
    start_time = time.time()

    REQUEST_COUNT.labels(
        endpoint="hr_rank"
    ).inc()

    HR_RANKING_COUNT.inc()

    try:

        candidates = []

        # Clean job description
        jd_clean = clean_text(
            job_description
        )

        for cv in cvs:

            file_bytes = await cv.read()

            cv_text = extract_text(
                file_bytes,
                cv.filename
            )

            candidate_name = (
                extract_candidate_name(
                    cv_text,
                    cv.filename
                )
            )

            semantic_score = (
                get_similarity_score(
                    cv_text,
                    jd_clean
                )
            )

            matched_skills, missing_skills = (
                match_cv_jd_hybrid(
                    cv_text,
                    jd_clean,
                    domain
                )
            )

            total_target_skills = (
                len(matched_skills)
                + len(missing_skills)
            )

            domain_skill_score = (
                round(
                    (
                        len(matched_skills)
                        / total_target_skills
                    ) * 100,
                    2
                )
                if total_target_skills > 0
                else 0.0
            )

            final_score = round(
                (
                    semantic_score * 0.85
                )
                +
                (
                    domain_skill_score * 0.15
                ),
                2
            )

            candidates.append({
                "name": candidate_name,
                "score": final_score,
                "semantic_score": semantic_score,
                "domain_skill_score": domain_skill_score,
                "matched_skills_count": len(
                    matched_skills
                ),
                "missing_skills_count": len(
                    missing_skills
                ),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "domain": domain,
                "filename": cv.filename
            })

        # Sort descending
        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        # Add ranking
        for i, candidate in enumerate(
            candidates,
            start=1
        ):
            candidate["rank"] = i

        return candidates

    finally:

        REQUEST_LATENCY.labels(
            endpoint="hr_rank"
        ).observe(
            time.time() - start_time
        )

@router.post("/hr/cluster")
async def cluster_candidates(
    cvs: List[UploadFile] = File(...),
    num_clusters: int = Form(3)
):
    start_time = time.time()

    REQUEST_COUNT.labels(
        endpoint="hr_cluster"
    ).inc()

    CLUSTERING_COUNT.inc()

    try:

        texts = []
        filenames = []

        for cv in cvs:

            file_bytes = await cv.read()

            cv_text = extract_text(
                file_bytes,
                cv.filename
            )

            texts.append(cv_text)
            filenames.append(cv.filename)

        clusters = cluster_documents(
            texts,
            filenames,
            num_clusters
        )

        return clusters

    finally:

        REQUEST_LATENCY.labels(
            endpoint="hr_cluster"
        ).observe(
            time.time() - start_time
        )