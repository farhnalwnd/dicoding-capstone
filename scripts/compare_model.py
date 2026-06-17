import sys
from pathlib import Path

# =====================================================
# PATH SETUP
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "backend"))

import json
from datetime import datetime

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from training.mlflow_utils import (
    log_run
)

from app.services.evaluation import (
    evaluate_multiple_queries
)

# =====================================================
# CONFIG
# =====================================================

DATA_DIR = (
    ROOT_DIR
    / "data"
    / "evaluation"
    / "v4"
)

REPORT_DIR = ROOT_DIR / "reports"
REPORT_DIR.mkdir(
    exist_ok=True
)

REPORT_FILE = (
    REPORT_DIR
    / "experiment_comparison.json"
)

BASELINE_MODEL = (
    "paraphrase-multilingual-MiniLM-L12-v2"
)

FINETUNED_MODEL = str(
    ROOT_DIR
    / "models"
    / "bi-encoder-cv-matcher"
)

TOP_K = 5

# =====================================================
# LOAD DATA
# =====================================================

print("Loading dataset...")

cvs_df = pd.read_csv(
    DATA_DIR / "cvs.csv"
)

jobs_df = pd.read_csv(
    DATA_DIR / "jobs.csv"
)

labels_df = pd.read_csv(
    DATA_DIR / "cv_jd_labeled.csv"
)

print(
    f"CVs: {len(cvs_df)} | "
    f"Jobs: {len(jobs_df)} | "
    f"Labels: {len(labels_df)}"
)

# =====================================================
# BUILD TEXT
# =====================================================

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

# =====================================================
# EVALUATION FUNCTION
# =====================================================

def evaluate_model(model_name):

    print("\n" + "=" * 50)
    print(f"Evaluating: {model_name}")
    print("=" * 50)

    model = SentenceTransformer(
        model_name
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

    rankings = []

    for job_idx, job_row in jobs_df.iterrows():

        jd_id = job_row["jd_id"]

        similarities = cosine_similarity(
            [job_embeddings[job_idx]],
            cv_embeddings
        )[0]

        candidates = []

        for cv_idx, cv_row in cvs_df.iterrows():

            cv_id = cv_row["cv_id"]

            label_row = labels_df[
                (labels_df["cv_id"] == cv_id)
                &
                (labels_df["jd_id"] == jd_id)
            ]

            relevance = (
                int(label_row.iloc[0]["relevance"])
                if not label_row.empty
                else 0
            )

            candidates.append({
                "cv_id": cv_id,
                "score": float(
                    similarities[cv_idx]
                ),
                "relevance": relevance
            })

        candidates = sorted(
            candidates,
            key=lambda x: x["score"],
            reverse=True
        )

        rankings.append({
            "relevance_scores": [
                c["relevance"]
                for c in candidates
            ],
            "predicted_scores": [
                c["score"]
                for c in candidates
            ]
        })

    metrics = evaluate_multiple_queries(
        rankings=rankings,
        k=TOP_K
    )

    return metrics

# =====================================================
# IMPROVEMENT
# =====================================================

def calc_improvement(
    baseline_value,
    finetuned_value
):

    if baseline_value == 0:
        return 0.0

    return round(
        (
            (
                finetuned_value
                - baseline_value
            )
            / baseline_value
        ) * 100,
        2
    )

# =====================================================
# RUN
# =====================================================

baseline_metrics = evaluate_model(
    BASELINE_MODEL
)

finetuned_metrics = evaluate_model(
    FINETUNED_MODEL
)

improvement = {
    "precision_at_k_percent":
        calc_improvement(
            baseline_metrics["precision_at_k"],
            finetuned_metrics["precision_at_k"]
        ),

    "recall_at_k_percent":
        calc_improvement(
            baseline_metrics["recall_at_k"],
            finetuned_metrics["recall_at_k"]
        ),

    "mrr_percent":
        calc_improvement(
            baseline_metrics["mrr"],
            finetuned_metrics["mrr"]
        ),

    "ndcg_at_k_percent":
        calc_improvement(
            baseline_metrics["ndcg_at_k"],
            finetuned_metrics["ndcg_at_k"]
        )
}

# =====================================================
# REPORT
# =====================================================

report = {
    "timestamp":
        datetime.now().isoformat(),

    "dataset_version":
        DATA_DIR.name if DATA_DIR.name != "evaluation" else "v1",

    "baseline": {
        "model":
            BASELINE_MODEL,
        **baseline_metrics
    },

    "finetuned": {
        "model":
            FINETUNED_MODEL,
        **finetuned_metrics
    },

    "improvement":
        improvement
}



with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        report,
        f,
        indent=4,
        ensure_ascii=False
    )
    log_run(
    run_name="model_comparison",
    params={
        "dataset_version": "v4"
    },
    metrics={

        "baseline_precision":
            baseline_metrics["precision_at_k"],

        "baseline_recall":
            baseline_metrics["recall_at_k"],

        "baseline_mrr":
            baseline_metrics["mrr"],

        "baseline_ndcg":
            baseline_metrics["ndcg_at_k"],

        "finetuned_precision":
            finetuned_metrics["precision_at_k"],

        "finetuned_recall":
            finetuned_metrics["recall_at_k"],

        "finetuned_mrr":
            finetuned_metrics["mrr"],

        "finetuned_ndcg":
            finetuned_metrics["ndcg_at_k"]
    },
    artifacts=[
        REPORT_FILE
    ]
)

# =====================================================
# CONSOLE OUTPUT
# =====================================================

print("\n" + "=" * 60)
print("EXPERIMENT COMPARISON")
print("=" * 60)

print("\nBASELINE")
print(
    json.dumps(
        baseline_metrics,
        indent=4
    )
)

print("\nFINETUNED")
print(
    json.dumps(
        finetuned_metrics,
        indent=4
    )
)

print("\nIMPROVEMENT (%)")
print(
    json.dumps(
        improvement,
        indent=4
    )
)

print("\nSaved to:")
print(REPORT_FILE)