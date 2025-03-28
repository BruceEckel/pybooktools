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

from typing import Any, Callable, Optional, TypeVar, overload, Union

R = TypeVar("R")


class _Catch:
    @overload
    def __call__(self) -> "_Catch":
        ...

    @overload
    def __call__(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
        ...

    def __call__(self, func: Optional[Callable[..., R]] = None, *args: Any, **kwargs: Any) -> Union[R, "_Catch"]:
        if func is None:
            # No function provided: assume context manager usage.
            return self
        else:
            # Function call mode.
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    print(result)
                return result
            except Exception as e:
                print(f"Error: {e}")
                return None

    def __enter__(self) -> "_Catch":
        # Enter context manager mode.
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        # If an exception occurs in the with-block, print its error message.
        if exc_type is not None:
            print(f"Error: {exc_value}")
        # Suppress the exception.
        return True


def foo(a: int, b: str, c: float) -> str:
    print(f"foo(a={a}, b='{b}', c={c})")
    if a < 0:
        raise ValueError("a must be positive")
    return f"{a} {b} {c}"


def x(u: int) -> None:
    if u < 0:
        raise ValueError("u must be positive")
    print(f"x(u={u})")


# Create a single instance that is both callable and a context manager.
catch = _Catch()

if __name__ == "__main__":
    print("Function call mode")
    catch(foo, 1, "bar", 3.14)
    catch(foo, -1, "bar", 3.14)
    catch(foo, -20, "bar", 3.14)
    catch(x, -1)
    catch(x, 1)

    print("Context manager mode")
    with catch():
        catch(foo, 1, "bar", 3.14)
        catch(foo, -1, "bar", 3.14)
        catch(foo, -20, "bar", 3.14)
        catch(x, -1)
        catch(x, 1)
