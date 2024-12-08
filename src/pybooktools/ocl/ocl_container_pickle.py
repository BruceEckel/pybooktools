import pickle
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Any, Optional, Generator

from icecream import ic

from pybooktools.util import error


@dataclass
class OCL:
    ident: str
    arg: Any
    result: list[str] = field(default_factory=list)
    output_lines: list[str] = field(default_factory=list)
    output: Optional[str] = None

    def __post_init__(self):
        # Use pformat for formatted output with line width
        formatted_arg = pformat(self.arg, width=47)

        # For string arguments, handle multiline strings gracefully
        if isinstance(self.arg, str):
            lines = [line for line in self.arg.splitlines() if line.strip()]
        else:
            # Split into lines, handling escaped newlines properly
            lines = []
            for line in formatted_arg.splitlines():
                parts = line.split("\\n")
                for part in parts:
                    stripped = part.strip()
                    if stripped:
                        lines.append(stripped)

        self.result = lines
        ic(self.result)
        self.output_lines = ["#| " + line for line in lines if line.strip()]
        ic(self.output_lines)
        self.output = "\n".join(self.output_lines)
        ic(self.output)


@dataclass
class OCLContainer:
    output_pickle: Path
    ocls: list[OCL] = field(default_factory=list)

    def __call__(self, ident: str, arg: Any) -> None:
        if isinstance(arg, Generator):
            error("Generator expressions are not allowed as arguments.")
        self.ocls.append(OCL(ident, arg))

    def write(self) -> None:
        with self.output_pickle.open("wb") as file:
            pickle.dump(
                self, file
            )  # file already satisfies SupportsWrite[bytes]

    @classmethod
    def read(cls, pickle_file: Path) -> "OCLContainer":
        with pickle_file.open("rb") as file:
            container = pickle.load(
                file
            )  # file already satisfies SupportsWrite[bytes]
        ic(container)
        return container
