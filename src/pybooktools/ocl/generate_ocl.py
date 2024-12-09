import argparse
import shutil
from pathlib import Path

import libcst as cst
from libcst.metadata import MetadataWrapper

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


def main():
    parser = argparse.ArgumentParser(
        description="Generate OCL script and transform."
    )
    parser.add_argument("filename", type=str, help="Python file to process.")
    args = parser.parse_args()
    example_path = Path(args.filename).resolve()

    check_dir = example_path.parent / f".check_{example_path.stem}"
    if check_dir.exists():
        shutil.rmtree(check_dir)
    check_dir.mkdir()

    ocl_printer_1_path = check_dir / f"{example_path.stem}_1.py"
    ocl_printer_2_path = check_dir / f"{example_path.stem}_2.py"

    source_code = example_path.read_text(encoding="utf-8")

    # Extract imports
    imports = []
    module = cst.parse_module(source_code)
    for stmt in module.body:
        if isinstance(stmt, (cst.Import, cst.ImportFrom)):
            imports.append(cst.Module([]).code_for_node(stmt))

    # Process with libcst
    transformer = OCLTransformer()
    wrapped = MetadataWrapper(module)
    transformed_module = wrapped.module.visit(transformer)

    # Generate transformed versions
    ocl_printer_1 = transformed_module.code
    imports_code = "\n".join(imports)

    ocl_printer_2 = f"""
from pathlib import Path
from pybooktools.ocl import OCLContainer

# Restore imports from the original script
{imports_code}

oclgen = OCLContainer()

{ocl_printer_1}

# Generate ocl_results dynamically
ocl_results = ""
for ocl in oclgen.ocls:
    search = f"oclgen({{ocl.ident}}, {{ocl.raw_print[6:-1]}}, r'''{{ocl.raw_print}}''')"
    replace = f"{{ocl.raw_print}}\\n{{'\\n'.join(ocl.output_lines)}}"
    ocl_results = ocl_results.replace(search, replace)

result_path = Path(r"{check_dir}") / "ocl_results.py"
result_path.write_text(ocl_results, encoding="utf-8")
"""

    # Write transformed versions
    ocl_printer_1_path.write_text(ocl_printer_1, encoding="utf-8")
    ocl_printer_2_path.write_text(ocl_printer_2, encoding="utf-8")

    run_script(ocl_printer_2_path)


if __name__ == "__main__":
    main()
