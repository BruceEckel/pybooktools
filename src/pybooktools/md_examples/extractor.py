# extractor.py
"""Extract code examples from Markdown files."""
from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

from examples import examples_with_sluglines, write_examples

app = App(
    version_flags=[],
    # console=console,
    # help_format="plaintext",
    help_flags="-h",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


@app.command(name="-e")
def extract(markdown_file: Path, target_dir: Path):
    """Extract examples from a single markdown file to a example_repo directory."""
    print(f" {markdown_file.name} ".center(80, "-"))
    print(f"  extracting to {target_dir}  ".center(80, "-"))
    examples = examples_with_sluglines(markdown_file, target_dir)
    write_examples(examples)


@app.command(name="-d")
def extract_directory(markdown_dir: ResolvedExistingDirectory, target_dir: Path):
    """Extract examples from all markdown files in a directory to a example_repo directory."""
    for markdown_file in list(markdown_dir.glob("*.md")):
        extract(markdown_file, target_dir)
