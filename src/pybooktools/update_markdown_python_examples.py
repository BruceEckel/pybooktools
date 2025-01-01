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
from pathlib import Path
from typing import Annotated

import typer

from pybooktools.python_chapter.python_chapter import PythonChapter
from pybooktools.util.typer_help_error import HelpError

app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
    rich_markup_mode="rich",
)


@app.command(no_args_is_help=True)
def main(
        ctx: typer.Context,
        python_markdown_chapter: Annotated[str, typer.Argument(
            ..., help="Path to the Python chapter to be updated."
        )]
):
    """Update Python slugline-marked source-code listings within a Python chapter."""

    help_error = HelpError(ctx)

    try:
        python_chapter = PythonChapter(Path(python_markdown_chapter))

        if python_chapter.differences:
            python_chapter.update_markdown_examples()
            python_chapter.write_updated_chapter()

        python_chapter.change_report()
    except ValueError as e:
        help_error(e.args[0])


if __name__ == "__main__":
    app()
