# display.py
import sys
from pathlib import Path
from typing import Any

from icecream import ic
from rich.panel import Panel

from .console import console


def icc(*_: Any) -> None:
    """Call ic() without the variable name prefix."""
    original_prefix = ic.prefix
    ic.configureOutput(prefix="")
    try:
        ic(*_)
    finally:
        ic.configureOutput(prefix=original_prefix)


# noinspection PyUnusedLocal
def dbg(msg: str) -> None:
    pass
    # Uncomment to enable dbg:
    # console.print(
    #     f"[medium_turquoise]dbg:[/medium_turquoise] [yellow]{msg}[/yellow]"
    # )


def display_function_name(title="", only_while_tracing=False) -> None:
    if only_while_tracing:
        return

    import inspect

    caller_frame = inspect.stack()[1]
    fname = f"{Path(caller_frame.filename).name}"
    panel_title = f"[green]{title}[/green]" if title else None
    panel = Panel(
        f"[orange3]{fname}[/orange3]",
        title=panel_title,
        title_align="left",
        style="green",
    )
    console.print(panel)


def test_display_function_name():
    display_function_name("Foo")
    display_function_name("Bar")


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


def panic(msg: str) -> None:
    report("Panic", msg)
    sys.exit()


def error(msg: str) -> None:
    report("Error", msg)
    sys.exit()


def warn(msg: str) -> None:
    report(
        "Warning",
        msg,
        msg_color="dark_goldenrod",
        title_color="cornflower_blue",
        style="light_slate_blue",
    )
