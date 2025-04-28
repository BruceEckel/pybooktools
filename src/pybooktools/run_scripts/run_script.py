# run_script.py
import os
import subprocess
from pathlib import Path
from typing import NamedTuple

from rich.syntax import Syntax

from pybooktools.run_scripts.get_virtual_environment import get_virtual_env_python
from pybooktools.util.console import console
from pybooktools.util.display import warn


class ScriptResult(NamedTuple):
    returncode: int
    result_value: str


def run_script(script_path: Path) -> ScriptResult:
    """
    Runs the script in its virtual environment and returns the output.
    Ensures the script's parent directory is on PYTHONPATH so it can import from its parent.
    """
    env = os.environ.copy()
    parent_dir = script_path.parent.parent.resolve()
    env["PYTHONPATH"] = f"{parent_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"

    result = subprocess.run(
        [get_virtual_env_python(), str(script_path)],
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        warn(f"Error running script {script_path}")
        syntax = Syntax(
            script_path.read_text(encoding="utf-8"),
            "python",
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)
        warn(f"{result.stderr}")
        return ScriptResult(result.returncode, result.stderr)
    else:
        return ScriptResult(result.returncode, result.stdout)
