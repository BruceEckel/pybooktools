# use_case.py
from dataclasses import dataclass
from typing import Any


@dataclass
class UseCase:
    case_id: int
    script: str
    expected_output: Any

    def __post_init__(self):
        # self.script = self.script.strip() + "\n"
        self.expected_output = str(self.expected_output).strip() + "\n"

    def __iter__(self):
        return iter((self.case_id, self.script, self.expected_output))
