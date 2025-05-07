# run_one_script.py
import os
import subprocess
from pathlib import Path

from rich.syntax import Syntax

from pybooktools.run_scripts.get_virtual_environment import get_virtual_env_python
from pybooktools.run_scripts.script_result import ScriptResult
from pybooktools.util.console import console
from pybooktools.util.display import warn


def run_script(script_path: Path) -> ScriptResult:
    """
    Runs the script in its virtual environment and returns the output.
    Ensures the script's parent directory is on PYTHONPATH so it can import from its parent.
    """
    python_exec = get_virtual_env_python()

    env = os.environ.copy()
    parent_dir = script_path.parent.parent.resolve()
    env["PYTHONPATH"] = f"{parent_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"

    result = subprocess.run(
        [python_exec, str(script_path)],
        capture_output=True,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        err_msg = f"Error running script {script_path}, {result.stderr}"
        warn(err_msg)
        syntax = Syntax(
            script_path.read_text(encoding="utf-8"),
            "python",
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)
        return ScriptResult(result.returncode, err_msg)

    return ScriptResult(0, result.stdout)
