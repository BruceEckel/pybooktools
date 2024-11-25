#: prompt2.py
import argparse
from pathlib import Path

from pybooktools.util import valid_python_file, panic


def add_output_tracking(example_path: Path):
    validate_dir = example_path.parent / "_validate"
    if not validate_dir.exists():
        panic(f"add_output_tracking: {validate_dir} does not exist")
    tracked_py_path = validate_dir / f"{example_path.stem}_tracked.py"
    json_tracker = validate_dir / f"{example_path.stem}_tracker.json"
    # Created by the previous step:
    numbered_py_path = valid_python_file(
        validate_dir / f"{example_path.stem}_numbered.py"
    )
    numbered_py = numbered_py_path.read_text(encoding="utf-8")
    """
    1. At top of numbered_py, add "from pybooktools.example_checker.tracker import Tracker" 
       followed by "tracker = Tracker()".
    2. Using libcst, find all unassigned strings in numbered_py that begin
       with an integral number `n` followed by `:`.
    3. For each, extract `n` and surround that unassigned string (including
       its escaped quotes at the beginning and end) with a call to
       `tracker.expected(the_number, the_complete_text_of_the_unassigned_string)`
    4. Using libcst, find all calls to `print` and replace them with `tracker.print`
    5. Store the modified numbered_py in tracked_py_path.
    # 6. Call `tracker.convert_to_json()` and store that return value in json_tracker.
>>>>>>>(This only works after tracked_py is executed)
    """


def main():
    parser = argparse.ArgumentParser(
        description="Adds numbers to output strings starting with ':'"
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test.",
    )
    args = parser.parse_args()
    if not args.file_pattern:
        parser.print_help()
        return

    scripts_to_number = list(Path(".").glob(args.file_pattern))
    if not scripts_to_number:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_number:
            print(f"\nNumbering script: {original_script}")
            add_output_tracking(original_script)


if __name__ == "__main__":
    main()
