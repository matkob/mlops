from pathlib import Path
from doit.action import CmdAction
from doit.tools import run_once
from doit import task_params

DOIT_CONFIG = {"verbosity": 2}


def task_code():  # type: ignore
    python_files = list(Path(".").glob("**/*.py"))
    yield {
        "name": "format",
        "file_dep": python_files,
        "actions": [CmdAction("black .")],
    }

    yield {
        "name": "stylecheck",
        "file_dep": python_files,
        "actions": [CmdAction("flake8 .")],
    }

    yield {
        "name": "typecheck",
        "file_dep": python_files,
        "actions": [CmdAction("mypy . --strict --ignore-missing-imports")],
    }


@task_params([{"name": "visualize", "default": False, "type": bool, "long": "visualize"}])  # type: ignore
def task_model(visualize: bool):
    local_mlflow_config = "spaceflights/conf/local/mlflow.yml"
    local_credentials = "spaceflights/conf/local/credentials.yml"

    model_files = list(Path("spaceflights").glob("**/*.py")) + [
        local_mlflow_config,
        local_credentials,
    ]

    yield {
        "name": "init",
        "actions": [
            CmdAction("kedro mlflow init", cwd="spaceflights"),
            CmdAction(f"touch {local_credentials}"),
        ],
        "targets": [local_mlflow_config, local_credentials],
        "uptodate": [run_once],
    }

    yield {
        "name": "test",
        "file_dep": model_files,
        "actions": [CmdAction("pytest", cwd="spaceflights")],
    }

    yield {
        "name": "run",
        "file_dep": model_files,
        "actions": [CmdAction("kedro run", cwd="spaceflights")],
    }

    if visualize:
        yield {
            "name": "visualize",
            "file_dep": model_files,
            "actions": [CmdAction("kedro viz", cwd="spaceflights")],
        }


def task_data():
    data_dir = "raw_data"
    data_file = "order_book.csv"
    url = "https://datasets.tardis.dev/v1/binance/book_snapshot_5/2023/03/01/BTCUSDT.csv.gz"

    yield {
        "name": "init",
        "targets": [data_dir],
        "actions": [CmdAction(f"mkdir {data_dir} || echo 'Dir already present'")],
        "uptodate": [run_once],
        "verbosity": 0
    }

    yield {
        "name": "download",
        "targets": [f"{data_dir}/{data_file}"],
        "actions": [CmdAction(f"curl {url} | gunzip -c > {data_dir}/{data_file}")],
        "uptodate": [run_once],
        "verbosity": 0,
        "task_dep": ["data:init"]
    }

    yield {
        "name": "prepare",
        "targets": [f"infrastructure/data/{data_file}", f"spaceflights/data/01_raw/{data_file}"],
        "actions": [CmdAction(f"cp {data_dir}/{data_file} infrastructure/data/{data_file}"), CmdAction(f"cp {data_dir}/{data_file} spaceflights/data/01_raw/{data_file}")],
        "task_dep": ["data:download"]
    }

    # TODO: Add a step to inject fabricated target values
