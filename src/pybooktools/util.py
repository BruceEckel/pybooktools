#: util.py
import os
import pprint
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax


# self.temp_script_path = Path(
#     tempfile.NamedTemporaryFile(delete=False, suffix="_tmp.py").name
# )


@dataclass
class Trace:
    tracing: bool = False

    def __call__(self, arg):
        if not self.tracing:
            return
        if isinstance(arg, list):
            pprint.pprint(arg)
        else:
            print(arg)


def panic(msg: str) -> None:
    sys.stderr.write(msg + "\nEXITING\n")
    sys.exit("EXITING")


def valid_python_file(pyfile: Path, msg: str = "") -> Path:
    if not pyfile.is_file():
        if msg:
            print(msg)
        panic(f"{pyfile} not found")
    if pyfile.suffix != ".py":
        if msg:
            print(msg)
        panic(f"{pyfile} is not a Python file")
    return pyfile


def fname(function_name: str) -> str:
    return f"{function_name}: " if function_name else ""


def artifact_path(
        example_path: Path, id_ext: str, function_name: str = "", file_ext="py"
) -> Path:
    if not example_path.exists():
        panic(f"{fname(function_name)}{example_path} does not exist")
    validate_dir = example_path.parent / "_validate"
    if not validate_dir.exists():
        panic(f"{fname(function_name)}{validate_dir} does not exist")
    artifact_path = validate_dir / f"{example_path.stem}_{id_ext}.{file_ext}"
    return artifact_path


def get_artifact(
        example_path: Path, id_ext: str, function_name: str = "", file_ext="py"
) -> Path:
    artifact = artifact_path(example_path, id_ext, function_name, file_ext)
    if not artifact.exists():
        panic(f"{fname(function_name)}{artifact} does not exist")
    return artifact


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


@dataclass(frozen=True)
class BoolStatus:
    status: bool = False

    def __bool__(self) -> bool:
        return self.status


@dataclass
class FileChanged:
    file_name: str
    # Set to False and exclude field from constructor arguments
    modified: bool = field(default=False, init=False)

    def true(self) -> "FileChanged":
        self.modified = True
        return self

    def false(self) -> "FileChanged":
        self.modified = False
        return self

    def report(self) -> str:
        if self.modified:
            return f"[bold red]{self.file_name}[/bold red]"
        return f"[bold green]{self.file_name}[/bold green]"
