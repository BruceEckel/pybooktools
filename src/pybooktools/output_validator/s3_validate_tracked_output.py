#: s3_validate_tracked_output.py
import argparse
from pathlib import Path

from pybooktools.tracing import trace
from pybooktools.util import run_script, display_function_name
from pybooktools.util.artifacts import get_artifact
from .tracker import Tracker


def validate_tracked_output(example_path: Path) -> None:
    tracked_py_path = get_artifact(
        example_path, "s2_tracked", "validate_tracked_output"
    )
    # Run tracked_py_path in its venv
    run_script(tracked_py_path)  # Produces JSON file
    # Use Tracker to ensure valid outputs:
    tracker = Tracker.from_json_file(
        get_artifact(
            example_path, "tracker", "validate_tracked_output", file_ext="json"
        )
    )
    trace(tracker.outputs)
    tracker.compare()


def main():
    display_function_name()
    parser = argparse.ArgumentParser(
        description="Executes example_s2_tracked.py and verifies results"
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test.",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()

    if not args.file_pattern:
        parser.print_help()
        return

    scripts_to_update = list(Path(".").glob(args.file_pattern))
    if not scripts_to_update:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_update:
            print(f"\nValidating {original_script}")
            validate_tracked_output(original_script)


if __name__ == "__main__":
    main()
