import argparse
import glob
import re
import subprocess
from pathlib import Path
from typing import Final

import libcst as cst
import libcst.matchers as m
from libcst.metadata import MetadataWrapper

from pybooktools.tracker import Tracker
from pybooktools.util import get_virtual_env_python

validate_dir: Final[Path] = Path("_validate")
validate_dir.mkdir(exist_ok=True)


class PrintTransformer(cst.CSTTransformer):
    def leave_Call(
            self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.CSTNode:
        if m.matches(original_node.func, m.Name("print")):
            # Replace print calls with track.print
            new_func = cst.Attribute(
                value=cst.Name("track"), attr=cst.Name("print")
            )
            return updated_node.with_changes(func=new_func)
        return updated_node


class UnassignedStringTransformer(cst.CSTTransformer):
    def leave_Expr(
            self, original_node: cst.Expr, updated_node: cst.Expr
    ) -> cst.CSTNode:
        if isinstance(original_node.value, cst.SimpleString):
            # Surround unassigned strings with track.expected
            new_call = cst.Call(
                func=cst.Attribute(
                    value=cst.Name("track"), attr=cst.Name("expected")
                ),
                args=[cst.Arg(original_node.value)],
            )
            return updated_node.with_changes(value=new_call)
        return updated_node


def create_validation_pyfile(pyfile: Path) -> (Path, Path):
    validation_file_path = validate_dir / pyfile.with_name(
        f"{pyfile.stem}_validate{pyfile.suffix}"
    )
    output_file_path = validate_dir / pyfile.with_name(
        f"{pyfile.stem}_tracker.json"
    )
    # Read the original Python file
    source_code = pyfile.read_text(encoding="utf-8")
    wrapper = MetadataWrapper(cst.parse_module(source_code))
    tree = wrapper.module

    # Add the necessary import and global Tracker instance
    import_node = cst.ImportFrom(
        module=cst.Attribute(
            value=cst.Name("pybooktools"), attr=cst.Name("tracker")
        ),
        names=[cst.ImportAlias(name=cst.Name("Tracker"))],
    )
    tracker_instance_node = cst.SimpleStatementLine(
        body=[
            cst.Assign(
                targets=[cst.AssignTarget(target=cst.Name("track"))],
                value=cst.Call(
                    func=cst.Name("Tracker"),
                    args=[
                        cst.Arg(
                            cst.SimpleString(f"{repr(str(output_file_path))}")
                        )
                    ],
                ),
            )
        ]
    )

    # Modify the tree by adding the import and tracker instance
    new_body = list(tree.body)
    new_body.insert(0, import_node)
    new_body.insert(1, cst.EmptyLine())
    new_body.insert(2, tracker_instance_node)

    modified_tree = tree.with_changes(body=new_body)

    # Apply transformations to replace print statements and unassigned strings
    modified_tree = modified_tree.visit(PrintTransformer())
    modified_tree = modified_tree.visit(UnassignedStringTransformer())

    # Write the transformed code to a new file
    transformed_code = (
            modified_tree.code + "\ntrack.compare()\ntrack.create_json_file()\n"
    )
    validation_file_path.write_text(transformed_code, encoding="utf-8")
    return validation_file_path, output_file_path


def run_validation_pyfile(validation_file_path: Path) -> bool:
    python_executable = get_virtual_env_python()
    if not validation_file_path.exists():
        print(f"Cannot locate {validation_file_path}")
        return False
    print(f"Using: {python_executable}")
    print(f"Running: {validation_file_path} ", end="")
    result = subprocess.run(
        [python_executable, str(validation_file_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(" ... failed")
        return False
    else:
        print("")
        return True


def update_original_script(original_script: Path, json_tracker_data: Path):
    if not original_script.exists():
        print(f"Cannot locate {original_script}")
        return
    source_code = original_script.read_text(encoding="utf-8")

    # Recreate Tracker instance from the JSON file
    tracker = Tracker.from_file(json_tracker_data)

    # Update the expected strings in the original script based on tracker data
    for output in tracker.outputs:
        expected = output.expected.strip()
        actual = output.actual.strip()
        if expected != actual:
            # Replace only the first occurrence of the expected output with the actual output
            print(f"Updating expected value: {expected} -> {actual}")
            # Use a more specific pattern to avoid accidental replacements
            pattern = re.escape(expected)
            matches = list(re.finditer(pattern, source_code))
            if matches:
                match = matches[0]  # Only replace the first match
                start, end = match.span()
                source_code = source_code[:start] + actual + source_code[end:]
            else:
                print(
                    f"Warning: Expected value '{expected}' not found for replacement."
                )

    # Write the updated code back to the original script
    original_script.write_text(source_code, encoding="utf-8")
    print(f"Updated {original_script} with new expected outputs")


def main():
    parser = argparse.ArgumentParser(
        description="Python Output Tester - Compare expected output comments with actual output."
    )
    parser.add_argument(
        "file_pattern",
        type=str,
        help="File or pattern to match Python scripts to test.",
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update the expected output to match the actual output.",
    )
    args = parser.parse_args()
    if not (args.file_pattern or args.store_true):
        parser.print_help()
        return

    scripts_to_test = glob.glob(args.file_pattern)
    if not scripts_to_test:
        print("No files matched the given file pattern.")
    else:
        for original_script in scripts_to_test:
            print(f"\nTesting script: {original_script}")
            val_file, json_tracker_data = create_validation_pyfile(
                Path(original_script)
            )
            print(f"Created {val_file}")
            if not run_validation_pyfile(val_file):
                print(f"{val_file} failed to run")
                continue
            else:
                print(f"{val_file} ran successfully")
                if args.update:
                    update_original_script(
                        Path(original_script), json_tracker_data
                    )


if __name__ == "__main__":
    main()
