#: panic.py
import sys

from rich.console import Console
from rich.panel import Panel

console = Console()


def panic(msg: str) -> None:
    panel = Panel(
        f"[orange3]{msg}[/orange3]",
        title="[bold red]Panic[/bold red]",
        title_align="left",
        style="bold red",
    )
    console.print(panel)
    sys.exit()
