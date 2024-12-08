#: tracker.py
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel

from pybooktools.tracing import trace
from pybooktools.util import panic

console = Console()


@dataclass
class Output:
    id_number: int | None = None
    untouched_output: str = ""
    expected_output: str = ""
    actual_output: str = ""
    actual_output_written: bool = False

    def __post_init__(self):
        if self.id_number is None:
            return  # Uninitialized Output
        if self.untouched_output.startswith(f'"""{self.id_number}:'):
            start, self.expected_output = self.untouched_output.split(
                ":", maxsplit=1
            )
            self.expected_output = self.expected_output[:-3]
            assert int(start[3:]) == self.id_number
        elif self.untouched_output.startswith(f'"{self.id_number}:'):
            start, self.expected_output = self.untouched_output.split(
                ":", maxsplit=1
            )
            self.expected_output = self.expected_output[:-1]
            assert int(start[1:]) == self.id_number
        else:
            panic(f"No ':' in {self}")

    def write(self, s: str) -> None:
        # For print(..., file='Output object')
        self.actual_output += s
        self.actual_output_written = True

    def compare(self) -> bool:
        if not self.actual_output_written:
            panic(f"Actual output not written in {self}")
        if self.actual_output != self.expected_output:
            return False
        else:
            return True

    def to_dict(self) -> dict:
        return {
            "id_number": self.id_number,
            "untouched_output": self.untouched_output,
            "expected_output": self.expected_output,
            "actual_output": self.actual_output,
            "actual_output_written": self.actual_output_written,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Output":
        return cls(
            id_number=data["id_number"],
            untouched_output=data["untouched_output"],
            expected_output=data["expected_output"],
            actual_output=data["actual_output"],
            actual_output_written=data["actual_output_written"],
        )


@dataclass
class Tracker:
    outputs: list[Output] = field(default_factory=list)
    __current: Output = field(default_factory=Output)

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.__current)

    def expected(self, id_number: int, untouched_output: str):
        # Call to expected() means add the accumulated output
        # to the expected output and start a new Output object.
        trace(f"expected({id_number=}, {untouched_output=})")
        self.__current.id_number = id_number
        self.__current.untouched_output = untouched_output
        if ":" not in untouched_output:
            panic(f"expected() ':' not in {untouched_output=}")
        if not untouched_output.startswith(
            '"'
        ) or not untouched_output.endswith('"'):
            panic(
                "Untouched_output not contained in "
                f"double quotes: {untouched_output}"
            )
        if untouched_output.startswith(r'"""'):
            output_str = untouched_output[3:-3]
        else:
            output_str = untouched_output[1:-1]
        trace(f"{untouched_output = }, {output_str = }")
        self.__current.expected_output = output_str.split(":", maxsplit=1)[
            1
        ].strip()
        trace(f"{self.__current.expected_output = }")
        # Complete the __current Output and start a new one:
        self.__current.actual_output = self.__current.actual_output.strip()
        self.outputs.append(self.__current)
        self.__current = Output()

    def compare(self, file_name: str = ""):
        non_equivalent_outputs = [
            output for output in self.outputs if not output.compare()
        ]
        if non_equivalent_outputs:
            panels = []
            for output in non_equivalent_outputs:
                actual_panel = Panel(
                    output.actual_output,
                    title="Actual Output",
                    title_align="center",
                    border_style="bold green",
                )
                expected_panel = Panel(
                    output.expected_output,
                    title="Expected Output",
                    title_align="center",
                    border_style="bold blue",
                )
                panels.append(Columns([actual_panel, expected_panel]))
            mismatch_panel = Panel(
                Columns(panels),
                title=file_name if file_name else "Mismatch",
                title_align="left",
                border_style="bold red",
            )
            console.print(mismatch_panel)
        else:
            match_panel = Panel(
                "[bold green]Outputs Match[/bold green]",
                title="Comparison Result",
                title_align="center",
                border_style="green",
            )
            console.print(match_panel)

    def write_json_file(self, tracker_json_file: str) -> None:
        data = {
            "outputs": [output.to_dict() for output in self.outputs],
        }
        tracker_json_file_path = Path(tracker_json_file)
        if not tracker_json_file_path.parent.exists():
            panic(f"Directory not found: {tracker_json_file_path.parent}")
        tracker_json_file_path.write_text(
            json.dumps(data, indent=4), encoding="utf-8"
        )

    @classmethod
    def from_json_file(
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
