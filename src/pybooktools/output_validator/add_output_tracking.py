#: add_output_tracking.py
import argparse
from pathlib import Path

import libcst as cst
from typing_extensions import override

from pybooktools.util import trace, artifact_path, get_artifact


def add_output_tracking(example_path: Path) -> Path:
    # Created by number_output_strings():
    numbered_py_path = get_artifact(
        example_path, "numbered", "add_output_tracking"
    )
    numbered_py = numbered_py_path.read_text(encoding="utf-8")

    # Add import statements and tracker initialization
    numbered_py = (
            "from pybooktools.tracker import Tracker\n"
            "tracker = Tracker()\n" + numbered_py
    )

    # Use libcst to modify the Python code
    class TrackerTransformer(cst.CSTTransformer):
        @override
        def leave_SimpleString(
                self,
                original_node: cst.SimpleString,
                updated_node: cst.SimpleString,
        ) -> cst.CSTNode:
            trace(f"testing {original_node.value}")
            # Find unassigned strings that begin with an integral number followed by ':'
            if (
                    original_node.value.startswith('"""')
                    and original_node.value[3].isdigit()
                    and ":" in original_node.value
            ):
                trace(f"Found {original_node.value}")
                parts = original_node.value.split(":", 1)
                trace(f"{parts = }")
                n = parts[0][3:]
                trace(f"{n = }")
                return cst.parse_expression(
                    f"tracker.expected({n}, r'{original_node.value}')"
                )
            if (
                    original_node.value.startswith('"')
                    and original_node.value[1].isdigit()
                    and ":" in original_node.value
            ):
                trace(f"Found {original_node.value}")
                parts = original_node.value.split(":", 1)
                trace(f"{parts = }")
                n = parts[0][1:]
                trace(f"{n = }")
                return cst.parse_expression(
                    f"tracker.expected({n}, r'{original_node.value}')"
                )
            return updated_node

        @override
        def leave_Call(
                self, original_node: cst.Call, updated_node: cst.Call
        ) -> cst.CSTNode:
            # Replace all calls to `print` with `tracker.print`
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

    # Add line to write the Tracker as a JSON file:
    json_tracker_path = artifact_path(
        example_path, "tracker", "add_output_tracking", file_ext="json"
    )
    modified_code = (
            modified_tree.code
            + f'\ntracker.write_json_file(r"{json_tracker_path}")\n'
    )

    # Store the modified code
    tracked_py_path = artifact_path(
        example_path, "tracked", "add_output_tracking"
    )
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

    scripts_to_track = list(Path("..").glob(args.file_pattern))
    if not scripts_to_track:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_track:
            print(f"\nAdding tracking to script: {original_script}")
            tracked_py_path = add_output_tracking(original_script)
            print(f"Tracked version saved: {tracked_py_path}")


if __name__ == "__main__":
    main()
