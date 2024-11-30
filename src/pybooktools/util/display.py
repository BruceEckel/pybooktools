from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from pybooktools.tracing import trace

console = Console()


def dbg(msg: str) -> None:
    pass
    # console.print(
    #     f"[medium_turquoise]dbg:[/medium_turquoise] [yellow]{msg}[/yellow]"
    # )


def trace_function_name(title="") -> None:
    dbg(f"In trace_function_name, {bool(trace) = }")
    if not trace:
        dbg("Early return from trace_function_name")
        return
    import inspect

    dbg("Continuing trace_function_name")
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
