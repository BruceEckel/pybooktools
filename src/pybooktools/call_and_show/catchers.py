#!/usr/bin/env python3
"""
Utilities: perr, Catcher, and catch

`perr` is used as a function call.
`Catcher` is used as a context manager that provides a `.run()` method
    for capturing exceptions on a per‑call basis without exiting the block.
`catch` is used as a decorator that prints the return value before returning it.
"""

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


def foo(a: int, b: str, c: float) -> str:
    if a < 0:
        raise ValueError(f"{a = }, must be positive")
    return f"foo({a}, {b}, {c}) succeeded"


if __name__ == "__main__":
    def mark(n: int) -> None:
        print(f"[{n}]:", end=" ")


    mark(1)
    perr(foo, 1, "bar", 3.14)
    mark(2)
    perr(foo, -1, "bar", 3.14)

    # Using Catcher as a context manager with its .run() method so errors don't abort the block:
    with Catcher() as catcher:
        mark(3)
        catcher.run(foo, 1, "bar", 3.14)
        mark(4)
        catcher.run(foo, -1, "bar", 3.14)


    @catch
    def decorated_foo(a: int, b: str, c: float) -> str:
        return foo(a, b, c)


    mark(5)
    decorated_foo(1, "bar", 3.14)
    mark(6)
    decorated_foo(-1, "bar", 3.14)
    print("completed")
