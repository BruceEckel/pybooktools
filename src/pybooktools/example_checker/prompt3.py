#: prompt3.py
from pathlib import Path

from pybooktools.util import panic


def generate_tracked_output(example_path: Path):
    validate_dir = example_path.parent / "_validate"
    if not validate_dir.exists():
        panic(f"add_output_tracking: {validate_dir} does not exist")
    json_tracker = validate_dir / f"{example_path.stem}_tracker.json"
