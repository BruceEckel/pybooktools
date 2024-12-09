import pickle
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Any, Optional


def ic(*args: Any) -> None:
    pass
    # icecream.ic(*args)


@dataclass
class OCL:
    ident: str
    arg: Any
    raw_print: str
    formatted_arg: Optional[str] = None
    result: list[str] = field(default_factory=list)
    output_lines: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.formatted_arg = pformat(self.arg, width=47)

        match self.arg:
            case str():  # An f-string arg is evaluated before it is passed
                self.result = [
                    line for line in self.arg.splitlines() if line.strip()
                ]
            case _:
                for line in self.formatted_arg.splitlines():
                    parts = line.split("\\n")
                    for part in parts:
                        stripped = part.strip()
                        if stripped:
                            self.result.append(stripped)

        ic(self.result)
        self.output_lines = [
            "#| " + line for line in self.result if line.strip()
        ]
        ic(self.output_lines)


@dataclass
class OCLContainer:
    ocls: list[OCL] = field(default_factory=list)

    def __call__(self, ident: str, arg: Any, raw_print: str) -> None:
        self.ocls.append(OCL(ident, arg, raw_print))

    def write(self, pickle_file: Path) -> None:
        pickle_file.write_bytes(pickle.dumps(self))

    @classmethod
    def read(cls, pickle_file: Path) -> "OCLContainer":
        container = pickle.loads(pickle_file.read_bytes())
        ic(container)
        return container
