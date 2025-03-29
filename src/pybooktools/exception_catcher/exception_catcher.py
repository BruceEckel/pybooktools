# book_utils/exception_catcher.py
"""
Context manager that catches exceptions and prints their error messages,
and can be used as a callable via its __call__ method.

When used as a callable, argument evaluation must be delayed until inside
the context manager in case argument evaluation raises an exception.
To do this the function should be provided as a zero-argument callable.
If the function takes arguments, it must be wrapped in a lambda to delay evaluation.
"""

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
