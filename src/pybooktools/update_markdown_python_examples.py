# update_markdown_python_examples.py
"""
Looks in Markdown files for listings with sluglines,
and updates those listings from the source code repository.
You must provide the path to at least one source code repository,
as a Markdown comment in the form:
<!-- #[code_location] ./src/functional_error_handling -->
These can appear anywhere in the file.
The path can be relative or absolute.
If you provide more than one source code repository, the program ensures
there are no duplicate file names across those directories.
"""

import argparse

from pybooktools.diagnostics import trace
from pybooktools.python_chapter.python_chapter import PythonChapter
from pybooktools.util import display_function_name


def main():
    parser = argparse.ArgumentParser(
        description="Update Python slugline-marked source-code listings within a Python chapter."
    )
    parser.add_argument(
        "python_markdown_chapter",
        help="Path to the Python chapter to be updated.",
    )
    parser.add_argument(
        "-t", "--trace", action="store_true", help="Enable tracing output"
    )
    args = parser.parse_args()

    if args.trace:
        trace.enable()
        display_function_name()

    python_chapter = PythonChapter(args.python_markdown_chapter)

    if python_chapter.differences:
        python_chapter.update_markdown_examples()
        python_chapter.write_updated_chapter()

    python_chapter.change_report()


if __name__ == "__main__":
    main()
