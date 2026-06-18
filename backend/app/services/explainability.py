from typing import Dict, List


def get_recommendation_level(score: float) -> str:
    if score >= 85:
        return "Strong Match"

    elif score >= 70:
        return "Good Match"

    elif score >= 50:
        return "Moderate Match"

    return "Low Match"


def generate_reasoning(matched_count: int, missing_count: int, recommendation: str):
    reasons = []

    reasons.append(f"Candidate matches {matched_count} required skills.")

    if missing_count > 0:
        reasons.append(f"Candidate is missing {missing_count} required skills.")

    reasons.append(f"Overall recommendation: {recommendation}.")

    return reasons


def build_match_explanation(
    similarity_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    domain_relevance: float = 0.0,
) -> Dict:
    total_skills = len(matched_skills) + len(missing_skills)

    coverage_ratio = 0.0

    if total_skills > 0:
        coverage_ratio = (len(matched_skills) / total_skills) * 100

    # Skill reliability penalty:
    # JDs with very few skills detected are less reliable signals.
    # A JD must have at least 8 skills to get full coverage weight.
    # This aggressively penalizes short/generic JDs (e.g. only 2 skills).
    MIN_RELIABLE_SKILLS = 8
    skill_reliability = min(1.0, total_skills / MIN_RELIABLE_SKILLS)
    effective_coverage = coverage_ratio * skill_reliability

    # Hybrid match score:
    # 70% Semantic similarity (CV vs JD text)
    # 10% Skill coverage (reliability-adjusted — penalizes JDs with < 8 skills)
    # 20% Domain relevance (how many domain skills CV actually contains)
    #
    # Domain relevance carries 2x more weight so that:
    # - An IT CV scores HIGHER against an IT JD than a Finance/HR JD
    # - JDs with very few skills cannot inflate coverage to beat domain-aligned JDs
    final_score = (
        (similarity_score * 0.70)
        + (effective_coverage * 0.10)
        + (domain_relevance * 0.20)
    )
    final_score = round(final_score, 2)

    recommendation = get_recommendation_level(final_score)

    result = {
        "match_score": final_score,
        "recommendation": recommendation,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_skills_count": len(matched_skills),
        "missing_skills_count": len(missing_skills),
        "skill_coverage_ratio": round(coverage_ratio, 2),
        "reasoning": generate_reasoning(
            len(matched_skills), len(missing_skills), recommendation
        ),
    }

    # Record the final match score in Prometheus
    from app.core.metrics import MATCH_SCORE_DISTRIBUTION

    MATCH_SCORE_DISTRIBUTION.observe(final_score)

    return result
