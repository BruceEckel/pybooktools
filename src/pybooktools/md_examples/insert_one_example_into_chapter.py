# insert_one_example_into_chapter.py
import difflib
import re
from pathlib import Path

from cyclopts import App, Parameter
from cyclopts.types import ResolvedExistingPath
from rich.console import Console
from rich.panel import Panel
from rich.traceback import install

from pybooktools.util import config

# Install a rich handler that shows syntax-highlighted code snippets,
# local variables, and “pretty” formatting.
install(show_locals=True, width=120)

console = Console()

app = App(
    version_flags=[],
    help_flags="-h",
    help=__doc__,
    default_parameter=Parameter(negative=()),
)


def pc(path_str: str) -> str:
    """Colorize file paths in steel_blue1 for console output."""
    return f"[steel_blue1]{path_str}[/steel_blue1]"


def nc(notification: str) -> str:
    """Colorize notifications in dark_orange for console output."""
    return f"[dark_orange]{notification}[/dark_orange]"


@app.default
def insert_example(example_path: ResolvedExistingPath, replace: bool = False, verbose: bool = True) -> None:
    """
    Using example_path, figures out:
    1. What Markdown chapter this example came from (by matching the lowercase
       example_path.parent.name to md.stem.lower()).
    2. Where in the Markdown chapter this example lives (slug line + fenced block).
    3. If the example at example_path is different from the one in the chapter, it
       shows a unified diff.
    4. If `replace` is True and the example is different, replace it in the chapter.
    """
    example_name = example_path.name
    chapter_key = example_path.parent.name  # e.g. "c05_custom_types"

    # 1️⃣ Locate the chapter file by matching its stem.lower() to chapter_key
    markdown_file: Path | None = None
    for md in config.book_chapters.rglob("*.md"):
        if md.stem.lower() == chapter_key:
            markdown_file = md
            break

    if markdown_file is None:
        raise FileNotFoundError(f"Could not find chapter file for '{chapter_key}'")

    console.print(pc(str(markdown_file)))
    markdown_text = markdown_file.read_text(encoding="utf-8")

    # 2️⃣ Find the existing fenced python block with the slug line
    block_re = re.compile(
        rf"```python\s*\n"  # opening fence
        rf"\s*(?:#|//)\s*{re.escape(example_name)}\s*\n"  # slug line
        r"(?P<content>.*?)\n```"  # capture existing content
        , re.DOTALL
    )
    match = block_re.search(markdown_text)
    if not match:
        raise ValueError(f"Could not locate code block for {example_name} in {markdown_file}")

    # 3️⃣ Extract the old content including the slug line
    full_block = match.group(0)
    block_lines = full_block.splitlines()
    # drop the opening and closing fences, keeping slug + code lines
    old_content = "\n".join(block_lines[1:-1]).rstrip()
    new_content = example_path.read_text(encoding="utf-8").rstrip()

    # Compare and handle accordingly
    if old_content != new_content:
        if verbose:
            # Display panels for before/after
            panel = Panel(
                old_content,
                title=f"Markdown: {example_name}",
                title_align="left",
                style="dark_orange",
            )
            console.print(panel)
            panel = Panel(
                new_content,
                title=f"Example: {example_name}",
                title_align="left",
                style="dark_orange",
            )
            console.print(panel)

        # Show unified diff
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=str(markdown_file),
            tofile=str(example_path),
            lineterm="",
        )
        for line in diff:
            console.print(line)

        # 4️⃣ Replace if requested
        if replace:
            # Reconstruct a new block with slug line + updated content
            slug_line = block_lines[1]
            new_block = f"```python\n{slug_line}\n{new_content}\n```"
            updated = block_re.sub(new_block, markdown_text, count=1)
            markdown_file.write_text(updated, encoding="utf-8")
            console.print(nc("Replaced example ") + pc(example_name))
    else:
        console.print(nc("No update: ") + pc(example_name))
