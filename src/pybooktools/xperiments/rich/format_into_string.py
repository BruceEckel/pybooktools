# format_into_string.py
from rich.syntax import Syntax

from pybooktools.util.console import console

code = """\
def hello_world():
    print("Hello, World!")\
"""


def syntax_highlight(code: str) -> str:
    syntax = Syntax(code, "python", theme="monokai")
    with console.capture() as capture:
        console.print(syntax)
    # Get the highlighted code as a string
    return capture.get()


# Create a Syntax object
syntax = Syntax(code, "python", theme="monokai")

# Capture the output of the Syntax object
with console.capture() as capture:
    console.print(syntax)

# Get the highlighted code as a string
highlighted_code = capture.get()

print(highlighted_code)
