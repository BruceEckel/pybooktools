# tracer.py
"""
Use Icecream instead?
"""
import json
import traceback
from dataclasses import dataclass
from typing import Any

from rich.pretty import Pretty

from pybooktools.util.console import console


@dataclass
class Trace:
    __tracing: bool = False

    def __bool__(self) -> bool:
        return bool(self.__tracing)

    def __call__(self, *args: Any) -> None:
        if not self.__tracing:
            return
        for arg in args:
            match arg:
                case list() | tuple() | set():
                    console.print(Pretty(arg))
                case dict():
                    console.print(Pretty(arg))
                case int() | float():
                    console.print(f"[bold cyan]{arg}[/bold cyan]")
                case bool():
                    console.print(
                        f"[bold green]{arg}[/bold green]"
                        if arg
                        else f"[bold red]{arg}[/bold red]"
                    )
                case Exception():
                    console.print(
                        "[bold red]Exception:[/bold red]", Pretty(arg)
                    )
                    console.print(traceback.format_exc())
                case str():
                    # Check if it's a JSON string
                    try:
                        parsed_json = json.loads(arg)
                        console.print(Pretty(parsed_json))
                    except (json.JSONDecodeError, TypeError):
                        console.print(arg)
                case _:
                    # Fallback for strings and other objects
                    if hasattr(arg, "__dataclass_fields__") or hasattr(
                        arg, "__dict__"
                    ):
                        console.print(Pretty(arg))
                    else:
                        console.print(arg)

    def enable(self) -> None:
        console.print(f"[red]trace enabled[/red]")
        self.__tracing = True

    def disable(self) -> None:
        console.print(f"[red]trace disabled[/red]")
        self.__tracing = False


trace = Trace()
