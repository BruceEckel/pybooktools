import argparse
import glob
import json
import subprocess
from pathlib import Path
from typing import Final

import libcst as cst
import libcst.matchers as m
from libcst.metadata import MetadataWrapper

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

    # Add the necessary import and global Tracker instance if not present
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
                        cst.Arg(cst.SimpleString(f'"{str(output_file_path)}"'))
                    ],
                ),
            )
        ]
    )

    # Check if import or tracker instance already exists
    has_import = any(
        m.matches(
            node,
            m.ImportFrom(
                module=m.Attribute(
                    value=m.Name("pybooktools"), attr=m.Name("tracker")
                )
            ),
        )
        for node in tree.body
    )
    has_tracker_instance = any(
        m.matches(
            node,
            m.SimpleStatementLine(
                body=[
                    m.Assign(targets=[m.AssignTarget(target=m.Name("track"))])
                ]
            ),
        )
        for node in tree.body
    )

    # Modify tree by adding the import and tracker instance if needed
    new_body = list(tree.body)
    if not has_import:
        new_body.insert(0, import_node)
    if not has_tracker_instance:
        new_body.insert(2, tracker_instance_node)

    modified_tree = tree.with_changes(body=new_body)

    # Apply transformations to replace print statements and unassigned strings
    modified_tree = modified_tree.visit(PrintTransformer())
    modified_tree = modified_tree.visit(UnassignedStringTransformer())

    # Write the transformed code to a new file
    transformed_code = (
            modified_tree.code + "\ntrack.compare()\ntrack.create_output_file()\n"
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
        print(" ... passed")
        return True


def update_original_script(original_script: Path, json_tracker_data: Path):
    if not original_script.exists():
        print(f"Cannot locate {original_script}")
        return
    if not json_tracker_data.exists():
        print(f"Cannot locate {json_tracker_data}")
        return

    # Load the tracker data from the JSON file
    with json_tracker_data.open("r", encoding="utf-8") as f:
        tracker_data = json.load(f)

    # Read the original source code
    source_code = original_script.read_text(encoding="utf-8")
    wrapper = MetadataWrapper(cst.parse_module(source_code))
    tree = wrapper.module

    # Update unassigned strings with the actual outputs from tracker data
    class UpdateExpectedTransformer(cst.CSTTransformer):
        def leave_Expr(
                self, original_node: cst.Expr, updated_node: cst.Expr
        ) -> cst.CSTNode:
            if isinstance(original_node.value, cst.SimpleString):
                original_value = original_node.value.value.strip('"')
                if original_value in tracker_data:
                    new_value = tracker_data[original_value]
                    return updated_node.with_changes(
                        value=cst.SimpleString(f'"{new_value}"')
                    )
            return updated_node

    updated_tree = tree.visit(UpdateExpectedTransformer())

    # Write the updated code back to the original script
    updated_code = updated_tree.code
    original_script.write_text(updated_code, encoding="utf-8")
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
