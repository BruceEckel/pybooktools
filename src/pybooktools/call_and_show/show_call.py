# show_call.py
"""
Utility: catch

This utility can be used both as a context manager and as a function call.

Usage as a context manager:
    with catch():
        foo(1, "bar", 3.14)
Any exception raised inside the with‑block is caught and its error message printed.

Usage as a function call:
    catch(foo, 1, "bar", 3.14)
This calls foo(1, "bar", 3.14) and prints its result (unless the result is None)
or, if an exception is raised, prints the error message.
"""

from contextlib import ContextDecorator
from typing import Any


class _Show(ContextDecorator):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if args:
            # Function call mode: the first argument must be callable.
            func = args[0]
            if not callable(func):
                raise TypeError("First argument must be callable")
            try:
                result = func(*args[1:], **kwargs)
                if result is not None:
                    print(result)
                return result
            except Exception as e:
                print(f"Error: {e}")
        else:
            # No arguments: assume context manager usage.
            return self

    def __enter__(self) -> "_Catch":
        # Entering context manager mode.
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        # If an exception occurred in the block, print its message.
        if exc_type is not None:
            print(f"Error: {exc_value}")
        # Suppress the exception so it does not propagate.
        return True


def foo(a: int, b: str, c: float) -> str:
    print(f"foo(a={a}, b='{b}', c={c})")
    if a < 0:
        raise ValueError("a must be positive")
    return f"{a} {b} {c}"


if __name__ == "__main__":
    # Create a single instance that is both callable and a context manager.
    show = _Show()
    print("Function call mode")
    show(foo, 1, "bar", 3.14)
    show(foo, -1, "bar", 3.14)
    show(foo, -10, "bar", 3.14)
    show(foo, -20, "bar", 3.14)

    print("Context manager mode")
    with show():
        foo(1, "bar", 3.14)
        foo(-1, "bar", 3.14)
        foo(-10, "bar", 3.14)
        foo(-20, "bar", 3.14)
