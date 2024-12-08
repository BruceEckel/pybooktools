import json
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Any, Optional, Generator

from icecream import ic

from pybooktools.util import error


def serialize_arg(arg: Any) -> Any:
    """Custom serializer to handle non-JSON-serializable objects using pattern matching."""
    match arg:
        case set():
            return {
                "__set__": list(arg)
            }  # Convert sets to a JSON-compatible format
        case tuple() | range():
            return repr(arg)  # Use repr for non-standard types
        case _ if isinstance(arg, (type(lambda: None), type)):
            return repr(arg)  # Use repr for lambdas and types
        case dict():
            return {  # Handle nested serialization
                str(k): serialize_arg(v) for k, v in arg.items()
            }
        case _ if hasattr(arg, "__iter__") and not isinstance(
                arg, (str, bytes)
        ):
            return [item for item in arg]  # Convert generators to lists
        case _:
            return arg


def deserialize_arg(arg: Any) -> Any:
    """Custom deserializer to restore specific types from their serialized forms."""
    if isinstance(arg, dict) and "__set__" in arg:
        return set(arg["__set__"])  # Restore sets from JSON-compatible format
    if isinstance(arg, str):
        # Handle <class ...> specifically
        if arg.startswith("<class ") and arg.endswith(">"):
            try:
                # Extract the class name and resolve it
                class_name = arg[8:-2]  # Remove <class '...'>' brackets
                module_name, class_name = class_name.rsplit(".", 1)
                module = __import__(module_name)
                return getattr(module, class_name)
            except (ImportError, AttributeError, ValueError):
                return arg  # Fallback to the string if class resolution fails
        try:
            # Attempt to eval for types like tuple, set, etc., that were serialized with repr
            return eval(arg) if any(c in arg for c in "{},()") else arg
        except (SyntaxError, NameError):
            return arg
    elif isinstance(arg, list):
        return set(arg) if all(isinstance(item, str) for item in arg) else arg
    elif isinstance(arg, dict):
        return {
            int(k) if k.isdigit() else k: deserialize_arg(v)
            for k, v in arg.items()
        }  # Restore numeric keys
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
        if isinstance(arg, Generator):
            error("Generator expressions are not allowed as arguments.")
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
