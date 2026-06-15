import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "backend"))

import subprocess
import yaml

from training.mlflow_utils import (
    log_training_run
)

CONFIG_FILE = ROOT_DIR / "training" / "config.yaml"


def load_config():

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


def run_command(cmd):

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()

    if process.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}"
        )


def main():

    config = load_config()

    print("=" * 60)
    print("CV MATCHER TRAINING PIPELINE")
    print("=" * 60)

    print("\n[1/4] Generate Dataset")

    run_command([
        sys.executable,
        str(
            ROOT_DIR
            / "training"
            / "scripts"
            / "generate_dataset_v2.py"
        ),
        "--skills_dir",
        str(
            ROOT_DIR
            / config["paths"]["skills_dir"]
        ),
        "--templates_dir",
        str(
            ROOT_DIR
            / config["paths"]["templates_dir"]
        ),
        "--output_dir",
        str(
            ROOT_DIR
            / "data"
            / "training"
        ),
        "--num_triplets",
        str(
            config["dataset"]["num_triplets"]
        )
    ])

    print("\n[2/4] Preprocess Dataset")

    run_command([
        sys.executable,
        str(
            ROOT_DIR
            / "training"
            / "preprocess_dataset.py"
        )
    ])

    print("\n[3/4] Train Bi Encoder")

    run_command([
        sys.executable,
        str(
            ROOT_DIR
            / "training"
            / "scripts"
            / "train_bi_encoder.py"
        ),
        "--train_csv",
        str(
            ROOT_DIR
            / "data"
            / "training"
            / "bi_encoder_train.csv"
        ),
        "--output_path",
        str(
            ROOT_DIR
            / config["model"]["output_path"]
        ),
        "--epochs",
        str(
            config["training"]["epochs"]
        ),
        "--batch_size",
        str(
            config["training"]["batch_size"]
        )
    ])

    print("\n[4/4] Evaluate Model")

    run_command([
        sys.executable,
        str(
            ROOT_DIR
            / "scripts"
            / "evaluate_model.py"
        )
    ])

    # =====================================================
    # MLflow Logging
    # =====================================================

    print("\nLogging to MLflow...")

    report_file = (
        ROOT_DIR
        / "reports"
        / "evaluation_report.json"
    )

    if report_file.exists():

        with open(
            report_file,
            "r",
            encoding="utf-8"
        ) as f:

            report = json.load(f)

        log_training_run(
            config=config,
            metrics=report["metrics"],
            model_path=str(
                ROOT_DIR
                / config["model"]["output_path"]
            )
        )

        print("MLflow logging completed.")

    else:

        print(
            "Warning: evaluation_report.json not found."
        )

    print(
        "\nPipeline completed successfully."
    )


if __name__ == "__main__":
    main()