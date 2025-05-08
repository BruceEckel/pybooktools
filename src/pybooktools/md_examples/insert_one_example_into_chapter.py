import difflib
import re
from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingPath
from rich.console import Console

console = Console()

app = App(
    version_flags=[],
    help_flags="-h",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


def pc(path_str: str) -> str:
    """Colorize file paths in steel_blue1 for console output."""
    return f"[steel_blue1]{path_str}[/steel_blue1]"


def nc(notification: str) -> str:
    """Colorize notifications in dark_orange for console output."""
    return f"[dark_orange]{notification}[/dark_orange]"


@app.command(name="-i")
def insert_example(example_path: ResolvedExistingPath, replace: bool = False) -> None:
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
    for md in Path.cwd().rglob("*.md"):
        if md.stem.lower() == chapter_key:
            markdown_file = md
            break

    if markdown_file is None:
        raise FileNotFoundError(f"Could not find chapter file for '{chapter_key}'")

    console.print(nc("Found chapter ") + pc(str(markdown_file)))
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

    old_content = match.group("content").rstrip()
    new_content = example_path.read_text(encoding="utf-8").rstrip()

    # 3️⃣ Compare and handle accordingly
    if old_content != new_content:
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
            new_block = f"```python\n{new_content}\n```"
            updated = block_re.sub(new_block, markdown_text, count=1)
            markdown_file.write_text(updated, encoding="utf-8")
            console.print(nc("Replaced example ") + pc(example_name))
    else:
        console.print(nc("No changes for ") + pc(example_name))
