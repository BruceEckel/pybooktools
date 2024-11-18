#: tracer.py
from dataclasses import dataclass, field


@dataclass
class Tracer:
    outputs: list[str] = field(default_factory=list)

    def write(self, trace: str) -> None:
        if trace.strip():
            self.outputs.append(trace)
