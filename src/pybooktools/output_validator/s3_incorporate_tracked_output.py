#: s3_incorporate_tracked_output.py
import argparse
from pathlib import Path

from pybooktools.tracing import trace
from pybooktools.util import panic, run_script, display_function_name
from pybooktools.util.artifacts import get_artifact, artifact_path
from .tracker import Tracker


def incorporate_tracked_output(example_path: Path) -> Path:
    tracked_py_path = get_artifact(
        example_path, "s2_tracked", "incorporate_tracked_output"
    )
    # Step 1: Run tracked_py_path in its venv
    run_script(tracked_py_path)
    # Step 2: Use json_tracker to incorporate outputs into example_path
    json_tracker = get_artifact(
        example_path, "tracker", "incorporate_tracked_output", file_ext="json"
    )
    tracker = Tracker.from_json_file(json_tracker)
    trace(tracker.outputs)
    numbered_example_path = get_artifact(
        example_path, "s1_numbered", "incorporate_tracked_output"
    )
    updated = numbered_example_path.read_text(encoding="utf-8")
    for output in tracker.outputs:
        if output.untouched_output.startswith('"""'):
            trace(f"3 quotes {output.untouched_output = }")
            trace(f"3 quotes {output.actual_output = }")
            updated = updated.replace(
                output.untouched_output, f'""":\n{output.actual_output}\n"""'
            )
            trace(updated)
        elif output.untouched_output.startswith('"'):
            trace(f"1 quote {output.untouched_output = }")
            trace(f"1 quote {output.actual_output = }")
            updated = updated.replace(
                output.untouched_output, f'":{output.actual_output}"'
            )
            trace(updated)
        else:
            panic(f"Bad output: {output}")
    incorporated_path = artifact_path(
        example_path, "s3_incorporated", "incorporate_tracked_output"
    )
    incorporated_path.write_text(updated, encoding="utf-8")
    return incorporated_path


def main():
    parser = argparse.ArgumentParser(
        description="Executes example_tracked.py and incorporates results"
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
        display_function_name()

    if not args.file_pattern:
        parser.print_help()
        return

    scripts_to_update = list(Path(".").glob(args.file_pattern))
    if not scripts_to_update:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_update:
            print(f"\nIncorporating tracked output for: {original_script}")
            updated_py_path = incorporate_tracked_output(original_script)
            print(f"Updated version saved: {updated_py_path}")


if __name__ == "__main__":
    main()
