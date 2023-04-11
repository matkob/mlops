from pathlib import Path
from doit.action import CmdAction
from doit.tools import run_once
from doit import task_params

DOIT_CONFIG = {"verbosity": 2}


def task_code():  # type: ignore
    code_files = list(Path(".").glob("**/*.(py|tf)"))
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
        "actions": [CmdAction("mypy . --strict --ignore-missing-imports")],
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
    }

    if visualize:
        yield {
            "name": "visualize",
            "file_dep": model_files,
            "actions": [CmdAction("kedro viz", cwd="forecasting_model")],
        }


def task_data():  # type: ignore
    data_dir = "raw_data"
    data_file = "order_book.csv"
    url = "https://datasets.tardis.dev/v1/binance/book_snapshot_5/2023/03/01/BTCUSDT.csv.gz"  # noqa: E501

    def rename_columns():
        import pandas as pd

        def fix_column_name(column: str):
            return (
                column
                    .replace("[", "_")
                    .replace("].", "_")
            )
        
        f = f"{data_dir}/{data_file}"
        pd.read_csv(f).rename(columns=fix_column_name).to_csv(f, index=False)

    yield {
        "name": "init",
        "targets": [data_dir],
        "actions": [CmdAction(f"mkdir {data_dir} || echo 'Dir already present'")],
        "uptodate": [run_once],
        "verbosity": 0,
    }

    yield {
        "name": "download",
        "targets": [f"{data_dir}/{data_file}"],
        "actions": [CmdAction(f"curl {url} | gunzip -c > {data_dir}/{data_file}")],
        "uptodate": [run_once],
        "verbosity": 0,
        "task_dep": ["data:init"],
    }

    yield {
        "name": "prepare",
        "targets": [
            f"infrastructure/data/{data_file}",
            f"forecasting_model/data/01_raw/{data_file}",
        ],
        "actions": [
            (rename_columns,),
            CmdAction(f"cp {data_dir}/{data_file} infrastructure/data/{data_file}"),
            CmdAction(f"cp {data_dir}/{data_file} forecasting_model/data/01_raw/{data_file}"),
        ],
        "task_dep": ["data:download"],
    }

    # TODO: Add a step to inject fabricated target values
