# extractor.py
"""Extract code examples from Markdown files."""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory


@dataclass
class Example:
    """
    Represents an extracted code example from a markdown file.

    Attributes:
        filename: The filename as indicated in the slug line (e.g. "# example_1.py" or "// DefaultValues.java").
        content: The code content of the example (excluding the slug line).
        code_dir: The directory where the example will be written.
    """
    filename: str
    content: str
    code_dir: Path

    def __str__(self) -> str:
        full_path = " " + str(self.code_dir / self.filename) + " "
        return f"""\
---{full_path.center(70, "-")}---
{self.content.strip()}"""


def extract_examples(markdown_file: Path, code_repo: Path) -> List[Example]:
    """
    Extracts all fenced code examples containing a "slug line" from a markdown file.

    A slug line is the first line in a fenced code block that is a comment containing the
    filename (for example, "# example_1.py" or "// example_1.java"). This function supports
    multiple languages by matching any language tag in the code fence and by recognizing
    common comment markers.

    The directory is created from the markdown file name by:
      - Removing the '.md' extension.
      - Converting the name to lowercase.
      - Replacing spaces with underscores.

    Each extracted example is written into its own file within the target directory.

    Args:
        markdown_file: The markdown file to extract examples from.
        code_repo: The root directory under which the target directory will be created.
    """
    # Create target directory from markdown file name.
    target_dir_name = markdown_file.stem.lower().replace(" ", "_")
    code_directory = code_repo / "src" / target_dir_name

    # Read markdown file contents.
    markdown_text = markdown_file.read_text(encoding="utf-8")

    # Regular expression to match fenced code blocks.
    # This pattern matches any fenced block regardless of the language.
    code_block_pattern = re.compile(r"```[^\n]*\n(.*?)\n```", re.DOTALL)
    code_blocks = code_block_pattern.findall(markdown_text)

    # Regular expression to match a slug line as the first line of the code block.
    # Supports comment markers such as '#' and '//' and matches a filename with an extension.
    slug_line_pattern = re.compile(r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)")

    examples: List[Example] = []

    for block in code_blocks:
        lines = block.splitlines()
        if not lines:
            continue

        # Check if the first line is a slug line.
        match = slug_line_pattern.match(lines[0])
        if match:
            filename = match.group(1)
            content = "\n".join(lines).rstrip() + "\n"
            examples.append(Example(filename=filename, content=content, code_dir=code_directory))

    return examples


def write_examples(examples: List[Example]) -> None:
    # Write each example to its corresponding file in the code directory.
    for example in examples:
        example.code_dir.mkdir(parents=True, exist_ok=True)
        file_path = example.code_dir / example.filename
        file_path.write_text(example.content, encoding="utf-8")
        print(f"Extracted example written to: {file_path}")


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
    """Extract examples from a single markdown file to a repo directory."""
    examples = extract_examples(markdown_file, target_dir)
    for example in examples:
        print(example)
    # write_examples(examples)


@app.command(name="-d")
def extract_directory(markdown_dir: ResolvedExistingDirectory, target_dir: Path):
    """Extract examples from all markdown files in a directory to a repo directory."""
    markdown_files = list(markdown_dir.glob("*.md"))
    for markdown_file in markdown_files:
        examples = extract_examples(markdown_file, target_dir)
        # for example in examples:
        #     print(example)
        write_examples(examples)
