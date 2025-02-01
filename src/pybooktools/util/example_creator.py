# example_creator.py
"""
[demo_dir_name]
---                # Create in demo_dir_name with auto-generated name
print('Valid')
print('Example')
--- foo            # Create in demo_dir_name as foo.py
print('Valid')
print('Example')
--- bar.py         # Create in demo_dir_name as bar.py
print('Valid')
print('Example')
---/baz1           # Create in subdirectory baz1
print('No slug line')
print('Example')
print('long enough')
---
for i in range(5):
    print(f"{i = }")
---
"""
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass
class Example:
    id_counter: ClassVar[int] = 0  # Class-level counter for IDs
    dir_path: Path
    input_text: str
    example_text: str = field(init=False)
    lines: list[str] = field(init=False)
    _filename: str = field(init=False)

    def __post_init__(self) -> None:
        self.input_text = self.input_text.strip()
        self.lines = self.input_text.splitlines()

        # Ensure the filename is extracted or generated
        self._filename = self._extract_filename() or self._generate_filename()

        # Ensure the example text includes the filename comment
        if not self.lines[0].startswith(f"# {self._filename}"):
            self.lines.insert(0, f"# {self._filename}")

        self.example_text = "\n".join(self.lines)

    def _extract_filename(self) -> str | None:
        """Extract filename from the first line if present."""
        match = re.match(r"^#\s*([\w_]+\.py)", self.lines[0].strip())
        return match.group(1) if match else None

    @staticmethod
    def _generate_filename() -> str:
        """Generate a filename if none is provided."""
        Example.id_counter += 1
        return f"example_{Example.id_counter}.py"

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def file_path(self) -> Path:
        return self.dir_path / self.filename

    def write_to_disk(self) -> None:
        """Write the example content to disk."""
        self.file_path.write_text(self.example_text + "\n", encoding="utf-8")

    def __repr__(self) -> str:
        return self.example_text


@dataclass
class CreateExamples:
    examples_dir: str
    examples_path: Path = field(init=False)
    examples: list[Example] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.examples_path = Path(self.examples_dir)
        self._reset_example_dir()
        self._write_examples_to_disk()

    def _reset_example_dir(self) -> None:
        """Reset the example directory, creating a fresh structure."""
        if self.examples_path.exists():
            shutil.rmtree(self.examples_path)
        self.examples_path.mkdir()

    def _write_examples_to_disk(self) -> None:
        """Write all examples to the example directory."""
        for e in self.examples:
            e.write_to_disk()

    @classmethod
    def from_text(cls, example_dir: str, text: str) -> "CreateExamples":
        """Create an instance from a block of text."""
        blocks = re.split(r"^---\s*$", text.strip(), flags=re.MULTILINE)
        return cls(examples_dir=example_dir,
                   examples=[
                       Example(Path(example_dir), input_text=block.strip())
                       for block in blocks if block.strip()
                   ])

    @classmethod
    def from_file(cls, example_dir: str, file_path: Path) -> "CreateExamples":
        """Create an instance by reading a text file."""
        return cls.from_text(example_dir, file_path.read_text(encoding="utf-8"))

    def delete(self) -> None:
        """Delete the example directory."""
        if self.examples_path.exists():
            shutil.rmtree(self.examples_path)

    def __repr__(self) -> str:
        return "\n---\n".join(repr(e) for e in self.examples)

    def __iter__(self):
        return iter(self.examples)


if __name__ == "__main__":
    examples = CreateExamples.from_file("example_dir", Path("examples.txt"))
    print(repr(examples))
    print("-" * 40)
    for example in examples:
        print(example.file_path)
    examples.delete()
