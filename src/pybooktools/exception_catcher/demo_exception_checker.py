# demo_exception_checker.py
from dataclasses import dataclass

from exception_catcher import Catch


@dataclass
class Fob:
    x: int

    def __post_init__(self) -> None:
        if self.x < 0:
            raise ValueError(f"Fob arg: {self.x} must be positive")


def foo(a: int, b: Fob) -> str:
    if a < 0:
        raise ValueError(f"foo arg {a} must be positive")
    return f"foo({a}, {b}) succeeded"


def mark(marker) -> None:
    print(f"[{marker}]:", end=" ")


mark(1)
print(foo(0, Fob(0)))

mark(2)
with Catch():  # Single-failure simple form
    foo(1, Fob(-1))

mark(3)
with Catch():  # Success does NOT automatically display the result
    print(foo(42, Fob(42)))  # Must explicitly print
    # Or call print inside the function

# If you know it succeeds you can just run it without a context:
mark(4)
print(foo(42, Fob(42)))

mark(5)
with Catch() as _:  # Lambda form displays successful result
    _(lambda: foo(42, Fob(42)))

# Multi-failure block requires lambda form:
with Catch() as _:
    mark("A")
    _(lambda: foo(1, Fob(1)))
    mark("B")
    _(lambda: foo(0, Fob(0)))
    mark("C")
    _(lambda: foo(-1, Fob(1)))
    mark("D")
    _(lambda: foo(1, Fob(-1)))
    mark("E")
    _(lambda: foo(-1, Fob(-1)))
    mark("F")
    _(lambda: foo(10, Fob(11)))

print("completed")
