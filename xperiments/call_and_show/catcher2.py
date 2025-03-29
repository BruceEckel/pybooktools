"""
A context manager that catches exceptions and prints their error messages,
and can be used as a callable via its __call__ method.

When used as a callable, argument evaluation must be delayed until inside
the context manager in case argument evaluation raises an exception.
To do this the function should be provided as a zero-argument callable.
If the function takes arguments, it must be wrapped in a lambda to delay evaluation.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

R = TypeVar("R")


class Catch:

    def __enter__(self) -> "Catch":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        # __exit__ is only called if an exception escapes the block.
        if exc_type is not None:
            print(f"Error: {exc_value}")
        return True

    def __call__(self, func: Callable[[], R]) -> R:
        """
        Execute a zero-argument callable, catching and
        printing errors so that subsequent calls run.
        """
        try:
            result = func()
            if result is not None:
                print(result)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


# Test code

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


if __name__ == "__main__":
    with Catch():  # Single-failure simple form
        mark(1)
        foo(1, Fob(-1))

    with Catch():  # Success does NOT automatically display the result
        mark(2)
        print(foo(42, Fob(42)))  # Must explicitly print
        # Or call print inside the function

    with Catch() as _:  # Lambda form does display the result
        mark(3)
        _(lambda: foo(42, Fob(42)))

    # Multi-failure lambda form:
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

"""
Here's where I am with this:
1. This will be applied to my own examples, so I can adjust them to fit my needs.
2. Most of the time, when I need this, I will know that a function fails and can just use the simple form.
3. I probably won't use the lambda form much, if at all, but if I need it, it's there. 
"""
