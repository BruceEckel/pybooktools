# get_virtual_environment.py
import os
import sys
from functools import cache
from pathlib import Path


@cache
def get_virtual_env_python() -> str:
    """
    Return the Python interpreter path from the virtual environment if available.
    Caches the result for efficiency, since the virtual environment typically
    does not change during program execution.
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
