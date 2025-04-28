# run_all.py
"""
Run Python scripts in a directory tree (or a
specific subdirectory) in parallel.

Prints colored output with timestamps and stops
all jobs on first failure.
"""

import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from invoke import task
from rich.console import Console

from pybooktools.invoke_tasks.find_python_files import find_python_files

console = Console()


@dataclass
class RunResult:
    """
    Result of running a Python script.
    """
    success: bool
    path: Path | None = None
    error: str | None = None
    skipped: bool = False


def run_script(file: Path, failure_event: threading.Event) -> RunResult:
    """
    Run the Python script specified by file.

    If the failure_event is set, skip running.
    Use a polling loop to allow early termination
    if a failure is detected.

    """
    if failure_event.is_set():
        return RunResult(
            success=False,
            path=file,
            error="Skipped due to a previous failure",
            skipped=True,
        )

    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"{timestamp} ▶️ Running: {file}", style="cyan")

    try:
        process = subprocess.Popen(
            ["python", str(file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        while True:
            if failure_event.is_set():
                if process.poll() is None:
                    process.terminate()
                    process.wait()
                    return RunResult(
                        success=False,
                        path=file,
                        error="Terminated due to another failure",
                    )
            ret = process.poll()
            if ret is not None:
                break
            time.sleep(0.1)
        stdout, stderr = process.communicate()

        if ret != 0:
            failure_event.set()
            return RunResult(success=False, path=file, error=stderr)
        else:
            if stdout:
                console.print(stdout, style="grey50")
            return RunResult(success=True)
    except Exception as e:
        failure_event.set()
        return RunResult(success=False, path=file, error=str(e))


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

    python_files = find_python_files(target_path)
    if not python_files:
        console.print("❗ No Python files found.", style="bold red")
        sys.exit(1)

    if throttle_limit is None:
        try:
            import os
            throttle_limit = os.cpu_count() or 1
        except (AttributeError, ValueError):
            throttle_limit = 1

    console.print(
        f"🚀 Running {len(python_files)} scripts in parallel (ThrottleLimit = {throttle_limit})",
        style="green"
    )

    failure_event = threading.Event()
    results: list[RunResult] = []

    with ThreadPoolExecutor(max_workers=throttle_limit) as executor:
        future_to_file = {
            executor.submit(run_script, file, failure_event): file
            for file in python_files
        }
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)
            if not result.success and not result.skipped:
                console.print(f"\nFailed: {result.path}\n{result.error}", style="bold red")
                failure_event.set()
                break

    if any(not res.success and not res.skipped for res in results):
        console.print("\n❌ One or more scripts failed.", style="bold red")
        sys.exit(1)

    console.print("\n✅ All scripts ran successfully.", style="bold green")
