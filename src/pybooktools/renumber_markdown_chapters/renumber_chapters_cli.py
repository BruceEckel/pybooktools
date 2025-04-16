from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

from pybooktools.renumber_markdown_chapters.renumber_chapters import Book

app = App(
    version_flags=[],
    # console=console,
    # help_format="plaintext",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


@app.command(name="-r")
def renumber(path: ResolvedExistingDirectory = Path("..")):
    """Renumber the chapters, update mkdocs.yml"""
    book = Book(path)
    book.renumber()
    book.update_file_names()
    book.update_nav()
    print(book)


@app.command(name="-d")
def display(path: ResolvedExistingDirectory = Path("..")):
    """Display the existing chapters without renumbering"""
    print(Book(path))


@app.command(name="-t")
def trace_info(path: ResolvedExistingDirectory = Path("..")):
    """Display trace info, no changes"""
    print(" Trace info ".center(60, "-"))
    print(f"{path = }")
    book = Book(path)
    print(f"{book.directory = }")
    print(book)
    print(" Renumbered ".center(60, "-"))
    book.renumber()
    print(book)
    print(" updated_mkdocs_yml ".center(60, "-"))
    mdkocs_yml_path, updated_mkdocs_yml = book.updated_mkdocs_yml()
    print(f"{mdkocs_yml_path = }")
    print(updated_mkdocs_yml)


if __name__ == "__main__":
    app()
