#: s3_validate_tracked_output.py
import argparse
from pathlib import Path

from pybooktools.util import panic, run_script, trace, display
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
    for output in tracker.outputs:
        if output.untouched_output.startswith('"""'):
            trace(f"3 quotes {output.untouched_output = }")
            trace(f"3 quotes {output.actual_output = }")
        elif output.untouched_output.startswith('"'):
            trace(f"1 quote {output.untouched_output = }")
            trace(f"1 quote {output.actual_output = }")
        else:
            panic(f"Bad output: {output}")


def main():
    display(f"{Path(__file__).name}")

    parser = argparse.ArgumentParser(
        description="Executes example_s2_tracked.py and verifies results"
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

    scripts_to_update = list(Path(".").glob(args.file_pattern))
    if not scripts_to_update:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_update:
            print(f"\nValidating {original_script}")
            validate_tracked_output(original_script)


if __name__ == "__main__":
    main()
