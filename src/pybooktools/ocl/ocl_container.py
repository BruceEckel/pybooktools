import json
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Any, Optional

from icecream import ic


def serialize_arg(arg: Any) -> Any:
    """Custom serializer to handle non-JSON-serializable objects."""
    if isinstance(arg, (set, tuple, type, range, type(lambda: None))):
        return repr(arg)
    elif hasattr(arg, "__iter__") and not isinstance(arg, (str, bytes)):
        return list(arg)
    return arg


def deserialize_arg(arg: Any) -> Any:
    """Custom deserializer to restore specific types from their serialized forms."""
    if isinstance(arg, str):
        # Handle <class ...> specifically
        if arg.startswith("<class ") and arg.endswith(">"):
            return arg  # Leave the string as-is
        try:
            # Attempt to eval for types like tuple, set, etc., that were serialized with repr
            return eval(arg) if any(c in arg for c in "{},()") else arg
        except (SyntaxError, NameError):
            return arg
    return arg


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

    def to_dict(self) -> dict:
        return {
            "ident": self.ident,
            "arg": serialize_arg(self.arg),
            "result": self.result,
            "output_lines": self.output_lines,
            "output": self.output,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OCL":
        return cls(
            ident=data["ident"],
            arg=deserialize_arg(data["arg"]),
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
        ic(ocls)
        return cls(output_json=json_ocl_container, ocls=ocls)
