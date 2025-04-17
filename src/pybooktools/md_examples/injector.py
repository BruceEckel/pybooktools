# injector.py
from pathlib import Path

from cyclopts import App
from cyclopts.types import ResolvedExistingDirectory

from pybooktools.md_examples.update_markdown_from_repo import pc, nc, update_markdown_with_repo_examples, console

app = App(
    version_flags=[],
    help_flags="-h",
    help=__doc__,
    # default_parameter=Parameter(negative=()),
)


@app.command(name="-i")
def update_markdown_files(markdown_files: ResolvedExistingDirectory, example_repo: ResolvedExistingDirectory) -> None:
    """ Inject examples from example_repo into markdown files"""
    """
    For each Markdown file in the directory `markdown_files`, produces the corresponding
    subdirectory under `example_repo` by lowercasing the file name (without the trailing '.md').
    It then calls `update_markdown_with_repo_examples` with that Markdown file and subdirectory,
    updating the Markdown file with the contents of the corresponding Python examples from the example_repo.

    Args:
        markdown_files: Directory containing Markdown files with Python examples in code fences.
        example_repo: Directory containing subdirectories with Python example files corresponding to each Markdown file.
    """
    # Iterate over all Markdown files in the provided directory.
    for md_file in markdown_files.iterdir():
        if md_file.is_file() and md_file.suffix.lower() == ".md":
            # Compute repo subdirectory name
            repo_subdir: Path = example_repo / md_file.stem.lower()
            if not repo_subdir.exists():
                console.print(
                    nc("Skipping missing subdirectory ") +
                    f"{pc(repo_subdir.name)} for {pc(md_file.name)}"
                )
                continue

            console.print(f"Processing {md_file.name} with example_repo subdir {repo_subdir.name}")
            try:
                updated_content: str = update_markdown_with_repo_examples(md_file, repo_subdir)
            except FileNotFoundError as err:
                console.print(f"[red]Error processing[/red] {md_file.name}: {err}")
                continue

            # Overwrite the markdown file with the updated content.
            # if updated_content != md_file.read_text(encoding="utf-8"):
            #     md_file.write_text(updated_content, encoding="utf-8")
            #     console.print(f"[green]Updated[/green] {pc(md_file.name)} with {pc(repo_subdir.name)}")
