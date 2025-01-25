# create_demo_examples.py
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, ClassVar


@dataclass
class Example:
    id_counter: ClassVar[int] = 0  # Class-level counter for IDs
    input_text: str = ""
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

    @filename.setter
    def filename(self, value: str) -> None:
        if " " in value:
            raise ValueError("Filename cannot contain spaces.")
        if not value.endswith(".py"):
            raise ValueError("Filename must end with '.py'.")
        self._filename = value

    def write_to_disk(self, directory: Path) -> None:
        if not self.filename:
            raise ValueError("Filename is not set.")
        file_path = directory / self.filename
        file_path.write_text(self.example_text + "\n", encoding="utf-8")

    def __repr__(self) -> str:
        return self.example_text


@dataclass
class DemoExamples:
    demo_dir: str
    demo_path: Path = field(init=False)
    examples: List[Example] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.demo_path = Path(self.demo_dir)
        if self.demo_path.exists():
            shutil.rmtree(self.demo_path)
        self.demo_path.mkdir(exist_ok=True)

        for example in self.examples:
            example.write_to_disk(self.demo_path)

    @classmethod
    def from_text(cls, demo_dir: str, text: str) -> "DemoExamples":
        """Create a DemoExamples instance from a block of text."""
        blocks = re.split(r"^---\s*$", text.strip(), flags=re.MULTILINE)
        examples = [Example(input_text=block.strip()) for block in blocks if block.strip()]
        instance = cls(demo_dir=demo_dir, examples=examples)
        return instance

    @classmethod
    def from_file(cls, demo_dir: str, file_path: str) -> "DemoExamples":
        """Create a DemoExamples instance by reading a text file."""
        file_content = Path(file_path).read_text(encoding="utf-8")
        return cls.from_text(demo_dir, file_content)

    def delete(self) -> None:
        if self.demo_path.exists():
            shutil.rmtree(self.demo_path)

    def __repr__(self) -> str:
        return "\n---\n".join(repr(example) for example in self.examples)

    def __iter__(self):
        return iter(self.examples)


if __name__ == "__main__":
    demos = DemoExamples.from_file("demo_dir", "example_text.txt")
    print(repr(demos))
    print("-" * 40)
    for demo in demos:
        print(demo.filename)
    demos.delete()
