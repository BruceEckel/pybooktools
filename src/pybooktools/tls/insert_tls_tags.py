"""
insert_top_level_separators(script: str) -> str

Takes a string containing a Python script and divides it into top-level statements.
It doesn't change any of the original code, but inserts lines containing:

print("__$n$_tls__")

(where n is an incremented int) after each top level statement.
The function returns the resulting string.
"""

import ast

from check_utils import UseCase, check_string_transformer


def insert_top_level_separators(script: str) -> str:
    """
    Inserts `print("__$n$_tls__")` between top-level statements in a Python script.

    Args:
        script: A string containing the Python script.

    Returns:
        A string with a special `print` statement inserted after each top-level statement.
    """

    class TopLevelInserter(ast.NodeVisitor):
        def __init__(self):
            self.lines = script.splitlines(keepends=True)
            self.insertions = []
            self.counter = 1

        def visit_Module(self, node: ast.Module) -> None:
            # Collect top-level statements
            for child in node.body:
                if hasattr(
                        child, "end_lineno"
                ):  # Ensure it's a statement with an end line number
                    self.insertions.append(
                        (child.end_lineno, f'print("__$self.counter$_tls__")\n')
                    )
                    self.counter += 1

        def apply_insertions(self) -> str:
            # Insert lines in reverse to maintain line number integrity
            for lineno, print_statement in reversed(self.insertions):
                self.lines.insert(lineno, print_statement)
            return "".join(self.lines)

    # Parse the script into an AST
    tree = ast.parse(script)

    # Traverse and collect top-level statements
    inserter = TopLevelInserter()
    inserter.visit(tree)

    # Apply the collected insertions and return the modified script
    return inserter.apply_insertions()


use_cases = [
    UseCase(
        case_id=1,
        script="""
x = 42
def greet():
    print("Hello, world!")

if x > 10:
    greet()
else:
    print("Goodbye!")
    
while True:
    print("Hello, world!")
    break
        """,
        expected_output="""
x = 42
print("__$1$_tls__")

def greet():
    print("Hello, world!")
print("__$2$_tls__")

if x > 10:
    greet()
else:
    print("Goodbye!")
print("__$3$_tls__")

        """,
    )
]

if __name__ == "__main__":
    check_string_transformer(insert_top_level_separators, use_cases)

""" Output From check_operation:

================ Case 1 failed ================
**** Script ****
_______________________________
x = 42
def greet():
    print("Hello, world!")

if x > 10:
    greet()
else:
    print("Goodbye!")
    
while True:
    print("Hello, world!")
    break
_______________________________
**** Actual ****
_______________________________
x = 42
print("__$self.counter$_tls__")
def greet():
    print("Hello, world!")
print("__$self.counter$_tls__")

if x > 10:
    greet()
else:
    print("Goodbye!")
print("__$self.counter$_tls__")
    
while True:
    print("Hello, world!")
    breakprint("__$self.counter$_tls__")
_______________________________
**** Expected ****
_______________________________
x = 42
print("__$1$_tls__")

def greet():
    print("Hello, world!")
print("__$2$_tls__")

if x > 10:
    greet()
else:
    print("Goodbye!")
print("__$3$_tls__")
_______________________________
**** Differences ****
--- Actual
+++ Expected
@@ -1,15 +1,12 @@
 x = 42
-print("__$self.counter$_tls__")
+print("__$1$_tls__")
+
 def greet():
     print("Hello, world!")
-print("__$self.counter$_tls__")
+print("__$2$_tls__")
 
 if x > 10:
     greet()
 else:
     print("Goodbye!")
-print("__$self.counter$_tls__")
-    
-while True:
-    print("Hello, world!")
-    breakprint("__$self.counter$_tls__")
+print("__$3$_tls__")

"""
