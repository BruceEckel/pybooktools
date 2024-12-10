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


def warn(msg: str, title="Warning") -> None:
    console.print(
        Panel(
            f"[dark_goldenrod]{msg}[/dark_goldenrod]",
            title=f"[cornflower_blue]{title}[cornflower_blue]",
            title_align="left",
            style="light_slate_blue",
        )
    )
