from typing import Dict, List

import numpy as np
from sklearn.metrics import ndcg_score

RELEVANCE_THRESHOLD = 2
# =====================================================
# Precision@K
# =====================================================


def precision_at_k(relevance_scores: List[int], k: int = 5) -> float:
    """
    relevance_scores:
    ranked relevance list
    example:
    [3, 3, 1, 0, 0]

    relevant = score > 0
    """

    if len(relevance_scores) == 0:
        return 0.0

    top_k = relevance_scores[:k]

    relevant_count = sum(1 for r in top_k if r > RELEVANCE_THRESHOLD)

    return relevant_count / k


# =====================================================
# Recall@K
# =====================================================


def recall_at_k(relevance_scores: List[int], total_relevant: int, k: int = 5) -> float:
    if total_relevant == 0:
        return 0.0

    top_k = relevance_scores[:k]

    retrieved_relevant = sum(1 for r in top_k if r > RELEVANCE_THRESHOLD)

    return retrieved_relevant / total_relevant


# =====================================================
# Reciprocal Rank
# =====================================================


def reciprocal_rank(relevance_scores: List[int]) -> float:
    for idx, score in enumerate(relevance_scores, start=1):
        if score > RELEVANCE_THRESHOLD:
            return 1.0 / idx

    return 0.0


# =====================================================
# Mean Reciprocal Rank
# =====================================================


def mean_reciprocal_rank(all_rankings: List[List[int]]) -> float:
    if not all_rankings:
        return 0.0

    rr_scores = [reciprocal_rank(ranking) for ranking in all_rankings]

    return float(np.mean(rr_scores))


# =====================================================
# NDCG
# =====================================================


def ndcg_at_k(
    true_relevance: List[int], predicted_scores: List[float], k: int = 10
) -> float:
    if len(true_relevance) == 0:
        return 0.0

    y_true = np.asarray([true_relevance])
    y_score = np.asarray([predicted_scores])

    return float(ndcg_score(y_true, y_score, k=k))


# =====================================================
# Full Ranking Evaluation
# =====================================================


def evaluate_ranking(
    relevance_scores: List[int], predicted_scores: List[float], k: int = 5
) -> Dict:
    precision = precision_at_k(relevance_scores, k=k)

    total_relevant = sum(1 for r in relevance_scores if r > RELEVANCE_THRESHOLD)

    recall = recall_at_k(relevance_scores, total_relevant, k=k)

    rr = reciprocal_rank(relevance_scores)

    ndcg = ndcg_at_k(relevance_scores, predicted_scores, k=k)

    return {
        "precision_at_k": round(precision, 4),
        "recall_at_k": round(recall, 4),
        "reciprocal_rank": round(rr, 4),
        "ndcg_at_k": round(ndcg, 4),
    }


# =====================================================
# Aggregate Evaluation
# =====================================================


def evaluate_multiple_queries(rankings: List[Dict], k: int = 5) -> Dict:
    precisions = []
    recalls = []
    reciprocal_ranks = []
    ndcgs = []

    for item in rankings:
        relevance_scores = item["relevance_scores"]
        predicted_scores = item["predicted_scores"]

        result = evaluate_ranking(
            relevance_scores=relevance_scores, predicted_scores=predicted_scores, k=k
        )

        precisions.append(result["precision_at_k"])

        recalls.append(result["recall_at_k"])

        reciprocal_ranks.append(result["reciprocal_rank"])

        ndcgs.append(result["ndcg_at_k"])

    return {
        "precision_at_k": round(float(np.mean(precisions)), 4),
        "recall_at_k": round(float(np.mean(recalls)), 4),
        "mrr": round(float(np.mean(reciprocal_ranks)), 4),
        "ndcg_at_k": round(float(np.mean(ndcgs)), 4),
    }
