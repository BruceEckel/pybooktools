from rich.console import Console
from rich.panel import Panel

console = Console()


def display(msg: str, title="") -> None:
    if title:
        title = (f"[green]{title}[/green]",)
    panel = Panel(
        f"[orange3]{msg}[/orange3]",
        title=title,
        title_align="left",
        style="green",
    )
    console.print(panel)
