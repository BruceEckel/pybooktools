import argparse
import pickle
import shutil
from pathlib import Path

import libcst as cst
from icecream import ic
from libcst.metadata import MetadataWrapper

from pybooktools.ocl_1 import OCLContainer
from pybooktools.util import run_script


class OCLTransformer(cst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.ocl_statements = []
        self.counter = 0

    def leave_Call(
        self, original_node: cst.Call, updated_node: cst.Call
    ) -> cst.BaseExpression:
        if (
            isinstance(updated_node.func, cst.Name)
            and updated_node.func.value == "print"
        ):
            args = updated_node.args
            if len(args) == 1:
                self.counter += 1
                original_source = cst.Module([]).code_for_node(original_node)
                # Serialize the argument to Python source code
                arg_source = cst.Module([]).code_for_node(args[0].value)
                ocl_call = cst.parse_expression(
                    f"oclgen({self.counter}, {arg_source}, r'''{original_source}''')"
                )
                self.ocl_statements.append(
                    (self.counter, original_source, arg_source)
                )
                return ocl_call
        return updated_node


def extract_imports_and_definitions(source_code: str) -> str:
    module = cst.parse_module(source_code)
    imports_and_definitions = []

    class ImportAndDefinitionCollector(cst.CSTVisitor):
        def visit_Import(self, node: cst.Import) -> None:
            imports_and_definitions.append(cst.Module([]).code_for_node(node))

        def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
            imports_and_definitions.append(cst.Module([]).code_for_node(node))

        def visit_ClassDef(self, node: cst.ClassDef) -> None:
            imports_and_definitions.append(node.name.value)

        def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
            imports_and_definitions.append(node.name.value)

    module.visit(ImportAndDefinitionCollector())
    return "\n".join(imports_and_definitions)


def main():
    parser = argparse.ArgumentParser(
        description="Generate OCL script and transform."
    )
    parser.add_argument("filename", type=str, help="Python file to process.")
    args = parser.parse_args()

    input_path = Path(args.filename).resolve()
    script_name = input_path.stem
    check_dir = input_path.parent / f".check_{script_name}"
    if check_dir.exists():
        shutil.rmtree(check_dir)
    check_dir.mkdir()

    ocl_container_path = check_dir / "ocl_container.pickle"
    environment_path = check_dir / "environment.pickle"
    ocl_printer_1_path = check_dir / f"{script_name}_1.py"
    ocl_printer_2_path = check_dir / f"{script_name}_2.py"
    ocl_results_path = check_dir / input_path.name

    source_code = input_path.read_text(encoding="utf-8")

    # Extract imports and definitions from the original source code
    imports_and_definitions = extract_imports_and_definitions(source_code)

    # Process with libcst
    module = cst.parse_module(source_code)
    transformer = OCLTransformer()
    wrapped = MetadataWrapper(module)
    transformed_module = wrapped.module.visit(transformer)

    # Generate transformed versions
    ocl_printer_1 = transformed_module.code

    ocl_printer_2 = f"""
from pybooktools.ocl import OCLContainer
from pathlib import Path
import pickle
import inspect

oclgen = OCLContainer()

{ocl_printer_1}
oclgen.write(Path(r'{ocl_container_path}'))

# Save the environment including imports and definitions
with open(Path(r'{environment_path}'), 'wb') as env_file:
    pickle.dump({{
        name: obj
        for name, obj in globals().items()
        if inspect.isfunction(obj) or inspect.isclass(obj)
    }}, env_file)
"""

    # Write transformed versions
    ocl_printer_1_path.write_text(ocl_printer_1, encoding="utf-8")
    ocl_printer_2_path.write_text(ocl_printer_2, encoding="utf-8")

    run_script(ocl_printer_2_path)

    # Load the saved environment
    environment = pickle.loads(environment_path.read_bytes())
    globals().update(environment)

    # Ensure imported classes and enums are available
    exec(imports_and_definitions, globals())

    # Load the OCL container
    ocl_container = OCLContainer.read(ocl_container_path)
    ic(ocl_container)

    # Generate ocl_results
    ocl_results = ocl_printer_1
    ic(ocl_results)
    for ocl in ocl_container.ocls:
        ic(ocl)
        search = f"oclgen({ocl.ident}, {ocl.raw_print[6:-1]}, r'''{ocl.raw_print}''')"
        replace = f'{ocl.raw_print}\n{"\n".join(ocl.output_lines)}'
        ic(search)
        ic(replace)
        ocl_results = ocl_results.replace(search, replace)
        ic(ocl_results)

    ocl_results_path.write_text(ocl_results, encoding="utf-8")


if __name__ == "__main__":
    main()
