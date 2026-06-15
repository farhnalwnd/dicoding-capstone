from typing import List, Dict


def get_recommendation_level(score: float) -> str:

    if score >= 85:
        return "Strong Match"

    elif score >= 70:
        return "Good Match"

    elif score >= 50:
        return "Moderate Match"

    return "Low Match"


def generate_reasoning(
    matched_count: int,
    missing_count: int,
    recommendation: str
):

    reasons = []

    reasons.append(
        f"Candidate matches {matched_count} required skills."
    )

    if missing_count > 0:
        reasons.append(
            f"Candidate is missing {missing_count} required skills."
        )

    reasons.append(
        f"Overall recommendation: {recommendation}."
    )

    return reasons


def build_match_explanation(
    similarity_score: float,
    matched_skills: List[str],
    missing_skills: List[str]
) -> Dict:

    total_skills = (
        len(matched_skills)
        + len(missing_skills)
    )

    coverage_ratio = 0.0

    if total_skills > 0:
        coverage_ratio = (
            len(matched_skills)
            / total_skills
        ) * 100

    recommendation = get_recommendation_level(
        similarity_score
    )

    return {

        "match_score": round(
            similarity_score,
            2
        ),

        "recommendation":
            recommendation,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "matched_skills_count":
            len(matched_skills),

        "missing_skills_count":
            len(missing_skills),

        "skill_coverage_ratio":
            round(
                coverage_ratio,
                2
            ),

        "reasoning":
            generate_reasoning(
                len(matched_skills),
                len(missing_skills),
                recommendation
            )
    }