# example_creator.py
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, ClassVar


@dataclass
class Example:
    id_counter: ClassVar[int] = 0  # Class-level counter for IDs
    dir_path: Path
    input_text: str
    example_text: str = ""
    lines: list[str] = field(init=False)
    _filename: str | None = None

    def __post_init__(self) -> None:
        self.input_text = self.input_text.strip()
        self.lines = self.input_text.splitlines()
        # Ensure example_text includes the filename comment:
        filename_pattern = re.compile(r"^#\s*([\w_]+\.py)")
        match = filename_pattern.match(self.lines[0].strip())
        if match:
            self._filename = match.group(1)
        else:
            Example.id_counter += 1
            self._filename = f"example_{Example.id_counter}.py"
            self.lines.insert(0, f"# {self._filename}")

        self.example_text = "\n".join(self.lines)

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def file_path(self):
        return self.dir_path / self.filename

    def write_to_disk(self) -> None:
        if not self.filename:
            raise ValueError("Filename is not set.")
        file_path = self.dir_path / self.filename
        file_path.write_text(self.example_text + "\n", encoding="utf-8")

    def __repr__(self) -> str:
        return self.example_text


@dataclass
class CreateExamples:
    example_dir: str
    example_path: Path = field(init=False)
    examples: List[Example] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.example_path = Path(self.example_dir)
        if self.example_path.exists():
            shutil.rmtree(self.example_path)
        self.example_path.mkdir(exist_ok=True)

        for exmpl in self.examples:
            exmpl.write_to_disk()

    @classmethod
    def from_text(cls, example_dir: str, text: str) -> "CreateExamples":
        """Create a exampleExamples instance from a block of text."""
        example_path = Path(example_dir)
        blocks = re.split(r"^---\s*$", text.strip(), flags=re.MULTILINE)
        return cls(example_dir=example_dir,
                   examples=[Example(example_path, input_text=block.strip()) for block in blocks if block.strip()])

    @classmethod
    def from_file(cls, example_dir: str, file_path: str) -> "CreateExamples":
        """Create a exampleExamples instance by reading a text file."""
        file_content = Path(file_path).read_text(encoding="utf-8")
        return cls.from_text(example_dir, file_content)

    def delete(self) -> None:
        if self.example_path.exists():
            shutil.rmtree(self.example_path)

    def __repr__(self) -> str:
        return "\n---\n".join(repr(ex) for ex in self.examples)

    def __iter__(self):
        return iter(self.examples)


if __name__ == "__main__":
    examples = CreateExamples.from_file("example_dir", "examples.txt")
    print(repr(examples))
    print("-" * 40)
    for example in examples:
        print(example.file_path)
    examples.delete()
