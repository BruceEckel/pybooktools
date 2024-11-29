import json
import traceback
from dataclasses import dataclass
from typing import Callable

from rich.console import Console
from rich.pretty import Pretty

console = Console()


@dataclass
class Trace:
    on: bool = False

    def __call__(self, *args):
        if not self.on:
            return
        for arg in args:
            match arg:
                case Callable():
                    try:
                        console.print(
                            "[bold yellow]Executing function:[/bold yellow]",
                            Pretty(arg),
                        )
                        result = arg()
                        console.print(
                            "[bold green]Function result:[/bold green]",
                            Pretty(result),
                        )
                    except Exception as e:
                        console.print(
                            "[bold red]Exception while executing function:[/bold red]",
                            Pretty(e),
                        )
                        console.print(traceback.format_exc())
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


trace = Trace()
