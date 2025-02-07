# demo_dir.py
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass
class Example:
    id_counter: ClassVar[int] = 0  # Class-level counter for IDs
    demo_dir_path: ClassVar[Path] = field(init=False)
    dir_path: Path
    input_text: str
    example_text: str = field(init=False)
    lines: list[str] = field(init=False)
    _filename: str = field(init=False)

    def __post_init__(self) -> None:
        self.input_text = self.input_text.strip()
        self.lines = self.input_text.splitlines()
        self._filename = self._extract_filename() or self._generate_filename()
        if not self.lines[0].startswith(f"# {self._filename}"):
            self.lines.insert(0, f"# {self._filename}")
        self.example_text = "\n".join(self.lines)

    def _extract_filename(self) -> str | None:
        match = re.match(r"^---\s*([\w/]+\.py)", self.lines[0])
        return match.group(1) if match else None

    @staticmethod
    def _generate_filename() -> str:
        Example.id_counter += 1
        return f"example_{Example.id_counter}.py"

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def file_path(self) -> Path:
        return self.dir_path / self.filename

    def write_to_disk(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(self.example_text + "\n", encoding="utf-8")

    def __repr__(self) -> str:
        relative_path = self.file_path.relative_to(self.demo_dir_path).parent.as_posix()
        # Avoid outputting '.' if the file is in the root directory
        if relative_path == ".":
            relative_path = ""
        return f"--- {relative_path}\n" + self.example_text


@dataclass
class DemoDir:
    input_text: str
    input_lines: list[str] = field(init=False)
    dirpath: Path = field(init=False)
    examples: list[Example] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.input_lines = self.input_text.strip().splitlines()
        self.dirpath = Path(self.input_lines[0].strip(' []'))
        Example.demo_dir_path = self.dirpath
        self._parse_examples()
        self._reset_example_dir()
        self._write_examples_to_disk()

    def _parse_examples(self) -> None:
        current_block = []
        file_path = None
        for line in self.input_lines[1:]:
            if line.startswith('---'):
                if current_block:
                    self.examples.append(Example(self.dirpath / (file_path or ''), input_text="\n".join(current_block)))
                    current_block = []
                file_path = line[3:].split('#')[0].strip()  # Extract file path and remove comments
            else:
                current_block.append(line)
        if current_block:
            self.examples.append(Example(self.dirpath / (file_path or ''), input_text="\n".join(current_block)))

    def _reset_example_dir(self) -> None:
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)
        self.dirpath.mkdir(parents=True)

    def _write_examples_to_disk(self) -> None:
        for e in self.examples:
            e.write_to_disk()

    @classmethod
    def from_file(cls, file_path: Path) -> "DemoDir":
        return cls(file_path.read_text(encoding="utf-8"))

    def delete(self) -> None:
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)

    def __repr__(self) -> str:
        return f"[{self.dirpath.name}]\n" + "\n".join(repr(e) for e in self.examples)

    def __iter__(self):
        return iter(self.examples)


# File names are auto-generated by `Example` class:
test_str = """
[demo_dir_name]
---              # Create in demo_dir_name
print('Valid')
print('Example')
--- foo          # Create in demo_dir_name/foo
print('Valid')
print('Example')
--- bar          # Create in demo_dir_name/bar
print('Valid')
print('Example')
--- bar/baz      # Create in demo_dir_name/baz
print('No slug line')
print('Example')
print('long enough')
--- baz/qux      # Create in demo_dir_name/baz/qux
print('For loop')
for i in range(5):
    print(f"{i = }")
--- baz/qux/zap  # Create in demo_dir_name/baz/qux/zap
print('While')
i = 0
while i < 5:
    i += 1
    print(f"{i = }")
"""

if __name__ == "__main__":
    examples = DemoDir(test_str)
    print(repr(examples))
    print("-" * 40)
    for example in examples:
        print(example.file_path)
    examples.delete()
