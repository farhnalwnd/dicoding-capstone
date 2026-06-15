import os
import sys
from pathlib import Path

# Setup paths
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "backend"))

import numpy as np
import pandas as pd
import json

from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from training.mlflow_utils import (
    log_run
)

# =====================================================
# Import evaluation service
# =====================================================

REPORT_DIR = ROOT_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

REPORT_FILE = REPORT_DIR / "evaluation_report.json"

from app.services.evaluation import (
    evaluate_multiple_queries
)

# =====================================================
# Config
# =====================================================

DATA_DIR = ROOT_DIR / "data" / "evaluation" / "v4"

CV_FILE = DATA_DIR / "cvs.csv"
JOB_FILE = DATA_DIR / "jobs.csv"
LABEL_FILE = DATA_DIR / "cv_jd_labeled.csv"

MODEL_NAME = os.getenv(
    "MODEL_BI_ENCODER",
    "paraphrase-multilingual-MiniLM-L12-v2"
)

TOP_K = 5

# =====================================================
# Load Dataset
# =====================================================

print("Loading dataset...")

cvs_df = pd.read_csv(CV_FILE)
jobs_df = pd.read_csv(JOB_FILE)
labels_df = pd.read_csv(LABEL_FILE)

print(f"CVs    : {len(cvs_df)}")
print(f"Jobs   : {len(jobs_df)}")
print(f"Labels : {len(labels_df)}")

# =====================================================
# Load Model
# =====================================================

print(f"\nLoading model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)

# =====================================================
# Build Text
# =====================================================

print("\nGenerating embeddings...")

if "cv_text" in cvs_df.columns:
    cvs_df["text"] = cvs_df["cv_text"].fillna("")
else:
    cvs_df["text"] = (
        cvs_df["target_role"].fillna("")
        + " "
        + cvs_df["skills"].fillna("")
    )

if "jd_text" in jobs_df.columns:
    jobs_df["text"] = jobs_df["jd_text"].fillna("")
else:
    jobs_df["text"] = (
        jobs_df["title"].fillna("")
        + " "
        + jobs_df["required_skills"].fillna("")
    )

cv_embeddings = model.encode(
    cvs_df["text"].tolist(),
    convert_to_numpy=True,
    show_progress_bar=True
)

job_embeddings = model.encode(
    jobs_df["text"].tolist(),
    convert_to_numpy=True,
    show_progress_bar=True
)

# =====================================================
# Evaluation
# =====================================================

print("\nRunning evaluation...")

rankings = []

for job_idx, job_row in jobs_df.iterrows():

    jd_id = job_row["jd_id"]

    jd_embedding = job_embeddings[job_idx]

    similarities = cosine_similarity(
        [jd_embedding],
        cv_embeddings
    )[0]

    candidate_results = []

    for cv_idx, cv_row in cvs_df.iterrows():

        cv_id = cv_row["cv_id"]

        label_row = labels_df[
            (labels_df["cv_id"] == cv_id)
            &
            (labels_df["jd_id"] == jd_id)
        ]

        if label_row.empty:
            relevance = 0
        else:
            relevance = int(
                label_row.iloc[0]["relevance"]
            )

        candidate_results.append({
            "cv_id": cv_id,
            "score": float(similarities[cv_idx]),
            "relevance": relevance
        })

    candidate_results = sorted(
        candidate_results,
        key=lambda x: x["score"],
        reverse=True
    )

    relevance_scores = [
        item["relevance"]
        for item in candidate_results
    ]

    predicted_scores = [
        item["score"]
        for item in candidate_results
    ]

    rankings.append({
        "relevance_scores": relevance_scores,
        "predicted_scores": predicted_scores
    })

# =====================================================
# Metrics
# =====================================================

metrics = evaluate_multiple_queries(
    rankings=rankings,
    k=TOP_K
)

def get_metrics():
    return {
        "precision_at_k": float(metrics["precision_at_k"]),
        "recall_at_k": float(metrics["recall_at_k"]),
        "mrr": float(metrics["mrr"]),
        "ndcg_at_k": float(metrics["ndcg_at_k"])
    }

# =====================================================
# Result
# =====================================================

print("\n" + "=" * 50)
print("MODEL EVALUATION RESULT")
print("=" * 50)

print(
    f"Precision@{TOP_K}: "
    f"{metrics['precision_at_k']:.4f}"
)

print(
    f"Recall@{TOP_K}: "
    f"{metrics['recall_at_k']:.4f}"
)

print(
    f"MRR: "
    f"{metrics['mrr']:.4f}"
)

print(
    f"NDCG@{TOP_K}: "
    f"{metrics['ndcg_at_k']:.4f}"
)

print("=" * 50)

# =====================================================
# Save Report
# =====================================================

dataset_version = DATA_DIR.name if DATA_DIR.name != "evaluation" else "v1"

report = {
    "timestamp": datetime.now().isoformat(),
    "model": MODEL_NAME,
    "dataset_version": dataset_version,
    "num_cvs": len(cvs_df),
    "num_jobs": len(jobs_df),
    "num_labels": len(labels_df),
    "top_k": TOP_K,
    "metrics": {
        "precision_at_k": metrics["precision_at_k"],
        "recall_at_k": metrics["recall_at_k"],
        "mrr": metrics["mrr"],
        "ndcg_at_k": metrics["ndcg_at_k"]
    }
}

log_run(
    run_name=f"evaluation_{dataset_version}",
    params={
        "model": MODEL_NAME,
        "dataset_version": dataset_version,
        "top_k": TOP_K
    },
    metrics=report["metrics"],
    artifacts=[
        REPORT_FILE
    ]
    
)
print("MLflow evaluation logged.")

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        report,
        f,
        indent=4,
        ensure_ascii=False
    )

print(f"\nReport saved to:")
print(REPORT_FILE)

if __name__ == "__main__":
    pass