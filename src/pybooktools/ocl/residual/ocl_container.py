import json
from pathlib import Path
from pprint import pformat
from typing import Any, Generator, Optional

from icecream import ic
from pydantic import BaseModel, ValidationError, model_validator

from pybooktools.util import error


class OCL(BaseModel):
    ident: str
    arg: Any
    result: list[str] = []
    output_lines: list[str] = []
    output: Optional[str] = None

    @model_validator(mode="before")
    def compute_fields(cls, values):
        arg = values.get("arg")
        formatted_arg = pformat(arg, width=47)

        if isinstance(arg, str):
            lines = [line for line in arg.splitlines() if line.strip()]
        else:
            lines = []
            for line in formatted_arg.splitlines():
                parts = line.split("\\n")
                for part in parts:
                    stripped = part.strip()
                    if stripped:
                        lines.append(stripped)

        output_lines = ["#| " + line for line in lines if line.strip()]
        output = "\n".join(output_lines)

        values["result"] = lines
        values["output_lines"] = output_lines
        values["output"] = output
        return values

    class Config:
        arbitrary_types_allowed = True  # Allow non-standard types


class OCLContainer(BaseModel):
    output_json: Path
    ocls: list[OCL] = []

    def __call__(self, ident: str, arg: Any) -> None:
        if isinstance(arg, Generator):
            error("Generator expressions are not allowed as arguments.")
        try:
            self.ocls.append(OCL(ident=ident, arg=arg))
        except ValidationError as e:
            error(f"Validation error: {e}")

    def write(self) -> None:
        data = [ocl.dict() for ocl in self.ocls]
        self.output_json.write_text(
            json.dumps(data, indent=4), encoding="utf-8"
        )

    @classmethod
    def read(cls, json_ocl_container: Path) -> "OCLContainer":
        data = json.loads(json_ocl_container.read_text(encoding="utf-8"))
        ocls = [OCL(**item) for item in data]
        ic(ocls)
        return cls(output_json=json_ocl_container, ocls=ocls)
