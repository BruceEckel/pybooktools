# run_all.py
"""
Run Python scripts in a directory tree (or a
specific subdirectory) in parallel.

Prints colored output with timestamps and stops
all jobs on first failure.
"""

import sys
from pathlib import Path
from typing import Optional

from invoke import task
from rich.console import Console

from pybooktools.invoke_tasks.find_python_files import find_python_files
from pybooktools.run_scripts.run_scripts_parallel import run_scripts_parallel

console = Console()


@task(
    help={
        "target_dir": "Directory to search for Python files (default: current directory).",
        "throttle_limit": "Maximum number of parallel processes (default: number of processors).",
    }
)
def examples(ctx, target_dir: str = ".", throttle_limit: Optional[int] = None) -> None:
    """
    Run all Python scripts in a directory tree in
    parallel.

    This task searches for Python files (skipping
    __init__.py and files in directories such as
    venv, .venv, __pycache__, or .git) and runs
    them concurrently with a throttle limit on the
    number of parallel processes. If any script
    fails (i.e., exits with a nonzero status), the
    task stops further execution and prints an
    error message.

    """
    _ = ctx  # Turns off "value is not used" warning
    target_path = Path(target_dir).resolve()
    console.print(f"🔍 Searching for Python files in: {target_path}", style="yellow")

    python_files: list[Path] = find_python_files(target_path)
    if not python_files:
        console.print("❗ No Python files found.", style="bold red")
        sys.exit(1)

    # if throttle_limit is None:
    #     try:
    #         import os
    #         throttle_limit = os.cpu_count() or 1
    #     except (AttributeError, ValueError):
    #         throttle_limit = 1
    #
    # console.print(
    #     f"🚀 Running {len(python_files)} scripts in parallel (ThrottleLimit = {throttle_limit})",
    #     style="green"
    # )

    results = run_scripts_parallel(python_files)

    # with ThreadPoolExecutor(max_workers=throttle_limit) as executor:
    #     future_to_file = {
    #         executor.submit(run_script, file, failure_event): file
    #         for file in python_files
    #     }
    #     for future in as_completed(future_to_file):
    #         result = future.result()
    #         results.append(result)
    #         if not result.success and not result.skipped:
    #             console.print(f"\nFailed: {result.path}\n{result.error}", style="bold red")
    #             failure_event.set()
    #             break

    if any(res.return_code != 0 for res in results):
        console.print("\n❌ One or more scripts failed.", style="bold red")
        for result in results:
            if result.return_code != 0:
                console.print(result)
        sys.exit(1)

    console.print("\n✅ All scripts ran successfully.", style="bold green")
