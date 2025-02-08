# demo_dir.py
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


def banner(msg: str) -> None:
    print(f" {msg} ".center(60, '-'))


@dataclass
class Example:
    id_counter: ClassVar[int] = 0
    demo_dir_path: ClassVar[Path] = field(init=False)
    dir_path: Path
    input_text: str
    example_text: str = field(init=False)
    lines: list[str] = field(init=False)
    _filename: str = field(init=False)
    _relative_path: str = field(init=False)

    def __post_init__(self) -> None:
        self.input_text = self.input_text.strip()
        self.lines = self.input_text.splitlines()
        self._filename = self._extract_filename() or self._generate_filename()
        self._ensure_slug_line()
        self.example_text = "\n".join(self.lines)
        self._relative_path = self.dir_path.resolve().relative_to(self.demo_dir_path.resolve()).as_posix()

    def _ensure_slug_line(self) -> None:
        slugline_pattern = re.compile(r"^#\s*([\w/]+\.py)")
        if self.lines and slugline_pattern.match(self.lines[0]):
            self.lines[0] = f"# {self._filename}"
        else:
            self.lines.insert(0, f"# {self._filename}")

    @classmethod
    def reset_counter(cls) -> None:
        cls.id_counter = 0

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
        slugline = f"# {self.filename}"
        content_without_slug = self.example_text.removeprefix(slugline).lstrip()
        return f"--- {self._relative_path}\n{content_without_slug}"

    def __str__(self) -> str:
        return f"{self.file_path.as_posix()}:\n{self.example_text}"


@dataclass
class DemoDir:
    input_text: str
    input_lines: list[str] = field(init=False)
    dirpath: Path = field(init=False)
    examples: list[Example] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.input_lines = self.input_text.strip().splitlines()
        self.dirpath = Path(self.input_lines.pop(0).strip(' []')).resolve()
        Example.demo_dir_path = self.dirpath
        self._parse_examples()
        self._prepare_directory()
        self._write_examples_to_disk()

    def _parse_examples(self) -> None:
        Example.reset_counter()
        current_block, file_path = [], None

        for line in self.input_lines:
            if line.startswith('---'):
                if current_block:
                    self.examples.append(Example(self.dirpath / (file_path or ''), input_text="\n".join(current_block)))
                    current_block.clear()
                file_path = line[3:].split('#')[0].strip()
            else:
                current_block.append(line)

        if current_block:
            self.examples.append(Example(self.dirpath / (file_path or ''), input_text="\n".join(current_block)))

    def _prepare_directory(self) -> None:
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)
        self.dirpath.mkdir(parents=True)

    def _write_examples_to_disk(self) -> None:
        for example in self.examples:
            example.write_to_disk()

    @classmethod
    def from_file(cls, file_path: Path) -> "DemoDir":
        return cls(file_path.read_text(encoding="utf-8"))

    @classmethod
    def from_directory(cls, directory: Path) -> "DemoDir":
        Example.reset_counter()
        examples = [
            Example(
                dir_path=file.parent.resolve(),
                input_text=file.read_text(encoding="utf-8").strip()
            )
            for file in directory.rglob("*.py")
        ]
        demo_dir = cls(input_text=f"[{directory.name}]")
        demo_dir.examples = examples
        return demo_dir

    def delete(self) -> None:
        if self.dirpath.exists():
            shutil.rmtree(self.dirpath)

    def __repr__(self) -> str:
        return f"[{self.dirpath.name}]\n" + "\n".join(repr(example) for example in self.examples)

    def __str__(self) -> str:
        return f"[{self.dirpath.name}]\n" + "\n".join(str(example) for example in self.examples)

    def __iter__(self):
        return iter(self.examples)

    def show(self) -> None:
        banner(self.dirpath.name)
        banner("str")
        print(self)
        banner("repr")
        print(repr(self))
        banner("Paths")
        for example in self:
            print(example.file_path)
        # banner("Examples")
        # for example in self:
        #     print(example)


# File names are auto-generated by `Example` class:
test_str = """
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
--- bar/baz      # Create in demo_dir_name/baz
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
"""

if __name__ == "__main__":
    examples_a = DemoDir(test_str)
    examples_a.show()
    examples = DemoDir.from_directory(examples_a.dirpath)
    examples.show()
    examples.delete()
