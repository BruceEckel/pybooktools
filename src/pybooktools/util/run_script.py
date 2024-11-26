import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax

console = Console()


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


def run_script(script_path: Path) -> None:
    """
    Runs the script in its virtual environment
    """
    result = subprocess.run(
        [get_virtual_env_python(), str(script_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console = Console()
        console.print(
            f"[bold red]Error running script {script_path}:[/bold red]"
        )
        syntax = Syntax(
            script_path.read_text(encoding="utf-8"),
            "python",
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)
        console.print(f"[bold red]Error Message:[/bold red] {result.stderr}")
        panic("")
