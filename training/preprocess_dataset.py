from pathlib import Path

import pandas as pd

import sys

# =====================================================
# PROJECT ROOT
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "backend"))

from backend.app.services.preprocessing import (
    preprocess_dataframe,
    dataset_statistics
)

# =====================================================
# CONFIG
# =====================================================

RAW_DIR = ROOT_DIR / "data" / "raw"

PROCESSED_DIR = (
    ROOT_DIR
    / "data"
    / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# FILES
# =====================================================

INPUT_FILES = [
    "cvs.csv",
    "jobs.csv"
]

# =====================================================
# MAIN
# =====================================================

def process_file(file_name: str):

    input_path = RAW_DIR / file_name

    if not input_path.exists():

        print(
            f"[SKIP] File not found: {input_path}"
        )

        return

    print(
        f"\nProcessing {file_name}"
    )

    df = pd.read_csv(input_path)

    text_column = None

    possible_columns = [
        "cv_text",
        "jd_text",
        "text",
        "description",
        "content"
    ]

    for col in possible_columns:

        if col in df.columns:

            text_column = col
            break

    if text_column is None:

        print(
            f"[SKIP] No text column found"
        )

        return

    stats_before = dataset_statistics(
        df,
        text_column
    )

    df = preprocess_dataframe(
        df,
        text_column
    )

    output_path = (
        PROCESSED_DIR
        / file_name
    )

    df.to_csv(
        output_path,
        index=False
    )

    stats_after = dataset_statistics(
        df,
        "processed_text"
    )

    print(
        f"Saved: {output_path}"
    )

    print(
        f"Rows: {stats_after['rows']}"
    )

    print(
        f"Words avg: "
        f"{stats_before['avg_words']} -> "
        f"{stats_after['avg_words']}"
    )


def main():

    print("=" * 60)
    print("DATASET PREPROCESSING")
    print("=" * 60)

    for file_name in INPUT_FILES:

        process_file(file_name)

    print("\nDone.")
    print(
        f"Processed data saved to:"
    )
    print(PROCESSED_DIR)


if __name__ == "__main__":
    main()