import mlflow
from pathlib import Path

EXPERIMENT_NAME = "CV-Matcher-Pro"


def setup_experiment():

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )


def log_run(
    run_name: str,
    params: dict = None,
    metrics: dict = None,
    artifacts: list = None
):

    setup_experiment()

    with mlflow.start_run(
        run_name=run_name
    ):

        # PARAMETERS

        if params:

            for key, value in params.items():

                mlflow.log_param(
                    key,
                    value
                )

        # METRICS

        if metrics:

            for key, value in metrics.items():

                try:
                    mlflow.log_metric(
                        key,
                        float(value)
                    )
                except:
                    pass

        # ARTIFACTS

        if artifacts:

            for artifact in artifacts:

                if Path(artifact).exists():

                    mlflow.log_artifact(
                        str(artifact)
                    )


def log_training_run(
    config,
    metrics,
    model_path
):

    params = {

        "epochs":
            config["training"]["epochs"],

        "batch_size":
            config["training"]["batch_size"],

        "dataset_version":
            config["evaluation"]["dataset_version"],

        "num_triplets":
            config["dataset"]["num_triplets"]
    }

    setup_experiment()

    with mlflow.start_run(
        run_name="training_pipeline"
    ):

        for k, v in params.items():

            mlflow.log_param(
                k,
                v
            )

        for k, v in metrics.items():

            mlflow.log_metric(
                k,
                float(v)
            )

        if Path(model_path).exists():

            mlflow.log_artifacts(
                model_path,
                artifact_path="model"
            )