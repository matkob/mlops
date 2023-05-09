from pathlib import Path
from doit.action import CmdAction
from doit.tools import run_once
from doit import task_params

DOIT_CONFIG = {"verbosity": 2}

GCP_REGISTRY = "europe-west1-docker.pkg.dev"
GCP_PROJECT_ID = "mlops-383318"
MODEL_TRAINING_IMAGE = f"{GCP_REGISTRY}/{GCP_PROJECT_ID}/model/training"


def task_code():
    code_files = list(Path(".").glob("**/*.(py|tf)"))
    project_roots = [
        "forecasting_model",
        "infrastructure/functions/data-mock",
    ]

    yield {
        "name": "format",
        "file_dep": code_files,
        "actions": [
            CmdAction("black ."),
            CmdAction("terraform fmt -recursive", cwd="infrastructure"),
        ],
    }

    yield {
        "name": "stylecheck",
        "file_dep": code_files,
        "actions": [
            CmdAction("flake8 ."),
            CmdAction("terraform fmt -check -recursive", cwd="infrastructure"),
        ],
    }

    yield {
        "name": "typecheck",
        "file_dep": code_files,
        "actions": [
            CmdAction(f"mypy {path} --strict --ignore-missing-imports")
            for path in project_roots
        ],
    }


@task_params([{"name": "visualize", "default": False, "type": bool, "long": "visualize"}])  # type: ignore # noqa: E501
def task_model(visualize: bool):
    local_mlflow_config = "forecasting_model/conf/local/mlflow.yml"
    local_credentials = "forecasting_model/conf/local/credentials.yml"

    model_files = list(Path("forecasting_model").glob("**/*.py")) + [
        local_mlflow_config,
        local_credentials,
    ]

    yield {
        "name": "init",
        "actions": [
            CmdAction("kedro mlflow init", cwd="forecasting_model"),
            CmdAction(f"touch {local_credentials}"),
        ],
        "targets": [local_mlflow_config, local_credentials],
        "uptodate": [run_once],
    }

    yield {
        "name": "test",
        "file_dep": model_files,
        "task_dep": ["data:prepare"],
        "actions": [CmdAction("pytest", cwd="forecasting_model")],
    }

    yield {
        "name": "run",
        "file_dep": model_files,
        "task_dep": ["data:prepare"],
        "actions": [CmdAction("kedro run", cwd="forecasting_model")],
        "uptodate": [run_once],
    }

    if visualize:
        yield {
            "name": "visualize",
            "file_dep": model_files,
            "actions": [CmdAction("kedro viz", cwd="forecasting_model")],
            "uptodate": [run_once],
        }


def task_docker():
    model_files = list(Path("forecasting_model").glob("**/*.py"))

    yield {
        "name": "build",
        "file_dep": model_files,
        "actions": [
            CmdAction(
                f"docker build . -t {MODEL_TRAINING_IMAGE}:latest -f Dockerfile.train",
                cwd="forecasting_model",
            )
        ],
        "uptodate": [False],
    }

    yield {
        "name": "push",
        "task_dep": ["docker:build"],
        "actions": [CmdAction(f"docker push {MODEL_TRAINING_IMAGE}:latest")],
        "uptodate": [False],
    }


def task_data():
    data_dir = "raw_data"
    data_file = "order_book.csv"
    url = "https://datasets.tardis.dev/v1/binance/book_snapshot_5/2023/03/01/BTCUSDT.csv.gz"  # noqa: E501

    data_targets = [
        f"infrastructure/data/{data_file}",
        f"forecasting_model/data/01_raw/{data_file}",
    ]

    yield {
        "name": "init",
        "targets": [data_dir],
        "actions": [CmdAction(f"mkdir {data_dir} || echo 'Dir already present'")],
        "uptodate": [run_once],
        "verbosity": 0,
    }

    yield {
        "name": "download",
        "targets": [f"{data_dir}/{data_file}.raw"],
        "actions": [CmdAction(f"curl {url} | gunzip -c > {data_dir}/{data_file}.raw")],
        "uptodate": [run_once],
        "verbosity": 0,
        "task_dep": ["data:init"],
    }

    def rename_columns():
        import pandas as pd

        def map_column(column: str):
            return column.replace("[", "_").replace("].", "_")

        file_in = f"{data_dir}/{data_file}.raw"
        file_out = f"{data_dir}/{data_file}"
        pd.read_csv(file_in).rename(columns=map_column).to_csv(file_out, index=False)

    yield {
        "name": "process",
        "targets": [f"{data_dir}/{data_file}"],
        "actions": [
            (rename_columns,),
        ],
        "uptodate": [run_once],
        "verbosity": 0,
        "task_dep": ["data:init"],
    }

    yield {
        "name": "prepare",
        "targets": data_targets,
        "actions": [
            CmdAction(f"cp {data_dir}/{data_file} {target}") for target in data_targets
        ],
        "task_dep": ["data:process"],
    }
