#: add_output_tracking.py
import argparse
from pathlib import Path

import libcst as cst
from typing_extensions import override

from pybooktools.util import valid_python_file, panic


def add_output_tracking(example_path: Path) -> Path:
    validate_dir = example_path.parent / "_validate"
    if not validate_dir.exists():
        panic(f"add_output_tracking: {validate_dir} does not exist")
    tracked_py_path = validate_dir / f"{example_path.stem}_tracked.py"
    json_tracker_path = validate_dir / f"{example_path.stem}_tracker.json"

    # Created by number_output_strings():
    numbered_py_path = valid_python_file(
        pyfile := validate_dir / f"{example_path.stem}_numbered.py",
        f"add_output_tracking: {pyfile} invalid",
    )
    numbered_py = numbered_py_path.read_text(encoding="utf-8")

    # Step 1: Add import statements and tracker initialization
    numbered_py = (
            "from pybooktools.example_checker.tracker import Tracker\n"
            "tracker = Tracker()\n" + numbered_py
    )

    # Step 2-4: Use libcst to modify the Python code
    class TrackerTransformer(cst.CSTTransformer):
        @override
        def leave_SimpleString(
                self,
                original_node: cst.SimpleString,
                updated_node: cst.SimpleString,
        ) -> cst.CSTNode:
            # Step 2 & 3: Find unassigned strings that begin with an integral number followed by ':'
            if (
                    original_node.value.startswith('"')
                    and original_node.value[1:].isdigit()
                    and ":" in original_node.value
            ):
                parts = original_node.value.split(":", 1)
                if parts[0][1:].isdigit():
                    n = parts[0][1:]
                    return cst.parse_expression(
                        f"tracker.expected({n}, {original_node.value})"
                    )
            return updated_node

        @override
        def leave_Call(
                self, original_node: cst.Call, updated_node: cst.Call
        ) -> cst.CSTNode:
            # Step 4: Replace all calls to `print` with `tracker.print`
            if (
                    isinstance(original_node.func, cst.Name)
                    and original_node.func.value == "print"
            ):
                return updated_node.with_changes(
                    func=cst.Attribute(
                        value=cst.Name("tracker"), attr=cst.Name("print")
                    )
                )
            return updated_node

    # Parse the numbered_py code with libcst and apply the transformer
    cst_tree = cst.parse_module(numbered_py)
    modified_tree = cst_tree.visit(TrackerTransformer())

    # Step 5: Add line to write the Tracker as a JSON file:
    modified_code = (
            modified_tree.code
            + f"\ntracker.write_json_file('{json_tracker_path}')\n"
    )

    # Step 6: Store the modified numbered_py in tracked_py_path
    tracked_py_path.write_text(modified_code, encoding="utf-8")
    return tracked_py_path


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

    scripts_to_track = list(Path(".").glob(args.file_pattern))
    if not scripts_to_track:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_track:
            print(f"\nAdding tracking to script: {original_script}")
            tracked_py_path = add_output_tracking(original_script)
            print(f"Tracked version saved: {tracked_py_path}")


if __name__ == "__main__":
    main()
