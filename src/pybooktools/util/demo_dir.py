# demo_dir.py
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Example:
    content: str
    filename: str = None

    def __post_init__(self) -> None:
        if self.filename is None:
            lines = self.content.strip().splitlines()
            if lines:
                first_line = lines[0].strip()
                if first_line.startswith("#"):
                    self.filename = first_line[1:].strip()
                else:
                    raise ValueError(f"Missing slugline in\n{content = }")
            else:
                raise ValueError("Empty example content")


@dataclass
class DemoDirectory:
    demo_dir: str
    examples: List[Example]

    def __post_init__(self) -> None:
        demo_path = Path(self.demo_dir)
        demo_path.mkdir(exist_ok=True)

        for example in self.examples:
            file_path = demo_path / example.filename
            file_path.write_text(example.content, encoding="utf-8")


example1 = Example("""
# example_filename1.py
print("Hello, world")
""")
print(example1)
