import json
import traceback
from dataclasses import dataclass

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
            if (
                    isinstance(arg, list)
                    or isinstance(arg, tuple)
                    or isinstance(arg, set)
            ):
                console.print(Pretty(arg))
            elif isinstance(arg, dict):
                console.print(Pretty(arg))
            elif isinstance(arg, (int, float)):
                console.print(f"[bold cyan]{arg}[/bold cyan]")
            elif isinstance(arg, bool):
                console.print(
                    f"[bold green]{arg}[/bold green]"
                    if arg
                    else f"[bold red]{arg}[/bold red]"
                )
            elif isinstance(arg, Exception):
                console.print("[bold red]Exception:[/bold red]", Pretty(arg))
                console.print(traceback.format_exc())
            else:
                # Check if it's a JSON string
                try:
                    parsed_json = json.loads(arg)
                    console.print(Pretty(parsed_json))
                except (json.JSONDecodeError, TypeError):
                    # Fallback for strings and other objects
                    if hasattr(arg, "__dataclass_fields__") or hasattr(
                            arg, "__dict__"
                    ):
                        console.print(Pretty(arg))
                    else:
                        console.print(arg)


trace = Trace()
