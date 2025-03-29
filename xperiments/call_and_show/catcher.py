from dataclasses import dataclass
from typing import Any, Callable, TypeVar

R = TypeVar("R")


class Catcher:
    """A context manager that catches exceptions and prints their error messages,
    and can be used as a callable via its __call__ method."""

    def __enter__(self) -> "Catcher":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        # __exit__ is only called if an exception escapes the block.
        if exc_type is not None:
            print(f"Error: {exc_value}")
        return True

    def __call__(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        """Execute a function, catching and printing errors so that subsequent calls run."""
        try:
            result = func(*args, **kwargs)
            if result is not None:
                print(result)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return None  # type: ignore


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


if __name__ == "__main__":
    def mark(marker: int) -> None:
        print(f"[{marker}]:", end=" ")


    with Catcher() as catch:
        mark(1)
        catch(foo, 1, Fob(1))
        mark(2)
        catch(foo, 0, Fob(0))
        mark(3)
        catch(foo, -1, Fob(1))
        mark(4)
        catch(foo, 1, Fob(-1))
        mark(5)
        catch(foo, -1, Fob(-1))
        mark(6)
        catch(foo, 10, Fob(11))

    print("completed")
