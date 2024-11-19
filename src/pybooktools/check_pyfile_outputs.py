#: check_pyfile_outputs.py
import ast
from pathlib import Path


class PrintTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call):
        # Replace print calls with track.print
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            node.func = ast.Attribute(
                value=ast.Name(id="track", ctx=ast.Load()),
                attr="print",
                ctx=ast.Load(),
            )
        return self.generic_visit(node)


class UnassignedStringTransformer(ast.NodeTransformer):
    def visit_Expr(self, node: ast.Expr):
        if isinstance(node.value, ast.Constant) and isinstance(
                node.value.value, str
        ):
            # Surround unassigned strings with track.expected
            new_node = ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="track", ctx=ast.Load()),
                        attr="expected",
                        ctx=ast.Load(),
                    ),
                    args=[node.value],
                    keywords=[],
                )
            )
            return ast.copy_location(new_node, node)
        return node


def transform_pyfile(pyfile: Path) -> None:
    # Read the original Python file
    source_code = pyfile.read_text(encoding="utf-8")
    tree = ast.parse(source_code)

    # Add the necessary import and global Tracker instance
    import_node = ast.ImportFrom(
        module="tracker",
        names=[ast.alias(name="Tracker", asname=None)],
        level=0,
    )
    tracker_instance_node = ast.Assign(
        targets=[ast.Name(id="track", ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id="Tracker", ctx=ast.Load()), args=[], keywords=[]
        ),
    )

    # Transform print calls and unassigned strings
    tree = PrintTransformer().visit(tree)
    tree = UnassignedStringTransformer().visit(tree)

    # Add the new import and tracker instance at the beginning
    tree.body.insert(0, tracker_instance_node)
    tree.body.insert(0, import_node)

    # Fix missing locations
    ast.fix_missing_locations(tree)

    # Write the transformed code to a new file
    transformed_code = ast.unparse(tree)
    new_file_path = pyfile.with_name(
        f"{pyfile.stem}_transformed{pyfile.suffix}"
    )
    new_file_path.write_text(
        transformed_code + "\ntrack.compare()\n", encoding="utf-8"
    )


if __name__ == "__main__":
    pyfile_path = Path("test.py")  # Change to the path of your file
    transform_pyfile(pyfile_path)
