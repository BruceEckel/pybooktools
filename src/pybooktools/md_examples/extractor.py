# extractor.py
"""Extract code examples from Markdown files."""
from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory
from rich.console import Console

from pybooktools.md_examples import write_examples, examples_with_sluglines

console = Console()

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
    """Extract examples from a single markdown file to target_dir."""
    console.rule(markdown_file.name)
    examples = examples_with_sluglines(markdown_file, target_dir)
    write_examples(examples)


@app.command(name="-d")
def extract_directory(markdown_dir: ResolvedExistingDirectory, target_dir: Path):
    """Extract examples from all markdown files in a directory to target_dir."""
    console.rule(f"  extracting to {target_dir}  ")
    for markdown_file in list(markdown_dir.glob("*.md")):
        extract(markdown_file, target_dir)
