# run_script.py
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple, Generator

from rich.syntax import Syntax

from pybooktools.run_scripts.get_virtual_environment import get_virtual_env_python
from pybooktools.util.console import console
from pybooktools.util.display import warn


class ScriptResult(NamedTuple):
    return_code: int
    result_value: str


def run_script(script_path: Path) -> ScriptResult:
    """
    Runs the script in its virtual environment and returns the output.
    Ensures the script's parent directory is on PYTHONPATH so it can import from its parent.
    """
    python_exec = get_virtual_env_python()
    # console.log(f"[dim]Using Python interpreter:[/] {python_exec}")

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

    return ScriptResult(result.returncode, result.stdout)


def run_scripts_parallel(
        scripts: Generator[Path, None, None] | list[Path],
        max_workers: int | None = None,
) -> list[ScriptResult]:
    """
    Takes a generator of script Paths, runs them in parallel (up to `max_workers` at once),
    logs each Python interpreter, and stops on the first script failure.

    Returns:
      - a ScriptResult for the first script that failed, cancelling all others
      - or a list of ScriptResult for all scripts if none failed
    """
    results: list[ScriptResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(run_script, path): path for path in scripts}

        for future in as_completed(future_to_path):
            script_path = future_to_path[future]
            try:
                result = future.result()
            except Exception as exc:
                warn(f"Exception running script {script_path}: {exc}")
                syntax = Syntax(
                    script_path.read_text(encoding="utf-8"),
                    "python",
                    theme="monokai",
                    line_numbers=True,
                )
                console.print(syntax)
                warn(f"{exc}")
                for f in future_to_path:
                    if not f.done():
                        f.cancel()
                return [ScriptResult(-1, str(exc))]

            match result:
                case ScriptResult(return_code=0, result_value=_):
                    results.append(result)
                case ScriptResult(return_code=code, result_value=_):
                    for f in future_to_path:
                        if not f.done():
                            f.cancel()
                    results.append(result)
                    return results

    return results
