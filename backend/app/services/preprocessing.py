import re
from typing import List

from app.services.parser import clean_text

# =====================================================
# NORMALIZATION
# =====================================================


def normalize_text(text: str) -> str:
    """
    Additional normalization after parser.clean_text()
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# PREPROCESS SINGLE TEXT
# =====================================================


def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline
    """

    text = clean_text(text)
    text = normalize_text(text)

    return text


# =====================================================
# BATCH PREPROCESS
# =====================================================


def preprocess_documents(documents: List[str]) -> List[str]:
    return [preprocess_text(doc) for doc in documents]


# =====================================================
# DATASET PREPROCESS
# =====================================================


def preprocess_dataframe(df, text_column: str):
    """
    Add processed_text column
    """

    df = df.copy()

    df["processed_text"] = df[text_column].fillna("").apply(preprocess_text)

    return df


# =====================================================
# SIMPLE SKILL COVERAGE
# =====================================================


def calculate_skill_coverage(
    matched_skills: List[str], missing_skills: List[str]
) -> float:
    total = len(matched_skills) + len(missing_skills)

    if total == 0:
        return 0.0

    return round((len(matched_skills) / total) * 100, 2)


# =====================================================
# DATASET STATISTICS
# =====================================================


def dataset_statistics(df, text_column: str):
    lengths = df[text_column].fillna("").astype(str).apply(lambda x: len(x.split()))

    return {
        "rows": len(df),
        "avg_words": round(lengths.mean(), 2),
        "min_words": int(lengths.min()),
        "max_words": int(lengths.max()),
    }
