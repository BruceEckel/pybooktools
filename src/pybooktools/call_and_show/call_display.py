# call_display.py
"""
This module defines several functions (f1, f2, f3) and a decorator, display_call.
The decorator inspects the decorated function’s source code, extracts each call, executes it,
and prints the function call (as a string) along with either the result or the error message.
"""

import ast
import functools
import inspect
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class CallResult:
    """Stores the string representation of a call and its outcome (result or error)."""
    call: str
    result: Any = None
    error: str = ""


def display_call(func: Callable) -> Callable:
    """
    Decorator that intercepts each function call inside the decorated function.

    It parses the decorated function’s source code, then for each expression statement
    that is a call, it evaluates the call in a try/except block. The call and its result
    (or error message) are printed to the console.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        # Get the source code of the decorated function.
        source = inspect.getsource(func)
        # Parse the source code into an AST.
        tree = ast.parse(source)
        func_def = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                func_def = node
                break
        if func_def is None:
            # Fallback: call the function normally if no definition is found.
            return func(*args, **kwargs)

        # Iterate over each statement in the function definition.
        for stmt in func_def.body:
            # Use pattern matching (Python 3.10+) to handle expression statements that are calls.
            match stmt:
                case ast.Expr(value=ast.Call() as call_expr):
                    # Get a string representation of the call using ast.unparse (requires Python 3.9+)
                    call_str = ast.unparse(stmt.value)
                    try:
                        # Compile the expression (the function call) in eval mode.
                        expr_code = compile(ast.Expression(body=stmt.value), filename="<ast>", mode="eval")
                        # Evaluate the call in the globals of the original function.
                        result = eval(expr_code, func.__globals__, {})
                        call_result = CallResult(call=call_str, result=result)
                        print(f"{call_result.call} -> {call_result.result}")
                    except Exception as e:
                        call_result = CallResult(call=call_str, error=str(e))
                        print(f"{call_result.call} -> Error: {call_result.error}")
                case _:
                    # For other types of statements, execute them normally.
                    try:
                        module = ast.Module(body=[stmt], type_ignores=[])
                        code_obj = compile(module, filename="<ast>", mode="exec")
                        exec(code_obj, func.__globals__, {})
                    except Exception as e:
                        print(e)
        return None

    return wrapper


# The following functions and decorated function demonstrate display_call.
def f1(x: int) -> int:
    if x < 0:
        raise ValueError("x must be non-negative")
    return x + 1


def f2(x: int) -> int:
    if x < 10:
        raise ValueError("x must be at least 10")
    return x * 2


def f3(x: int) -> int:
    if x < 20:
        raise ValueError("x must be at least 20")
    return x * 3


@display_call
def _() -> None:
    f1(1)
    f1(-1)
    f2(10)
    f2(9)
    f3(20)
    f3(19)


if __name__ == "__main__":
    _()
