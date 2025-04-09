# TODO: Dedup the use of this file by moving invoke_tasks to pybooktools

from pathlib import Path

# Directories to exclude from the search.
EXCLUDED_DIRS = {"venv", ".venv", "__pycache__", ".git", "python", "invoke_tasks"}
EXCLUDED_FILES = {"__init__.py", "tasks.py", "bootstrap.py"}


def find_python_files(target_dir: Path) -> list[Path]:
    """
    Recursively find all Python files (*.py) in
    target_dir, excepting exclusions.
    """
    python_files: list[Path] = []
    for file in target_dir.rglob("*.py"):
        if file.name in EXCLUDED_FILES:
            continue
        if any(ex_dir in file.parts for ex_dir in EXCLUDED_DIRS):
            continue
        python_files.append(file)
    return python_files
