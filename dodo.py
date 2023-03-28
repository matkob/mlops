from pathlib import Path
from typing import Any, Dict, List
from doit.action import CmdAction


def task_check_and_format_code() -> Dict[str, List[Any]]:
    """Check and fix code format, typing and style."""

    def check_types() -> str:
        return "mypy . --strict --ignore-missing-imports"

    def format_code() -> str:
        return "black ."

    def check_style() -> str:
        return "flake8 ."

    return {
        "file_dep": list(Path(".").glob("**/*.py")),
        "actions": [
            CmdAction(check_types),
            CmdAction(format_code),
            CmdAction(check_style),
        ],
    }


def task_test_model() -> Dict[str, List[Any]]:
    def run_pytest() -> str:
        return "cd spaceflights && pytest"

    return {
        "file_dep": list(Path("spaceflights").glob("**/*.py")),
        "actions": [
            CmdAction(run_pytest),
        ],
    }


def task_check_all() -> Dict[str, List[Any]]:
    return {
        "uptodate": [False],
        "actions": [],
        "task_dep": ["check_and_format_code", "test_model"],
    }
