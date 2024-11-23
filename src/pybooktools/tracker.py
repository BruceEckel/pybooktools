#: tracker.py
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union


@dataclass
class Output:
    actual: str = ""
    expected: str = ""

    def write(self, s: str) -> None:
        # For print(..., file='Output object')
        self.actual += s

    def compare(self):
        if self.actual != self.expected:
            print(f"actual: {self.actual} != expected: {self.expected}")
        else:
            print(f"{self.actual = }    {self.expected = }")

    def to_dict(self) -> dict:
        return {"actual": self.actual, "expected": self.expected}

    @classmethod
    def from_dict(cls, data: dict) -> "Output":
        return cls(actual=data["actual"], expected=data["expected"])


@dataclass
class Tracker:
    output_file_location: str
    outputs: list[Output] = field(default_factory=list)
    current: Output = field(default_factory=Output)

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.current)

    def expected(self, expected_output: str):
        # Call to expected() means compare all the current output
        # to the expected output and start a new Output object.
        if not expected_output.startswith(":"):
            return
        self.current.expected = expected_output[1:].strip()
        # Complete the current Output and start a new one:
        self.current.actual = self.current.actual.strip()
        self.outputs.append(self.current)
        self.current = Output()

    def compare(self):
        for output in self.outputs:
            output.compare()

    def create_json_file(self):
        # Containing Tracker data in human-readable JSON
        data = {
            "outputs": [output.to_dict() for output in self.outputs],
            "current": self.current.to_dict(),
        }
        Path(self.output_file_location).write_text(
            json.dumps(data, indent=4), encoding="utf-8"
        )

    @classmethod
    def from_file(
            cls, tracker_json_file_path: Path | str
    ) -> Union["Tracker", None]:
        if not tracker_json_file_path.exists():
            return None
        if isinstance(tracker_json_file_path, str):
            json_path = Path(tracker_json_file_path)
        else:
            json_path = tracker_json_file_path
        # Recreate a Tracker instance from a result file
        data = json.loads(json_path.read_text(encoding="utf-8"))
        outputs = [Output.from_dict(output) for output in data["outputs"]]
        current = Output.from_dict(data["current"])
        return cls(str(json_path), outputs, current)
