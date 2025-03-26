# extractor.py
"""Extract code examples from Markdown files."""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

# Matches fenced code blocks.
code_block_pattern = re.compile(r"```[^\n]*\n(.*?)\n```", re.DOTALL)

# Matches a slug line; supports different comment markers and matches a filename with an extension.
slug_line_pattern = re.compile(r"^\s*(?:#|//)\s*(\S+\.[a-zA-Z0-9_]+)")


@dataclass
class Example:
    """
    Represents an extracted code example from a markdown file.

    Attributes:
        filename: The filename as extracted from the slug line (e.g. "# example_1.py" or "// DefaultValues.java").
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

    If a slugline contains a '/' character, the file will be written to a corresponding
    path from the root directory under the 'src' directory.

    Args:
        markdown_file: The markdown file to extract examples from.
        code_repo: The root directory under which the target directory will be created.
    """
    # Create target directory from markdown file name:
    target_dir_name = markdown_file.stem.lower().replace(" ", "_")
    # Parse code blocks from file:
    markdown_text = markdown_file.read_text(encoding="utf-8")
    code_blocks = code_block_pattern.findall(markdown_text)

    examples: List[Example] = []

    for block in code_blocks:
        lines = block.splitlines()
        if not lines:
            continue

        # Check if the first line is a slug line.
        match = slug_line_pattern.match(lines[0])
        if match:
            filename = match.group(1)
            parts = filename.split('/')
            code_dir = code_repo / "src"
            if '/' in filename:
                for part in parts[:-1]:
                    code_dir = code_dir / part
                code_dir.mkdir(parents=True, exist_ok=True)
            else:
                code_dir = code_dir / target_dir_name

            content = "\n".join(lines).rstrip() + "\n"
            examples.append(Example(filename=parts[-1], content=content, code_dir=code_dir))

    return examples


def write_examples(examples: List[Example]) -> None:
    # Write each example to its corresponding file in the code directory.
    for example in examples:
        example.code_dir.mkdir(parents=True, exist_ok=True)
        file_path = example.code_dir / example.filename
        file_path.write_text(example.content, encoding="utf-8")
        print(f"{file_path}")


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
    print(f" {markdown_file.name} -> {target_dir} ".center(80, "-"))
    examples = extract_examples(markdown_file, target_dir)
    for example in examples:
        print(example.filename)
    write_examples(examples)


@app.command(name="-d")
def extract_directory(markdown_dir: ResolvedExistingDirectory, target_dir: Path):
    """Extract examples from all markdown files in a directory to a repo directory."""
    for markdown_file in list(markdown_dir.glob("*.md")):
        extract(markdown_file, target_dir)
        # examples = extract_examples(markdown_file, target_dir)
        # # for example in examples:
        # #     print(example)
        # write_examples(examples)
