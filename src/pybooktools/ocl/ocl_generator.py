import json
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Any, Optional

from icecream import ic


@dataclass
class OCL:
    ident: str
    arg: Any
    result: list[str] = field(default_factory=list)
    output_lines: list[str] = field(default_factory=list)
    output: Optional[str] = None

    def __post_init__(self):
        self.result = pformat(self.arg, width=47).splitlines()
        ic(self.result)
        self.output_lines = [
            "#| " + subline
            for line in self.result
            for subline in line.split("\n")
            if subline.strip()
        ]
        ic(self.output_lines)
        self.output = "\n".join(self.output_lines)
        ic(self.output)

    def to_dict(self) -> dict:
        return {
            "ident": self.ident,
            "arg": self.arg,
            "result": self.result,
            "output_lines": self.output_lines,
            "output": self.output,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OCL":
        return cls(
            ident=data["ident"],
            arg=data["arg"],
            result=data.get("result", []),
            output_lines=data.get("output_lines", []),
            output=data.get("output"),
        )


@dataclass
class OCLContainer:
    output_json: Path
    ocls: list[OCL] = field(default_factory=list)

    def __call__(self, ident: str, arg: Any) -> None:
        self.ocls.append(OCL(ident, arg))

    def write(self) -> None:
        data = [ocl.to_dict() for ocl in self.ocls]
        self.output_json.write_text(
            json.dumps(data, indent=4), encoding="utf-8"
        )

    @classmethod
    def read(cls, json_ocl_container: Path) -> "OCLContainer":
        data = json.loads(json_ocl_container.read_text(encoding="utf-8"))
        ocls = [OCL.from_dict(item) for item in data]
        return cls(output_json=json_ocl_container, ocls=ocls)