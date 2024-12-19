# reporting.py
import sys

from rich.console import Console
from rich.panel import Panel

console = Console()


def report(
        msg: str,
        title: str,
        msg_color: str = "orange3",
        title_color: str = "bold red",
        style="bold red",
) -> None:
    panel = Panel(
        f"[{msg_color}]{msg}[/{msg_color}]",
        title=f"[{title_color}]{title}[/{title_color}]",
        title_align="left",
        style=style,
    )
    console.print(panel)


def panic(msg: str) -> None:
    report(msg, "Panic")
    sys.exit()


def error(msg: str) -> None:
    report(msg, "Error")
    sys.exit()


def warn(msg: str) -> None:
    report(
        msg,
        "Warning",
        msg_color="dark_goldenrod",
        title_color="cornflower_blue",
        style="light_slate_blue",
    )
