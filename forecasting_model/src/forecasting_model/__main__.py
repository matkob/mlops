"""forecasting_model file for ensuring the package is executable
as `forecasting_model` and `python -m forecasting_model`
"""
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from click import Command, Group, MultiCommand

from kedro.framework.cli.utils import KedroCliError, load_entry_points
from kedro.framework.project import configure_project


def _find_run_command(package_name: str) -> Command:
    try:
        project_cli = importlib.import_module(f"{package_name}.cli")
        # fail gracefully if cli.py does not exist
    except ModuleNotFoundError as exc:
        if f"{package_name}.cli" not in str(exc):
            raise
        plugins = load_entry_points("project")
        run = _find_run_command_in_plugins(plugins) if plugins else None
        if run:
            # use run command from installed plugin if it exists
            return run
        # use run command from the framework project
        import kedro.framework.cli.project as project

        return project.run
    # fail badly if cli.py exists, but has no `cli` in it
    if not hasattr(project_cli, "cli") or not isinstance(project_cli.run, Command):
        raise KedroCliError(f"Cannot load commands from {package_name}.cli")
    return project_cli.run


def _find_run_command_in_plugins(plugins: Sequence[MultiCommand]) -> Optional[Command]:
    for group in plugins:
        if isinstance(group, Group) and "run" in group.commands:
            return group.commands["run"]
    return None


def main(*args: List[Any], **kwargs: Dict[str, Any]) -> None:
    package_name = Path(__file__).parent.name
    configure_project(package_name)
    run = _find_run_command(package_name)
    run(*args, **kwargs)


if __name__ == "__main__":
    main()
