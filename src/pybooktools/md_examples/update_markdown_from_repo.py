# update_markdown_from_repo.py
import re
from pathlib import Path

from rich.console import Console

console = Console()


def pc(path_str: str) -> str:  # Path color
    return f"[steel_blue1]{path_str}[/steel_blue1]"


def nc(notification: str) -> str:  # Notification color
    return f"[dark_orange]{notification}[/dark_orange]"


def update_markdown_with_repo_examples(markdown_file: Path, example_repo: Path) -> str:
    """
    Reads a Markdown file containing Python examples within fenced code blocks,
    where each block starts with a "slug line" (a comment containing the filename).
    It then replaces each fenced example with the corresponding Python file's content
    from the given repository directory.

    A slug line is defined as the first line in the fenced code block that is a comment,
    for example: "# example_1.py" or "// example_1.py". The Python file in the repo directory
    with that filename is read and its content is inserted in a new fenced block (with the
    "python" language tag).

    Code blocks with slug lines containing a '/' character are ignored; these are book utilities.

    Args:
        markdown_file: The Markdown file to process.
        example_repo: The directory containing Python examples. Each example must have a filename
              corresponding to its slug line in the Markdown file.

    Returns:
        A new version of the Markdown file as a string, with the fenced examples replaced
        by the contents of the corresponding Python files.
    """
    # Read the original markdown content.
    markdown_text = markdown_file.read_text(encoding="utf-8")

    # Pattern to match a fenced python code block starting with a slug line.
    # Group 1: opening fence (e.g. "```python\n")
    # Group 2: slug line including comment marker (e.g. "# example_1.py\n")
    # Group 3: the filename from the slug line (e.g. "example_1.py")
    # Group 4: the rest of the code block (which will be replaced)
    fenced_python_block = re.compile(
        r"(```python\s*\n)"  # opening fence with language tag.
        r"(\s*(?:#|//)\s*(\S+\.py)\s*\n)"  # slug line: commented filename.
        r"(.*?)"  # the rest of the code block.
        r"\n```",  # closing fence.
        re.DOTALL
    )

    def replacer(match: re.Match) -> str:
        example_name: str = match.group(3)
        if "/" in example_name:
            console.print(nc("Skipping book utility ") + pc(example_name))
            return match.group(0)
        example_path: Path = example_repo / example_name
        try:
            # Read the content of the corresponding file.
            file_content: str = example_path.read_text(encoding="utf-8").rstrip()
        except Exception as e:
            raise FileNotFoundError(f"Could not read file {example_path}: {e}")
        # Return a new fenced code block with the file's content.
        return f"```python\n{file_content}\n```"

    # Substitute all matching code blocks with the updated content.
    new_markdown: str = fenced_python_block.sub(replacer, markdown_text)
    return new_markdown
