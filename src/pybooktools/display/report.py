from pathlib import Path
from typing import Any

from rich.panel import Panel

from pybooktools.util import console


def display(msg: str) -> None:
    console.print(msg)


def report(
        title: str,
        msg: str,
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


def display_dict(title: str, data: dict[Any, Any]) -> None:
    console.rule(f"[red]{title}")
    for k, v in data.items():
        console.print(f"\t[red]{k}: {v}[/red]")
    console.rule("[red]")


def display_path_list(title: str, paths: list[Path]) -> None:
    console.rule(f"[orange3]{title}")
    for item in [it.name for it in paths]:
        console.print(f"\t[sea_green2]{item}[/sea_green2]")
    console.rule("[orange3]")
