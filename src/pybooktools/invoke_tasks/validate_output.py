# validate_output.py
"""
Validate Python example scripts by comparing their
actual output to expected ## comments.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from difflib import Differ
from pathlib import Path

from invoke import task
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from pybooktools.invoke_tasks.find_python_files import find_python_files

console = Console()


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


def actual_output_set(result: str) -> set[str]:
    """
    Turn the result string into a set of unique words.
    """
    return set(re.findall(r"\b\w+\b", result))


def rich_diff(text1: str, text2: str) -> Panel:
    """
    Return a rich-formatted panel showing the diff between two texts.
    """
    differ = Differ()
    diff_lines = list(differ.compare(text1.splitlines(), text2.splitlines()))
    rich_lines = Text()
    for line in diff_lines:
        if line.startswith("+ "):
            rich_lines.append(line + "\n", style="green")
        elif line.startswith("- "):
            rich_lines.append(line + "\n", style="red")
        elif line.startswith("? "):
            rich_lines.append(line + "\n", style="yellow")
        else:
            rich_lines.append(line + "\n")
    return Panel(rich_lines, title="Diff", border_style="white")


@dataclass(frozen=True)
class Result:
    msg: str = ""
    failed: bool = False


def succeed() -> Result:
    return Result()


def fail(msg: str = "") -> Result:
    return Result(msg=msg, failed=True)


def run_and_compare(file: Path, interpreter: str) -> Result:
    """
    Run a Python script using the specified
    interpreter, compare its output to the
    expected output, and return a result object.
    """
    try:
        result = subprocess.run(
            [interpreter, str(file)],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        return fail(
            f"{file}\n[bold red]\u274c Exception trying to run script:[/bold red] {e}"
        )

    if result.returncode != 0:
        return fail(
            f"{file}\n[bold red]\u274c {result.returncode = }: [/bold red]\n{result.stderr}"
        )

    expected = extract_expected_output(file)
    actual = actual_output_set(result.stdout)
    if actual != expected:
        diff_panel = rich_diff("\n".join(sorted(expected)), "\n".join(sorted(actual)))
        msg = (
            f"{file}\n[bold red]\u274c Output mismatch.[/bold red]\n"
            f"[yellow]Expected (from ## comments):[/yellow] {sorted(expected)}\n"
            f"[green]Actual (stdout):[/green]\n{result.stdout}\n"
            f"[magenta]Actual (parsed):[/magenta] {sorted(actual)}\n"
            f"[red]Missing:[/red] {sorted(expected - actual)}\n"
            f"[blue]Unexpected:[/blue] {sorted(actual - expected)}"
        )
        console.print(Panel(msg, title="Comparison", border_style="red"))
        console.print(diff_panel)
        return fail()

    return succeed()


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
            if result.failed:
                discrepancies.append(result.msg)

    if discrepancies:
        console.print("\n❗ Discrepancies found in output:", style="bold red")
        for msg in discrepancies:
            console.print(f"\n{msg}")
        sys.exit(1)

    console.print("\n✅ All outputs matched expectations.", style="bold green")
