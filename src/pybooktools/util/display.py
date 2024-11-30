from rich.console import Console
from rich.panel import Panel

from pybooktools.util import trace

console = Console()


def display(msg: str, title="", with_trace=True) -> None:
    print(f"in display {msg = }")
    # print(f"{trace.on() = }")
    print(f"{with_trace = }, {(not trace) = }")
    if with_trace and (not trace.on()):
        return
    print("passed check")
    if title:
        title = (f"[green]{title}[/green]",)
    panel = Panel(
        f"[orange3]{msg}[/orange3]",
        title=title,
        title_align="left",
        style="green",
    )
    console.print(panel)
