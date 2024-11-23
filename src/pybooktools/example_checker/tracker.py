#: tracker.py
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from pybooktools.util import panic


@dataclass
class Output:
    id_number: int
    untouched_output: str
    expected_output: str = ""
    actual_output: str = ""
    actual_output_written: bool = False

    def __post_init__(self):
        if self.untouched_output.startswith(f'"""{self.id_number}:'):
            start, self.expected_output = self.untouched_output.split(
                ":", maxsplit=1
            )
            self.expected_output = self.expected_output[:3]
            assert int(start[3:]) == self.id_number
        elif self.untouched_output.startswith(f'"{self.id_number}:'):
            start, self.expected_output = self.untouched_output.split(
                ":", maxsplit=1
            )
            self.expected_output = self.expected_output[:1]
            assert int(start[1:]) == self.id_number
        else:
            panic(f"No ':' in {self}")

    def write(self, s: str) -> None:
        # For print(..., file='Output object')
        self.actual_output += s
        self.actual_output_written = True

    def compare(self):
        if not self.actual_output_written:
            panic(f"Actual output not written in {self}")
        if self.actual_output != self.expected_output:
            print(
                f"actual: [{self.actual_output}] IS NOT expected: [{self.expected_output}]"
            )
        else:
            print(
                f"actual: [{self.actual_output}]     IS expected: [{self.expected_output}]"
            )

    def to_dict(self) -> dict:
        return {
            "expected_output": self.expected_output,
            "actual_output": self.actual_output,
            "actual_output_written": self.actual_output_written,
            "id_number": self.id_number,
            "untouched_output": self.untouched_output,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Output":
        return cls(
            expected_output=data["expected_output"],
            actual_output=data["actual_output"],
            actual_output_written=data["actual_output_written"],
            id_number=data["id_number"],
            untouched_output=data["untouched_output"],
        )


@dataclass
class Tracker:
    outputs: list[Output] = field(default_factory=list)
    __current: Output = field(default_factory=Output)

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.__current)

    def expected(self, expected_output: str):
        # Call to expected() means compare all the current output
        # to the expected output and start a new Output object.
        if not expected_output.startswith(":"):
            return
        self.__current.expected_output = expected_output[1:].strip()
        # Complete the current Output and start a new one:
        self.__current.actual_output = self.__current.actual_output.strip()
        self.outputs.append(self.__current)
        self.__current = Output()

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
            panic(f"Does not exist: {tracker_json_file_path}")
        # Recreate a Tracker instance from a result file
        data = json.loads(json_path.read_text(encoding="utf-8"))
        outputs = [Output.from_dict(output) for output in data["outputs"]]
        return cls(outputs)
