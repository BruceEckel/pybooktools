# demo_dir.py
"""
Creates and manages a demo directory structure from a given input string of the form:
[demo_dir_name]
---              # Create in demo_dir_name
print('Valid')
print('Example #1')
--- foo          # Create in demo_dir_name/foo
print('Another')
print('Valid')
print('Example #2')
--- bar          # Create in demo_dir_name/bar
print('Valid')
print('Example')
print('#3')
--- bar/baz      # Create in demo_dir_name/bar/baz
print('No slug line')
print('Example #4')
print('long enough')
--- baz/qux      # Create in demo_dir_name/baz/qux
print('For loop')
for i in range(5):
    print(f"{i = } Example #5")
--- baz/qux/zap  # Create in demo_dir_name/baz/qux/zap
print('While')
i = 0
while i < 5:
    i += 1
    print(f"{i = } Example #6")
--- named_file.py  # Create in demo_dir_name/named_file.py
print('Named file')
print('Example #7')
--- bun/another_named_file.py  # Create in demo_dir_name/bun/another_named_file.py
print('Another named file')
print('Example #8')
"""

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


def parse_demo_dir_name(lines: list[str]) -> tuple[Path, list[str]]:
    """
    Find the line containing [some_directory_name], extract that name, and
    return the corresponding Path plus the remaining lines after that line.

    This version skips all lines before the '[directory_name]' line so that
    docstring text preceding it doesn't become part of the first example.

    Args:
        lines: A list of lines (strings).

    Returns:
        A tuple: (Path(directory_name), list_of_remaining_lines_after_that_line)

    Raises:
        ValueError: If the pattern '[dir_name]' is not found in the list of lines.
    """
    start_index = next(
        (i for i, line in enumerate(lines) if re.match(r"^\[.+]$", line.strip())),
        None
    )
    if start_index is None:
        raise ValueError("Input text does not contain a valid directory name in square brackets.")

    dir_line = lines[start_index].strip(" []")  # e.g. "demo_dir_name"
    remaining = lines[start_index + 1:]  # All lines after the directory line
    return Path(dir_line), remaining


def extract_path_part(block_line: str) -> str:
    """
    Given a line starting with '---', extract the portion after '---' and before any '#' comment.
    Then strip whitespace. This part could be:
      - a directory path, e.g. 'foo' or 'bar/baz'
      - or a fully qualified .py filename, e.g. 'some_file.py' or 'foo/bar.py'.

    Args:
        block_line: A string starting with '---'.

    Returns:
        The candidate path or empty string if none is provided.
    """
    # Remove the leading '---' and split on '#'
    candidate = block_line[3:].split('#', 1)[0].strip()
    return candidate


def split_directory_and_filename(root_dir: Path, candidate: str) -> tuple[Path, str | None]:
    """
    Split the candidate path into a directory path and optional filename. If it ends with ".py",
    treat everything before the last slash (if any) as the directory path, and the final
    component as the actual filename. Otherwise, treat the entire candidate as a directory,
    returning None as the filename (auto-generate later).

    Example:
      candidate = "foo/bar.py"
        -> dir_path = target_path / "foo"
        -> filename = "bar.py"

      candidate = "foo/bar"
        -> dir_path = target_path / "foo/bar"
        -> filename = None   (auto-generate)

      candidate = "named_file.py"
        -> dir_path = target_path
        -> filename = "named_file.py"

      candidate = ""
        -> dir_path = target_path
        -> filename = None   (auto-generate)
    """
    path_obj = Path(candidate)
    if candidate.endswith(".py"):
        # Separate the final file component from any parent dirs
        if path_obj.parent.name == "." and path_obj.parent != path_obj:
            return root_dir, path_obj.name
        else:
            return root_dir / path_obj.parent, path_obj.name
    else:
        # It's a directory path or empty => let Example auto-generate .py name
        return root_dir / path_obj, None


def parse_file_blocks(lines: list[str], root_dir: Path) -> list["Example"]:
    """
    Parse lines that define file blocks in the format:
      ---
      <python code>
      ---
      <python code>
    to build `Example` objects.

    Args:
        lines: Lines after removing the directory name line.
        root_dir: The resolved directory where the examples will be stored.

    Returns:
        A list of Example objects.
    """
    from_line_blocks: list[str] = []
    examples: list[Example] = []
    current_dir: Path = root_dir
    current_filename: str | None = None
    current_label: str | None = None

    # Reset the Example class counter before building new ones
    Example.reset_counter()

    for line in lines:
        if line.startswith('---'):
            # If there is a current block, finalize it into an Example
            if from_line_blocks:
                examples.append(
                    Example(
                        dir_path=current_dir,
                        filename=current_filename,
                        input_text="\n".join(from_line_blocks),
                        original_label=current_label
                    )
                )
                from_line_blocks.clear()

            # Extract the path part from the line
            candidate_path = extract_path_part(line)
            current_dir, current_filename = split_directory_and_filename(root_dir, candidate_path)
            # Save the exact text as typed by the user
            current_label = candidate_path if candidate_path else None

        else:
            from_line_blocks.append(line)

    # If there's a remaining block after the loop ends, build the last Example
    if from_line_blocks:
        examples.append(
            Example(
                dir_path=current_dir,
                filename=current_filename,
                input_text="\n".join(from_line_blocks),
                original_label=current_label
            )
        )

    return examples


@dataclass
class Example:
    """
    Represents a single Python example file in a demo directory. Handles parsing of input text,
    determining a filename (if not explicitly provided), writing to disk, and providing string representations.
    """

    id_counter: ClassVar[int] = 0
    demo_dir_path: ClassVar[Path] = field(init=False)

    dir_path: Path
    input_text: str
    filename: str | None = field(default=None)  # If None, we auto-generate or extract from a slug line
    original_label: str | None = field(default=None)  # The user-typed label (e.g. "foo", "named_file.py")

    example_text: str = field(init=False)
    lines: list[str] = field(init=False)
    _final_filename: str = field(init=False)
    _relative_path: str = field(init=False)
    _repr_label: str = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the Example by processing its input_text, determining a filename if needed,
        and storing its relative path for string representations.
        """
        self.input_text = self.input_text.strip()
        self.lines = self.input_text.splitlines()

        # If user didn't provide an explicit filename, see if the block includes '--- <something>.py'
        # else auto-generate a unique filename.
        if not self.filename:
            extracted = self._extract_filename_from_slugline()
            self._final_filename = extracted or self._generate_filename()
        else:
            self._final_filename = self.filename

        # Insert or fix the slug line
        self._ensure_slug_line()
        self.example_text = "\n".join(self.lines)

        # Compute relative path from the top-level demo directory
        rel_path = self.dir_path.resolve().relative_to(self.demo_dir_path.resolve())
        self._relative_path = rel_path.as_posix() if rel_path != Path('') else '.'

        # Decide what to show in the "repr" after "--- "
        # 1) If we have an original_label, that means the user typed it. Use it.
        # 2) Otherwise, try to guess from the directory and filename
        if self.original_label is not None:
            self._repr_label = self.original_label or '.'  # if empty => '.'
        else:
            self._repr_label = self._compute_auto_label()

    @classmethod
    def reset_counter(cls) -> None:
        """Reset the global counter for auto-generated filenames."""
        cls.id_counter = 0

    def _extract_filename_from_slugline(self) -> str | None:
        """
        If the first line starts with '--- <something>.py', extract <something>.py if present.
        Returns the extracted filename or None if not found.
        """
        if not self.lines:
            return None
        match_obj = re.match(r"^---\s*([\w/.\-]+\.py)", self.lines[0])
        return match_obj.group(1) if match_obj else None

    @staticmethod
    def _generate_filename() -> str:
        """Auto-generate a unique filename like 'example_1.py'."""
        Example.id_counter += 1
        return f"example_{Example.id_counter}.py"

    def _ensure_slug_line(self) -> None:
        """
        Ensure the first line of the example is a slug line in the form "# <filename>".
        Overwrite or insert if needed.
        """
        slugline_pattern = re.compile(r"^#\s*([\w/]+\.py)")
        expected_slug = f"# {self._final_filename}"

        if self.lines and slugline_pattern.match(self.lines[0]):
            self.lines[0] = expected_slug
        else:
            self.lines.insert(0, expected_slug)

    def _compute_auto_label(self) -> str:
        """
        Compute a best-guess label (for use in repr) if we do not have a user-typed label.
        - If the dir_path is `.`, just show the filename (if not auto-generated, or `.` if auto).
        - If the filename is auto-generated, we might just show the subdirectory portion.
        - If the filename is user-provided, show subdir/filename.

        This is only used when we re-construct from disk and have no original_label.
        """
        # If there's no relative subdir (i.e. '.'), we either show the actual filename or '.' if auto-generated
        is_auto = self._final_filename.startswith("example_") and self._final_filename.endswith(".py")
        if self._relative_path == '.' and not is_auto:
            # We have a real user-provided .py filename, so show that
            return self._final_filename
        elif self._relative_path == '.' and is_auto:
            return '.'
        elif is_auto:
            # Show just the relative subdirectory portion
            return self._relative_path
        else:
            # We have a user-provided filename in some subdirectory
            return f"{self._relative_path}/{self._final_filename}"

    @property
    def file_path(self) -> Path:
        """The full path for the example."""
        return self.dir_path / self._final_filename

    def write_to_disk(self) -> None:
        """Write the example text to disk, creating parent dirs as needed."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(self.example_text + "\n", encoding="utf-8")

    def __repr__(self) -> str:
        """
        Debug-friendly string representation: shows the user-typed path if available (original_label),
        or else shows a best guess. Then the content minus the slug line.
        """
        slugline = f"# {self._final_filename}"
        content_without_slug = self.example_text.removeprefix(slugline).lstrip()
        return f"--- {self._repr_label}\n{content_without_slug}"

    def __str__(self) -> str:
        """User-friendly string representation with the path and full content."""
        return f"{self.file_path.as_posix()}:\n{self.example_text}"


@dataclass
class DemoDir:
    """
    Represents a demo directory containing multiple Python example files. Parses an input string
    to build directory paths and files, writes them to disk, and can later load the same structure
    from disk or delete it.
    """

    input_text: str
    input_lines: list[str] = field(init=False)
    dirpath: Path = field(init=False)
    examples: list[Example] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Perform initialization by extracting the directory name (and ignoring lines before it),
        parsing file blocks, then writing files to disk.
        """
        all_lines = self.input_text.strip().splitlines()

        # Extract directory name and skip lines before it
        parsed_dirpath, remaining_lines = parse_demo_dir_name(all_lines)
        self.dirpath = parsed_dirpath.resolve()
        Example.demo_dir_path = self.dirpath

        # Save the lines after extracting the dir name
        self.input_lines = remaining_lines

        # Parse the examples
        self.examples = parse_file_blocks(self.input_lines, self.dirpath)

        # Prepare and write
        self._prepare_directory()
        self._write_examples_to_disk()

    def _prepare_directory(self) -> None:
        """Recreate the directory from scratch."""
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)
        self.dirpath.mkdir(parents=True)

    def _write_examples_to_disk(self) -> None:
        """Write each example file to disk."""
        for example in self.examples:
            example.write_to_disk()

    @classmethod
    def from_file(cls, file_path: Path) -> "DemoDir":
        """
        Build a DemoDir from a file containing the input string.

        Args:
            file_path: A Path to the file.

        Returns:
            A DemoDir built from that file's contents.
        """
        content = file_path.read_text(encoding="utf-8")
        return cls(content)

    @classmethod
    def from_directory(cls, directory: Path) -> "DemoDir":
        """
        Build a DemoDir by scanning an existing directory for .py files and forming
        Example objects from each file's content.

        Args:
            directory: A Path representing the directory to scan.

        Returns:
            A DemoDir for the existing structure.
        """
        Example.reset_counter()
        found_examples = []
        # For each .py file, we no longer have a user-typed path. We'll set original_label=None
        for file in directory.rglob("*.py"):
            content = file.read_text(encoding="utf-8").strip()
            found_examples.append(
                Example(
                    dir_path=file.parent.resolve(),
                    filename=file.name,
                    input_text=content,
                    original_label=None  # We can't know what the user typed originally
                )
            )

        # We store minimal text here: just "[dirname]" so that parse_demo_dir_name sees it as well
        demo_dir = cls(f"[{directory.name}]")
        demo_dir.examples = found_examples
        return demo_dir

    def delete(self) -> None:
        """Delete the entire directory structure for this DemoDir instance."""
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)

    def __repr__(self) -> str:
        """
        For reconstructing the DemoDir
        """
        return f"[{self.dirpath.name}]\n" + "\n".join(repr(example) for example in self.examples)

    def __str__(self) -> str:
        """
        User-friendly string: shows `[dirpath.name]` plus the str of each example.
        """
        return f"[{self.dirpath.name}]\n" + "\n".join(str(example) for example in self.examples)

    def __iter__(self):
        """Iterate over contained examples."""
        return iter(self.examples)

    def show(self, msg: str | None = None) -> None:
        """
        For understanding & debugging.
        """

        def banner(msg: str) -> None:
            print(f" {msg} ".center(60, '-'))

        if msg:
            banner(msg)
        banner(self.dirpath.name)
        banner("str")
        print(self)
        banner("repr")
        print(repr(self))
        banner("Paths")
        for example in self:
            print(example.file_path)


if __name__ == "__main__":
    # Create a DemoDir from the docstring above
    examples_a = DemoDir(__doc__)
    examples_a.show("examples_a")

    # Now load the same structure back from the newly created directory
    examples_b = DemoDir.from_directory(examples_a.dirpath)
    examples_b.show("examples_b")

    # Then build a new DemoDir from the repr of examples_b
    examples_c = DemoDir(repr(examples_b))
    examples_c.show("examples_c")

    # Finally, delete the directory structure to clean up
    examples_b.delete()
