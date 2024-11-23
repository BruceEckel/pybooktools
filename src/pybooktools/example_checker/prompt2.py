import argparse
from pathlib import Path

from pybooktools.util import valid_python_file


def add_output_tracking(example_path: Path):
    validate_dir = example_path.parent / "_validate"
    numbered_py_path = validate_dir / f"{example_path.stem}_numbered.py"
    if not valid_python_file(numbered_py_path):
        return
    numbered_py = numbered_py_path.read_text(encoding="utf-8")
    """
    1. Add "from pybooktools.example_checker.tracker import Tracker" followed 
       by "tracker = Tracker()" at top of file.
    2. Using libcst, find all unassigned strings that begin
       with a number followed by ':'.
    3. Extract that number and surround that unassigned string with a call to
       `tracker.expected(the_number, the_complete_text_of_the_unassigned_string)`
    4. Using libcst, find all calls to `print` and replace them with `tracker.print`
    5. Store the result in the validate_dir with the stem of the
       original file followed by _tracked.py
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
