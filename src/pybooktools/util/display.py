# display.py
from pathlib import Path
from typing import Any

from icecream import ic
from rich.console import Console
from rich.panel import Panel

from pybooktools.trace import trace

console = Console()


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
    dbg(f"In display_function_name, {bool(trace) = } {only_while_tracing = }")
    if only_while_tracing:
        if not trace:
            dbg("Early return from display_function_name")
            return

    import inspect

    dbg("Continuing display_function_name")
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
    print(f"{trace = }")
    display_function_name("Foo")
    trace.enable()
    print(f"{trace = }")
    display_function_name("Bar")
