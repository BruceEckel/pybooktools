import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import libcst as cst
import libcst.matchers as m


def process_script(file_path: Path) -> tuple[str, str]:
    class OCLTransformer(cst.CSTTransformer):
        def __init__(self):
            super().__init__()
            self.counter = 0

        def leave_SimpleStatementLine(
            self,
            original_node: cst.SimpleStatementLine,
            updated_node: cst.SimpleStatementLine,
        ) -> cst.SimpleStatementLine:
            # Match a top-level print statement
            if m.matches(
                original_node,
                m.SimpleStatementLine(
                    body=[m.Expr(value=m.Call(func=m.Name("print")))]
                ),
            ):
                self.counter += 1
                # Extract the print() call by ensuring the node type
                expr = original_node.body[0]
                if isinstance(expr, cst.Expr) and isinstance(
                    expr.value, cst.Call
                ):
                    call = expr.value  # Safely access the Call node

                    # Handle print arguments
                    arg = call.args[0].value
                    ocl_var = f"o{self.counter}"

                    # Generate the replacement OCL code
                    new_statement = cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[
                                    cst.AssignTarget(target=cst.Name(ocl_var))
                                ],
                                value=cst.Call(
                                    func=cst.Name("OCL"),
                                    args=[cst.Arg(value=arg)],
                                ),
                            )
                        ]
                    )
                    return new_statement

            return updated_node

    # Read and parse the file
    code = file_path.read_text(encoding="utf-8")
    tree = cst.parse_module(code)

    # Extract and preserve imports
    import_lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import") or stripped.startswith("from"):
            import_lines.append(line)

    # Apply transformation
    transformer = OCLTransformer()
    updated_tree = tree.visit(transformer)

    # Generate the OCL-instrumented code with original imports
    ocl_printer = "\n".join(import_lines) + "\n" + updated_tree.code

    # Execute the OCL code
    exec_env = {}
    exec(ocl_printer, globals(), exec_env)

    # Generate the resulting output
    ocl_result_lines = []
    counter = 1
    for line in code.splitlines():
        if line.strip().startswith("print("):
            ocl_var = f"o{counter}"
            ocl_obj: OCL = exec_env[ocl_var]
            ocl_result_lines.append(line)
            ocl_result_lines.append(ocl_obj.output)
            counter += 1
        else:
            ocl_result_lines.append(line)

    ocl_result = "\n".join(ocl_result_lines)
    return ocl_printer, ocl_result


# Example OCL implementation
@dataclass
class OCL:
    arg: Any
    result: list[str] = field(default_factory=list)
    output_lines: list[str] = field(default_factory=list)
    output: Optional[str] = None

    def __post_init__(self):
        from pprint import pformat

        # Use repr for dataclass objects and complex types
        if hasattr(self.arg, "__repr__"):
            repr_arg = repr(self.arg)
        else:
            repr_arg = pformat(self.arg, width=47)

        self.result = repr_arg.splitlines()
        self.output_lines = [
            "#| " + line for line in self.result if line.strip()
        ]
        self.output = "\n".join(self.output_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Process a Python script to replace print statements with OCL instances."
    )
    parser.add_argument(
        "input", type=Path, help="Path to the input Python script."
    )
    args = parser.parse_args()

    input_path = args.input
    ocl_printer, ocl_result = process_script(input_path)

    # Output the results
    output_printer_path = input_path.with_name("ocl_printer.py")
    output_result_path = input_path.with_name("ocl_result.py")

    output_printer_path.write_text(ocl_printer, encoding="utf-8")
    output_result_path.write_text(ocl_result, encoding="utf-8")

    print(f"Instrumented code written to: {output_printer_path}")
    print(f"Resulting code written to: {output_result_path}")


if __name__ == "__main__":
    main()
