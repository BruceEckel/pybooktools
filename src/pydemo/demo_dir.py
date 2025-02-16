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


def banner(msg: str) -> None:
    """
    Print a banner with the given message, centered and surrounded by dashes for clarity.
    """
    print(f" {msg} ".center(60, '-'))


def parse_demo_dir_name(lines: list[str]) -> Path:
    """
    Extract the demo directory name from the first valid line enclosed in square brackets.

    Args:
        lines: A list of lines where one of them should match the pattern '[dir_name]'.

    Returns:
        A Path object representing the directory name.

    Raises:
        ValueError: If the pattern '[dir_name]' is not found in the list of lines.
    """
    start_index = next(
        (i for i, line in enumerate(lines) if re.match(r"^\[.+]$", line.strip())),
        None
    )
    if start_index is None:
        raise ValueError("Input text does not contain a valid directory name in square brackets.")

    # Extract the directory line, remove it from the list, and parse out the directory name
    dir_line = lines.pop(start_index).strip(" []")
    return Path(dir_line)


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
    we treat everything before the last slash (if any) as the directory path, and the final
    component as the actual filename. Otherwise, we treat the entire candidate as a directory,
    and return None for the filename to be auto-generated later.

    Example:
      candidate = "foo/bar.py"
        -> dir_path = root_dir / "foo"
        -> filename = "bar.py"

      candidate = "foo/bar"
        -> dir_path = root_dir / "foo/bar"
        -> filename = None   (auto-generate)

      candidate = "named_file.py"
        -> dir_path = root_dir
        -> filename = "named_file.py"

      candidate = ""
        -> dir_path = root_dir
        -> filename = None   (auto-generate)

    Args:
        root_dir: The base directory for these files.
        candidate: The extracted path portion (may or may not end with ".py").

    Returns:
        A 2-tuple: (dir_path, filename or None)
    """
    if candidate.endswith(".py"):
        # The user provided a .py file. Separate directory vs. the last component.
        # For example, "foo/bar.py" => path "foo", filename "bar.py".
        path_obj = Path(candidate)
        # If the parent is just ".", that means there's no subdirectory.
        if path_obj.parent.name == "." and path_obj.parent != path_obj:
            return root_dir, path_obj.name
        return root_dir / path_obj.parent, path_obj.name
    else:
        # The user gave a directory path (or nothing), so let the Example auto-generate the filename.
        return root_dir / candidate, None


def parse_file_blocks(lines: list[str], root_dir: Path) -> list["Example"]:
    """
    Parse lines that define file blocks in the format:
      ---
      <python code>
      ---
      <python code>
    to build `Example` objects.

    Args:
        lines: Remaining lines after removing the directory name line.
        root_dir: The resolved directory where the examples will be stored.

    Returns:
        A list of Example objects.
    """
    from_line_blocks: list[str] = []
    examples: list[Example] = []
    current_dir: Path = root_dir
    current_filename: str | None = None

    # Reset the Example class counter before building new ones
    Example.reset_counter()

    for line in lines:
        if line.startswith('---'):
            # If there is a current block accumulated, save it as an Example
            if from_line_blocks:
                examples.append(
                    Example(
                        dir_path=current_dir,
                        filename=current_filename,
                        input_text="\n".join(from_line_blocks),
                    )
                )
                from_line_blocks.clear()

            # Extract the path part from the line
            candidate_path = extract_path_part(line)
            current_dir, current_filename = split_directory_and_filename(root_dir, candidate_path)

        else:
            from_line_blocks.append(line)

    # If there's a remaining block after the loop ends, build the last Example
    if from_line_blocks:
        examples.append(
            Example(
                dir_path=current_dir,
                filename=current_filename,
                input_text="\n".join(from_line_blocks),
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
    filename: str | None = field(default=None)  # If None, we generate or extract from the block
    example_text: str = field(init=False)
    lines: list[str] = field(init=False)
    _final_filename: str = field(init=False)
    _relative_path: str = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the Example by processing its input_text, determining a filename if needed,
        and storing its relative path for string representations.
        """
        self.input_text = self.input_text.strip()
        self.lines = self.input_text.splitlines()

        # If user didn't provide an explicit filename, check if the first line starts with '--- <something>.py'
        # or else auto-generate a unique filename.
        if not self.filename:
            extracted = self._extract_filename_from_slugline()
            self._final_filename = extracted or self._generate_filename()
        else:
            self._final_filename = self.filename

        self._ensure_slug_line()
        self.example_text = "\n".join(self.lines)
        self._relative_path = (
            self.dir_path.resolve()
            .relative_to(self.demo_dir_path.resolve())
            .as_posix()
        )

    @classmethod
    def reset_counter(cls) -> None:
        """
        Reset the global counter used to auto-generate unique filenames.
        """
        cls.id_counter = 0

    def _extract_filename_from_slugline(self) -> str | None:
        """
        If the first line starts with '--- <something>.py', extract <something>.py if present.

        Returns:
            The extracted filename (as a string) or None if not found.
        """
        # e.g. the line could be: "--- foo/bar.py"
        # We'll see if it has a pattern that includes .py
        if not self.lines:
            return None
        match_obj = re.match(r"^---\s*([\w/.\-]+\.py)", self.lines[0])
        return match_obj.group(1) if match_obj else None

    @staticmethod
    def _generate_filename() -> str:
        """
        Auto-generate a unique filename using the global id_counter.

        Returns:
            A string representing the generated filename.
        """
        Example.id_counter += 1
        return f"example_{Example.id_counter}.py"

    def _ensure_slug_line(self) -> None:
        """
        Ensure the first line of the example is a slug line (i.e., '# <filename>').
        Overwrite any existing slug line if necessary.
        """
        slugline_pattern = re.compile(r"^#\s*([\w/]+\.py)")
        expected_slug = f"# {self._final_filename}"

        if self.lines and slugline_pattern.match(self.lines[0]):
            self.lines[0] = expected_slug
        else:
            # Insert a new slug line at the top
            self.lines.insert(0, expected_slug)

    @property
    def file_path(self) -> Path:
        """
        The full path where this example will be written.
        """
        return self.dir_path / self._final_filename

    def write_to_disk(self) -> None:
        """
        Create any necessary directories and write the example to the designated file path.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(self.example_text + "\n", encoding="utf-8")

    def __repr__(self) -> str:
        """
        String representation suitable for debugging. Shows the relative path
        and the content of the example (excluding the slug line).
        """
        slugline = f"# {self._final_filename}"
        content_without_slug = self.example_text.removeprefix(slugline).lstrip()
        return f"--- {self._relative_path}\n{content_without_slug}"

    def __str__(self) -> str:
        """
        A more user-friendly string representation showing the file path and content.
        """
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
        Perform initialization by extracting the directory name, parsing file blocks to build Example objects,
        preparing and writing the directory structure to disk.
        """
        self.input_lines = self.input_text.strip().splitlines()

        # Extract directory name and remove that line from the input lines
        self.dirpath = parse_demo_dir_name(self.input_lines).resolve()
        Example.demo_dir_path = self.dirpath

        # Parse examples into objects
        self.examples = parse_file_blocks(self.input_lines, self.dirpath)

        # Prepare the directory and write files
        self._prepare_directory()
        self._write_examples_to_disk()

    def _prepare_directory(self) -> None:
        """
        Clear any existing directory at self.dirpath and recreate it.
        """
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)
        self.dirpath.mkdir(parents=True)

    def _write_examples_to_disk(self) -> None:
        """
        Write each Example object to disk.
        """
        for example in self.examples:
            example.write_to_disk()

    @classmethod
    def from_file(cls, file_path: Path) -> "DemoDir":
        """
        Build a DemoDir from a file containing the input string.

        Args:
            file_path: A Path object pointing to the file.

        Returns:
            A DemoDir instance built by reading the file's contents.
        """
        content = file_path.read_text(encoding="utf-8")
        return cls(content)

    @classmethod
    def from_directory(cls, directory: Path) -> "DemoDir":
        """
        Build a DemoDir by scanning an existing directory for .py files and creating
        Example objects from each file's contents.

        Args:
            directory: A Path object representing the directory to scan.

        Returns:
            A DemoDir instance representing the existing structure.
        """
        Example.reset_counter()
        found_examples = [
            Example(
                dir_path=file.parent.resolve(),
                filename=file.name,  # we know the last part is the actual .py name
                input_text=file.read_text(encoding="utf-8").strip()
            )
            for file in directory.rglob("*.py")
        ]
        demo_dir = cls(f"[{directory.name}]")
        demo_dir.examples = found_examples
        return demo_dir

    def delete(self) -> None:
        """
        Delete the entire directory structure for this DemoDir instance.
        """
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)

    def __repr__(self) -> str:
        """
        Debug-friendly string representation that shows the directory name and all examples' repr strings.
        """
        return f"[{self.dirpath.name}]\n" + "\n".join(repr(example) for example in self.examples)

    def __str__(self) -> str:
        """
        More user-friendly string representation that shows the directory name and all examples' content.
        """
        return f"[{self.dirpath.name}]\n" + "\n".join(str(example) for example in self.examples)

    def __iter__(self):
        """
        Allow iteration over the internal list of Example objects.
        """
        return iter(self.examples)

    def show(self) -> None:
        """
        Print banners, the string representation, the repr representation,
        and each example's file path for demonstration purposes.
        """
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
    examples_a.show()

    # Now load the same structure back from the newly created directory
    # This time, each .py file will be recognized properly as a file, not a directory.
    examples_b = DemoDir.from_directory(examples_a.dirpath)
    examples_b.show()

    # Finally, delete the directory structure to clean up
    examples_b.delete()
