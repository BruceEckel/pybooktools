#: tracker.py
from dataclasses import dataclass, field


@dataclass
class Output:
    actual: str = ""
    expected: str = ""

    def write(self, s: str) -> None:
        self.actual += s


@dataclass
class Tracker:
    outputs: list[Output] = field(default_factory=list)
    current: Output = Output()

    def print(self, *args, **kwargs):
        print(*args, **kwargs, self.current)

    def expected(self, exp: str):
        if not exp.startswith(':'):
            return
        self.current.expected = exp
        self.outputs.append(self.current)
        self.current = Output()
