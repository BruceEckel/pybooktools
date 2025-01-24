# demo_dir.py
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, ClassVar


@dataclass
class Example:
    id_counter: ClassVar[int] = 0  # Class-level counter for IDs
    id: int = field(init=False)
    content: str = ""
    lines: list[str] = None
    _filename: str = None

    def __post_init__(self) -> None:
        self.id = Example.id_counter
        Example.id_counter += 1

        self.content = self.content.strip()
        self.lines = self.content.strip().splitlines()
        if not self.lines:
            return  # Empty content: create Example later
        if self._filename is None:
            first_line = self.lines[0].strip()
            if first_line.startswith("#"):
                self._filename = first_line[1:].strip()
            else:
                raise ValueError(f"Missing slugline in\n{self.content = }")

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


@dataclass
class DemoDirectory:
    demo_dir: str
    example_text: str
    demo_path: Path = field(init=False)
    examples: List[Example] = field(init=False)
    cleanup: bool = True

    def __post_init__(self) -> None:
        self.demo_path = Path(self.demo_dir)
        self.demo_path.mkdir(exist_ok=True)

        # Parse example_text into individual Example objects
        self.examples = []
        current_example = []
        filename_pattern = re.compile(r"^#\s*([\w_]+\.py)")

        for line in self.example_text.splitlines():
            match = filename_pattern.match(line)
            if match:
                # If there's an existing example, save it before starting a new one
                if current_example:
                    example = Example("\n".join(current_example))
                    if example.filename is not None:  # Ensure filename is valid
                        self.examples.append(example)
                    current_example = []
            current_example.append(line)

        # Add the last example if it exists
        if current_example:
            example = Example("\n".join(current_example))
            if example.filename is not None:  # Ensure filename is valid
                self.examples.append(example)

        # Write the files
        for example in self.examples:
            if example.filename:  # Ensure the filename is valid
                file_path = self.demo_path / example.filename
                file_path.write_text(example.content, encoding="utf-8")
            else:
                raise ValueError(f"Example is missing a valid filename: {example.content}")

    def __del__(self) -> None:
        if self.cleanup:
            if self.demo_path.exists():
                shutil.rmtree(self.demo_path)


if __name__ == "__main__":
    from icecream import ic

    ic.configureOutput(outputFunction=print)

    example_text = """
# example_filename1.py
print("Hello, world")

# example_filename2.py
print("More content")
print("More data")
print("More fun")
"""

    demo = DemoDirectory("demo_dir", example_text)
    ic(demo)
