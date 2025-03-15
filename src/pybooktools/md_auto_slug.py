# md_auto_slug.py
"""
Automatically inserts a slug line (# example_N.py) at the beginning of
any Python code block in Markdown files that doesn't already have one.

Usage:
    python md_auto_slug.py --directory path/to/markdown_dir
    python md_auto_slug.py --file path/to/single_file.md

Description:
    - Searches for Markdown files with .md extension.
    - Finds Python fenced code blocks (```python ... ```).
    - Checks if the first non-blank line is a slug line (# example_N.py).
    - If not, inserts one.
    - Each code block in a file is given an incremental N in its slug.
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SlugInserter:
    """
    Dataclass to handle inserting slug lines in one or more Markdown files.
    """
    directory: Path
    single_file: Optional[Path] = None

    def _find_markdown_files(self) -> list[Path]:
        """
        Collect all .md files in the given directory. If single_file is specified,
        just return that file in a list.
        """
        if self.single_file is not None:
            return [self.single_file]
        return list(self.directory.rglob("*.md"))

    @staticmethod
    def _insert_slug_lines(content: str) -> str:
        """
        Insert slug lines before Python code blocks in the markdown content if they
        don't already have one. Each code block is detected by the pattern
        \"```python\" and ended by \"```\".

        Slug lines follow the pattern: \"# example_N.py\".

        Steps:
        1. Find each Python code block using a regex capturing (```python)(content)(```).
        2. Split the content into lines.
        3. Remove leading blank lines.
        4. If the first non-blank line is NOT already a slug, insert it.
        5. Reassemble and replace in the original text.
        """
        pattern = re.compile(r"(```python)(.*?)(```)", re.DOTALL)

        def replacer(match: re.Match[str]) -> str:
            block_start = match.group(1)  # "```python"
            block_content = match.group(2)
            block_end = match.group(3)  # "```"

            # Split on newlines (without discarding them all).
            lines = block_content.splitlines(keepends=False)

            # Remove all leading blank lines (lines that are empty after .strip()).
            while lines and not lines[0].strip():
                lines.pop(0)

            # If there's no content at all after removing leading blanks,
            # or we can't get a first line to check:
            if not lines:
                # There's nothing to annotate
                return match.group(0)

            # Check if the first non-blank line is already a slug
            first_line = lines[0].rstrip()
            slug_pattern = re.compile(r"^#\s*example_\d+\.py\s*$")
            if slug_pattern.match(first_line):
                # Already has a slug line
                return match.group(0)

            # Insert a slug line
            if not hasattr(replacer, "count"):
                replacer.count = 1
            else:
                replacer.count += 1

            slug_line = f"# example_{replacer.count}.py"
            lines.insert(0, slug_line)

            # Rebuild the code block content
            new_block_content = "\n".join(lines)

            # Return the entire code block with the inserted slug
            return f"{block_start}\n{new_block_content}\n{block_end}"

        return pattern.sub(replacer, content)

    def process_files(self) -> None:
        """
        Find Markdown files, read their content, insert slug lines, then rewrite the files.
        """
        md_files = self._find_markdown_files()
        for md_file in md_files:
            original_content = md_file.read_text(encoding='utf-8')
            updated_content = self._insert_slug_lines(original_content)
            md_file.write_text(updated_content, encoding='utf-8')


def main() -> None:
    """
    Entry point for the auto_slug_md script. Uses argparse to parse user inputs.
    """
    parser = argparse.ArgumentParser(
        description="""Automatically inserts a slug line (# example_N.py)
                       at the beginning of any Python code block in Markdown files
                       that doesn't already have one."""
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        default=".",
        help="Directory containing Markdown files. Defaults to the current directory."
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to a single Markdown file to process."
    )
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    single_file = Path(args.file).resolve() if args.file else None

    inserter = SlugInserter(directory=directory, single_file=single_file)
    inserter.process_files()


if __name__ == "__main__":
    main()
