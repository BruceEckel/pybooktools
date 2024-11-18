#: util.py
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


# self.temp_script_path = Path(
#     tempfile.NamedTemporaryFile(delete=False, suffix="_tmp.py").name
# )


def get_virtual_env_python() -> str:
    """Return the Python interpreter path from the virtual environment if available"""
    venv_path = os.getenv("VIRTUAL_ENV")
    if venv_path:
        python_path = (
                Path(venv_path)
                / ("Scripts" if os.name == "nt" else "bin")
                / "python"
        )
        return str(python_path)
    return sys.executable


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
