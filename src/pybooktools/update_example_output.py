import argparse
from pathlib import Path

from pybooktools.output_validator.s1_number_output_strings import (
    number_output_strings,
)
from pybooktools.output_validator.s2_add_output_tracking import add_tracking
from pybooktools.output_validator.s3_incorporate_tracked_output import (
    incorporate_tracked_output,
)
from pybooktools.output_validator.s4_adjust_indentation import (
    adjust_multiline_strings_indent,
)
from pybooktools.tracing import trace
from pybooktools.util import artifact_path, trace_function_name


def main():
    parser = argparse.ArgumentParser(
        description='Updates Python examples containing output strings that begin with ": or """:'
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing output"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()

    if not args.file_pattern:
        parser.print_help()
        return

    trace_function_name(f"{Path(__file__).name}")
    scripts_to_update = list(Path(".").glob(args.file_pattern))
    if not scripts_to_update:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_update:
            print(f"\nUpdating {original_script}")
            numbered_py_path = number_output_strings(original_script)
            print(f"Numbered version saved: {numbered_py_path}")
            tracked_py_path = add_tracking(original_script)
            print(f"Tracked version saved: {tracked_py_path}")
            updated_py_path = incorporate_tracked_output(original_script)
            print(f"Updated version saved: {updated_py_path}")
            adjusted = adjust_multiline_strings_indent(
                updated_py_path.read_text(encoding="utf-8")
            )
            finished = artifact_path(
                original_script, "s4_finished", "update_python_examples"
            )
            finished.write_text(adjusted, encoding="utf-8")
            print(f"Finished version saved: {finished}")


if __name__ == "__main__":
    main()
