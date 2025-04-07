# find_file_types.py
from pybooktools.find_files.file_finder import curry_file_finder

# Exclude these directories from python_files().
EXCLUDE_DIRS = {"venv", ".venv", "__pycache__", ".git", "python", "invoke_tasks"}
# Exclude these files from python_files().
EXCLUDE_FILES = {"__init__.py", "tasks.py", "bootstrap.py"}

python_files = curry_file_finder(extensions={".py"}, exclude_files=EXCLUDE_FILES, exclude_dirs=EXCLUDE_DIRS)
