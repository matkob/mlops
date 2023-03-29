from pathlib import Path
from doit.action import CmdAction
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


@task_params(
    [{"name": "visualize", "default": False, "type": bool, "long": "visualize"}]
)  # type: ignore
def task_model(visualize: bool):
    model_files = list(Path("spaceflights").glob("**/*.py"))
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
