#: tracker.py
from dataclasses import dataclass, field


@dataclass
class Output:
    actual: str = ""
    expected: str = ""

    def write(self, s: str) -> None:
        self.actual += s

    def compare(self):
        if self.actual != self.expected:
            print(f"actual: {self.actual} != expected: {self.expected}")
        else:
            print(f"{self.actual = }   {self.expected = }")


@dataclass
class Tracker:
    outputs: list[Output] = field(default_factory=list)
    current: Output = field(default_factory=Output)

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.current)

    def expected(self, exp: str):
        # Call to expected means compare all the current output
        # to the expected output and start a new Output object.
        if not exp.startswith(":"):
            return
        self.current.expected = exp[1:].strip()
        # Complete the current Output and start a new one:
        self.current.actual = self.current.actual.strip()
        self.outputs.append(self.current)
        self.current = Output()

    def compare(self):
        for output in self.outputs:
            output.compare()
