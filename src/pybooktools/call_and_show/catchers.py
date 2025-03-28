#!/usr/bin/env python3
"""
Utilities: perr, Catcher, and catch

`perr` is used as a function call.
`Catcher` is used as a context manager that provides a `.run()` method
    for capturing exceptions on a per‑call basis without exiting the block.
`catch` is used as a decorator that prints the return value before returning it.
"""
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

R = TypeVar("R")


def perr(func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """Call the function and print its result (unless None) or error."""
    try:
        result = func(*args, **kwargs)
        if result is not None:
            print(result)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None  # type: ignore


class Catcher:
    """A context manager that provides a .run() method to catch exceptions for each call
    without aborting the entire block."""

    def __enter__(self) -> "Catcher":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        # __exit__ is only invoked if an exception escapes the block.
        # Since we use run() to catch errors, this should rarely be hit.
        if exc_type is not None:
            print(f"Error: {exc_value}")
        return True

    def run(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """Execute a function, catching and printing errors so that subsequent calls run."""
        try:
            result = func(*args, **kwargs)
            if result is not None:
                print(result)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None


def catch(func: Callable[..., R]) -> Callable[..., R]:
    """A decorator that wraps the function call with a Catcher context manager,
    printing the return value (if not None) before returning it."""

    def wrapper(*args: Any, **kwargs: Any) -> R:
        result = None  # noqa
        with Catcher():
            result = func(*args, **kwargs)
        if result is not None:
            print(result)
        return result

    return wrapper


### Tests

@dataclass
class Fob:
    x: int

    def __post_init__(self) -> None:
        if self.x < 0:
            raise ValueError(f"{self.x = }, must be positive")


def foo(a: int, b: Fob) -> str:
    if a < 0:
        raise ValueError(f"{a = }, must be positive")
    return f"foo({a}, {b}) succeeded"


if __name__ == "__main__":
    def mark(marker: int) -> None:
        print(f"[{marker}]:", end=" ")


    mark(1)
    perr(foo, 1, Fob(1))
    mark(2)
    perr(foo, -1, Fob(1))
    # mark(3)
    # perr(foo, 1, Fob(-1))

    # Use Catcher run() method so errors don't abort the block:
    with Catcher() as _:
        mark(4)
        _.run(foo, 1, Fob(1))
        mark(5)
        _.run(foo, -1, Fob(1))
        mark(6)
        _.run(foo, 1, Fob(-1))


    @catch
    def decorated_foo(a: int, b: Fob) -> str:
        return foo(a, b)


    mark(7)
    decorated_foo(1, Fob(1))
    mark(8)
    decorated_foo(-1, Fob(1))
    # mark(9)
    # decorated_foo(1, Fob(-1))
    print("completed")
