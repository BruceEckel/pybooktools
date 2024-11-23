#: tracker.py
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union


@dataclass
class Output:
    original_numbered_string: str = ""
    expected_output: str = ""
    actual_output: str = ""

    def write(self, s: str) -> None:
        # For print(..., file='Output object')
        self.actual_output += s

    def compare(self):
        if self.actual_output != self.expected_output:
            print(
                f"actual: {self.actual_output} != expected: {self.expected_output}"
            )
        else:
            print(f"{self.actual_output = }    {self.expected_output = }")

    def to_dict(self) -> dict:
        return {"actual": self.actual_output, "expected": self.expected_output}

    @classmethod
    def from_dict(cls, data: dict) -> "Output":
        return cls(
            actual_output=data["actual"], expected_output=data["expected"]
        )


@dataclass
class Tracker:
    outputs: list[Output] = field(default_factory=list)
    current: Output = field(default_factory=Output)

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.current)

    def expected(self, expected_output: str):
        # Call to expected() means compare all the current output
        # to the expected output and start a new Output object.
        if not expected_output.startswith(":"):
            return
        self.current.expected_output = expected_output[1:].strip()
        # Complete the current Output and start a new one:
        self.current.actual_output = self.current.actual_output.strip()
        self.outputs.append(self.current)
        self.current = Output()

    def compare(self):
        for output in self.outputs:
            output.compare()

    def convert_to_json(self) -> str:
        # Containing Tracker data in human-readable JSON
        data = {
            "outputs": [output.to_dict() for output in self.outputs],
        }
        return json.dumps(data, indent=4)

    @classmethod
    def from_file(
            cls, tracker_json_file_path: Path | str
    ) -> Union["Tracker", None]:
        if isinstance(tracker_json_file_path, str):
            json_path = Path(tracker_json_file_path)
        else:
            json_path = tracker_json_file_path
        if not json_path.exists():
            return None
        # Recreate a Tracker instance from a result file
        data = json.loads(json_path.read_text(encoding="utf-8"))
        outputs = [Output.from_dict(output) for output in data["outputs"]]
        return cls(outputs)
