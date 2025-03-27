# injector.py
import re
from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory


def update_markdown_with_repo_examples(markdown_file: Path, repo: Path) -> str:
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
        repo: The directory containing Python examples. Each example must have a filename
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
        r"(\s*(?:#|//)\s*(\S+\.py)\s*\n)"  # slug line: comment marker and filename.
        r"(.*?)"  # the rest of the code block.
        r"\n```",  # closing fence.
        re.DOTALL
    )

    def replacer(match: re.Match) -> str:
        file_name: str = match.group(3)
        if "/" in file_name:
            print(f"Skipping book utility {file_name}")
            return match.group(0)
        file_path: Path = repo / file_name
        try:
            # Read the content of the corresponding file.
            file_content: str = file_path.read_text(encoding="utf-8").rstrip()
        except Exception as e:
            raise FileNotFoundError(f"Could not read file {file_path}: {e}")
        # Return a new fenced code block with the file's content.
        return f"```python\n{file_content}\n```"

    # Substitute all matching code blocks with the updated content.
    new_markdown: str = fenced_python_block.sub(replacer, markdown_text)
    return new_markdown


app = App(
    version_flags=[],
    help_flags="-h",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


@app.command(name="-i")
def update_markdown_files(markdown_files: ResolvedExistingDirectory, root_repo: ResolvedExistingDirectory) -> None:
    """ Inject examples into markdown files from repo"""
    """
    For each Markdown file in the directory `markdown_files`, produces the corresponding
    subdirectory under `root_repo` by lowercasing the file name (without the trailing '.md').
    It then calls `update_markdown_with_repo_examples` with that Markdown file and subdirectory,
    updating the Markdown file with the contents of the corresponding Python examples from the repo.

    Args:
        markdown_files: Directory containing Markdown files with Python examples in code fences.
        root_repo: Directory containing subdirectories with Python example files corresponding to each Markdown file.
    """
    # Iterate over all Markdown files in the provided directory.
    for md_file in markdown_files.iterdir():
        if md_file.is_file() and md_file.suffix.lower() == ".md":
            # Compute subdirectory name: lowercase the markdown file name (without '.md').
            subdir_name: str = md_file.stem.lower()
            repo_subdir: Path = root_repo / subdir_name
            print(f"Processing {md_file.name} with repo subdir {repo_subdir}")
            if not repo_subdir.exists():
                print(f"Warning: Repository subdirectory {repo_subdir} does not exist for {md_file.name}. Skipping.")
                continue

            try:
                updated_content: str = update_markdown_with_repo_examples(md_file, repo_subdir)
            except FileNotFoundError as err:
                print(f"Error processing {md_file.name}: {err}")
                continue

            # Overwrite the markdown file with the updated content.
            md_file.write_text(updated_content, encoding="utf-8")
            print(f"Updated {md_file.name} with content from {repo_subdir}")
