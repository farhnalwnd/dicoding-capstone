from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from typing import List, Tuple
from app.services.parser import extract_text, extract_candidate_name, clean_text
from app.services.nlp import cluster_documents, get_similarity_score, match_cv_jd_hybrid, extract_phrases, get_skill_embeddings_for_skills, model, has_skill_exact
from app.core.domain_loader import load_domain_config
from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    HR_RANKING_COUNT,
    CLUSTERING_COUNT
)
from app.services.progress import progress_manager
from sklearn.cluster import KMeans
from sentence_transformers import util
import time
import asyncio

router = APIRouter()


def compute_candidate_score(
    semantic_score: float,
    matched_skills: list,
    missing_skills: list,
    cv_text: str,
    domain: str
) -> tuple:
    """
    Compute final match score using the same formula as build_match_explanation.
    Formula: 70% Semantic + 10% Coverage (reliability-adjusted) + 20% Domain Relevance

    Rules:
    - IT CV + IT JD  → highest score (domain relevance bonus)
    - IT CV + HR JD  → lower score  (0 domain relevance)
    - HR CV + IT JD  → lower score  (0 domain relevance for IT domain)
    - JDs with < 8 skills get a reliability penalty on coverage
    """
    total_skills = len(matched_skills) + len(missing_skills)
    coverage_ratio = (
        (len(matched_skills) / total_skills) * 100
        if total_skills > 0 else 0.0
    )

    # Skill reliability penalty: JDs with few skills get less coverage bonus
    MIN_RELIABLE_SKILLS = 8
    skill_reliability = min(1.0, total_skills / MIN_RELIABLE_SKILLS)
    effective_coverage = coverage_ratio * skill_reliability

    # Domain relevance: how many of ALL domain skills appear in the CV
    config = load_domain_config(domain)
    all_domain_skills = config.get("skills", [])
    if all_domain_skills:
        cv_domain_hits = sum(
            1 for s in all_domain_skills
            if has_skill_exact(s, cv_text)
        )
        domain_relevance = round(
            (cv_domain_hits / len(all_domain_skills)) * 100, 2
        )
    else:
        domain_relevance = 0.0

    final_score = round(
        (semantic_score * 0.70)
        + (effective_coverage * 0.10)
        + (domain_relevance * 0.20),
        2
    )

    return final_score, round(coverage_ratio, 2), domain_relevance

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

            final_score, coverage_ratio, domain_relevance = compute_candidate_score(
                semantic_score=semantic_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                cv_text=cv_text,
                domain=domain
            )

            candidates.append({
                "name": candidate_name,
                "score": final_score,
                "semantic_score": semantic_score,
                "domain_skill_score": coverage_ratio,
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills),
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


# ==========================================
# Real-Time SSE endpoints & Background Workers
# ==========================================

async def run_hr_rank_task(job_id: str, cv_files: List[Tuple[bytes, str]], job_description: str, domain: str):
    try:
        progress_manager.update_progress(job_id, 10, "Parsing CVs")
        jd_clean = clean_text(job_description)
        
        parsed_cvs = []
        for file_bytes, filename in cv_files:
            cv_text = extract_text(file_bytes, filename)
            parsed_cvs.append((cv_text, filename))
        await asyncio.sleep(0.3)
        
        progress_manager.update_progress(job_id, 30, "Extracting Skills")
        candidates = []
        for cv_text, filename in parsed_cvs:
            candidate_name = extract_candidate_name(cv_text, filename)
            semantic_score = get_similarity_score(cv_text, jd_clean)
            matched_skills, missing_skills = match_cv_jd_hybrid(cv_text, jd_clean, domain)

            final_score, coverage_ratio, domain_relevance = compute_candidate_score(
                semantic_score=semantic_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                cv_text=cv_text,
                domain=domain
            )

            candidates.append({
                "name": candidate_name,
                "score": final_score,
                "semantic_score": semantic_score,
                "domain_skill_score": coverage_ratio,
                "matched_skills_count": len(matched_skills),
                "missing_skills_count": len(missing_skills),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "domain": domain,
                "filename": filename
            })
        await asyncio.sleep(0.3)
        
        progress_manager.update_progress(job_id, 50, "Embedding Generation")
        await asyncio.sleep(0.3)
        
        progress_manager.update_progress(job_id, 75, "Ranking Candidates")
        candidates.sort(key=lambda x: x["score"], reverse=True)
        for i, candidate in enumerate(candidates, start=1):
            candidate["rank"] = i
        await asyncio.sleep(0.2)
        
        progress_manager.complete_job(job_id, candidates)
    except Exception as e:
        progress_manager.fail_job(job_id, f"Failed to rank: {str(e)}")

async def run_hr_cluster_task(job_id: str, cv_files: List[Tuple[bytes, str]], num_clusters: int):
    try:
        progress_manager.update_progress(job_id, 10, "Parsing CVs")
        texts = []
        filenames = []
        for file_bytes, filename in cv_files:
            cv_text = extract_text(file_bytes, filename)
            texts.append(cv_text)
            filenames.append(filename)
        await asyncio.sleep(0.3)
        
        progress_manager.update_progress(job_id, 30, "Generating Embeddings")
        await asyncio.sleep(0.3)
        
        progress_manager.update_progress(job_id, 60, "Clustering Candidates")
        actual_num_clusters = num_clusters
        if len(texts) < actual_num_clusters:
            actual_num_clusters = len(texts)
            
        embeddings = model.encode(texts)
        kmeans = KMeans(n_clusters=actual_num_clusters, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        labels = kmeans.labels_
        await asyncio.sleep(0.3)
        
        progress_manager.update_progress(job_id, 85, "Building Clusters")
        clusters = {i: [] for i in range(actual_num_clusters)}
        for idx, label in enumerate(labels):
            clusters[label].append({
                "filename": filenames[idx],
                "text": texts[idx]
            })
            
        result = []
        for cluster_id, items in clusters.items():
            combined_text = " ".join([item["text"] for item in items])
            cluster_phrases = extract_phrases(combined_text)
            
            if cluster_phrases:
                phrase_embs = model.encode(cluster_phrases[:50], convert_to_tensor=True)
                cluster_skills = []
                for skill_name, skill_emb in get_skill_embeddings_for_skills([]).items():
                    similarities = util.cos_sim(skill_emb, phrase_embs)[0]
                    max_sim = similarities.max().item()
                    if max_sim > 0.82:
                        cluster_skills.append(skill_name)
                suggested_label = " / ".join(cluster_skills[:3]) if cluster_skills else f"Cluster {cluster_id + 1}"
            else:
                suggested_label = f"Cluster {cluster_id + 1}"
                
            result.append({
                "cluster_id": cluster_id,
                "suggested_label": suggested_label,
                "candidates": [item["filename"] for item in items]
            })
        await asyncio.sleep(0.2)
        
        progress_manager.complete_job(job_id, result)
    except Exception as e:
        progress_manager.fail_job(job_id, f"Failed to cluster: {str(e)}")

@router.post("/hr/rank/start")
async def start_rank_candidates(
    background_tasks: BackgroundTasks,
    cvs: List[UploadFile] = File(...),
    job_description: str = Form(...),
    domain: str = Form("general")
):
    REQUEST_COUNT.labels(endpoint="hr_rank_start").inc()
    HR_RANKING_COUNT.inc()
    
    cv_files = []
    for cv in cvs:
        file_bytes = await cv.read()
        cv_files.append((file_bytes, cv.filename))
        
    job_id = progress_manager.create_job()
    background_tasks.add_task(
        run_hr_rank_task,
        job_id,
        cv_files,
        job_description,
        domain
    )
    return {"job_id": job_id}

@router.post("/hr/cluster/start")
async def start_cluster_candidates(
    background_tasks: BackgroundTasks,
    cvs: List[UploadFile] = File(...),
    num_clusters: int = Form(3)
):
    REQUEST_COUNT.labels(endpoint="hr_cluster_start").inc()
    CLUSTERING_COUNT.inc()
    
    cv_files = []
    for cv in cvs:
        file_bytes = await cv.read()
        cv_files.append((file_bytes, cv.filename))
        
    job_id = progress_manager.create_job()
    background_tasks.add_task(
        run_hr_cluster_task,
        job_id,
        cv_files,
        num_clusters
    )
    return {"job_id": job_id}