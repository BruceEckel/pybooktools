#: check_example_output.py
import argparse
from pathlib import Path

from pybooktools.output_validator.s1_number_output_strings import (
    number_output_strings,
)
from pybooktools.output_validator.s2_add_output_tracking import add_tracking
from pybooktools.output_validator.s3_validate_tracked_output import (
    validate_tracked_output,
)
from pybooktools.tracing import trace
from pybooktools.util import display_function_name


def main():
    prog_id = f"{Path(__file__).stem}"
    parser = argparse.ArgumentParser(
        description='Updates Python examples containing output strings that begin with ": or """:'
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test",
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
            trace(f"\n{prog_id}: Updating {original_script}")
            numbered_py_path = number_output_strings(original_script)
            trace(f"{prog_id}: Numbered version saved: {numbered_py_path}")
            tracked_py_path = add_tracking(original_script)
            trace(f"{prog_id}: Tracked version saved: {tracked_py_path}")
            validate_tracked_output(original_script)


if __name__ == "__main__":
    main()
