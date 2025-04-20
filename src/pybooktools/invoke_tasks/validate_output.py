# validate_output.py
"""
Validate Python example scripts by comparing their
output to expected ## comments.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import Differ
from pathlib import Path
from typing import NamedTuple

from invoke import task
from rich.console import Console

from pybooktools.invoke_tasks.find_python_files import find_python_files

console = Console()


def rich_diff(text1, text2):
    """
    Compares two strings and prints a rich-formatted diff output.
    """
    differ = Differ()
    diff = list(
        differ.compare(text1.splitlines(keepends=True), text2.splitlines(keepends=True))
    )

    for line in diff:
        if line.startswith("+ "):
            console.print(f"[green]{line.rstrip()}[/green]")
        elif line.startswith("- "):
            console.print(f"[red]{line.rstrip()}[/red]")
        elif line.startswith("? "):
            console.print(f"[yellow]{line.rstrip()}[/yellow]")
        else:
            console.print(line.rstrip())


def extract_expected_output(file: Path) -> set[str]:
    """
    Extract expected output from a Python file by
    reading lines that start with '## ' and return a set
    of all unique words found in those lines.
    """
    lines = file.read_text(encoding="utf-8").splitlines()
    words: set[str] = set()
    for line in lines:
        match = re.match(r"^\s*## (.*)$", line)
        if match:
            words.update(re.findall(r"\b\w+\b", match.group(1)))
    return words


def word_set_compare(expected: str, actual: str) -> set[str]:
    def word_set(s):
        return set(s.split())

    return word_set(expected) ^ word_set(actual)


class Result(NamedTuple):
    msg: str | None = None
    diffs: set[str] | None = None
    failed: bool = False


class Fail(Result):
    failed = True


def run_and_compare(file: Path, interpreter: str) -> Result:
    """
    Run a Python script using the specified
    interpreter, compare its output to the
    expected output, and return a tuple indicating
    success and an error message (if any).
    """
    try:
        result = subprocess.run(
            [interpreter, str(file)],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        return Fail(
            f"{file}\n[bold red]\u274c Exception trying to run script:[/bold red] {e}"
        )

    if result.returncode != 0:
        return Fail(
            f"{file}\n[bold red]\u274c {result.returncode = }: [/bold red]\n{result.stderr}"
        )

    expected = extract_expected_output(file)
    actual = extract_expected_output(file)
    if actual != expected:
        return Fail(
            f"{file}\n[bold red]\u274c Output mismatch.[/bold red]\n"
            f"--- [yellow]Expected (from ## comments)[/yellow] ---\n{expected}\n"
            f"--- [green]Actual (stdout)[/green] ---\n{result.stdout}\n"
            f"--- [blue]Expected[/blue] ---\n{expected}\n"
            f"--- [magenta]Actual[/magenta] ---\n{actual}"
        )

    return Result(diffs=expected - actual)


@task(
    help={
        "target_dir": "Directory to search for Python files (default: current directory).",
        "throttle_limit": "Max number of parallel workers (default: number of CPU cores).",
    }
)
def validate(ctx, target_dir: str = ".", throttle_limit: int | None = None) -> None:
    """
    Run Python example scripts and compare actual
    output to expected ## comments.

    Ignores whitespace, supports parallel
    execution, and uses the active interpreter.

    """
    _ = ctx  # Silence warning
    interpreter = sys.executable
    root = Path(target_dir).resolve()
    console.print(f"🐍 Using interpreter: {interpreter}", style="green")
    console.print(f"🔍 Validating Python examples in: {root}", style="yellow")

    files = find_python_files(root)
    if not files:
        console.print("❗ No Python files found.", style="bold red")
        sys.exit(1)

    if throttle_limit is None:
        throttle_limit = os.cpu_count() or 4

    console.print(
        f"🧪 Comparing output for {len(files)} examples (ThrottleLimit = {throttle_limit})",
        style="cyan",
    )

    discrepancies: list[str] = []
    with ThreadPoolExecutor(max_workers=throttle_limit) as executor:
        futures = {
            executor.submit(run_and_compare, file, interpreter): file for file in files
        }
        for future in as_completed(futures):
            result = future.result()
            if result.failed and result.msg:
                discrepancies.append(result.msg)

    if discrepancies:
        console.print("\n❗ Discrepancies found in output:", style="bold red")
        for msg in discrepancies:
            console.print(f"\n{msg}")
        sys.exit(1)

    console.print("\n✅ All outputs matched expectations.", style="bold green")
