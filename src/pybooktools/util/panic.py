#: panic.py
import sys

from rich.console import Console
from rich.panel import Panel

console = Console()


def panic(msg: str, title="Panic") -> None:
    panel = Panel(
        f"[orange3]{msg}[/orange3]",
        title=f"[bold red]{title}[/bold red]",
        title_align="left",
        style="bold red",
    )
    console.print(panel)
    sys.exit()


def error(msg: str) -> None:
    panic(msg, title="Error")
