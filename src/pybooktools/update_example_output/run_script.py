# run_script.py
import os
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

from pybooktools.util.console import console
from pybooktools.util.display import warn
from rich.syntax import Syntax


def get_virtual_env_python() -> str:
    """
    Return the Python interpreter path from the virtual environment if available
    """
    venv_path = os.getenv("VIRTUAL_ENV")
    if venv_path:
        python_path = (
            Path(venv_path)
            / ("Scripts" if os.name == "nt" else "bin")
            / "python"
        )
        return str(python_path)
    return sys.executable


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
