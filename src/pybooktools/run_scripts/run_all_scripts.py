# run_all_scripts.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Generator

from rich.syntax import Syntax

from pybooktools.run_scripts.run_one_script import run_script
from pybooktools.run_scripts.script_result import ScriptResult
from pybooktools.util.console import console
from pybooktools.util.display import warn


def run_scripts(
    scripts: Generator[Path, None, None] | list[Path],
) -> list[ScriptResult]:
    """
    Runs a list or generator of script Paths sequentially.
    Stops on the first failure and returns that ScriptResult.
    Otherwise returns a list of all successful ScriptResults.
    """
    results: list[ScriptResult] = []

    for path in scripts:
        try:
            result = run_script(path)
        except Exception as exc:
            warn(f"Exception running script {path}: {exc}")
            syntax = Syntax(
                path.read_text(encoding="utf-8"),
                "python",
                theme="monokai",
                line_numbers=True,
            )
            console.print(syntax)
            warn(f"{exc}")
            return [ScriptResult(-1, str(exc))]

        match result.return_code:
            case 0:
                results.append(result)
            case _:
                results.append(result)
                return results

    return results


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

            match result.return_code:
                case 0:
                    results.append(result)
                case _:
                    for f in future_to_path:
                        if not f.done():
                            f.cancel()
                    results.append(result)
                    return results

    return results
