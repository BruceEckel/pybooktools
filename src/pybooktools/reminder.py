#: reminder.py
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    content = (
        "[deep_sky_blue1]slug  [/deep_sky_blue1]"
        "    [yellow]Add/update sluglines in Python files[/yellow]\n"
        "[deep_sky_blue1]checkpy[/deep_sky_blue1]"
        "   [yellow]Check/Update[/yellow] [green]'\":' / '\"\"\":'[/green] [yellow]statements in Python files[/yellow]\n"
        "[deep_sky_blue1]upcon  [/deep_sky_blue1]"
        "   [yellow]Update[/yellow] [green]'console =='[/green] [yellow]statements in Python files[/yellow]\n"
        "[deep_sky_blue1]uplist  [/deep_sky_blue1]"
        "  [yellow]Update code listings in Markdown files[/yellow]\n"
        "[deep_sky_blue1]chapz  [/deep_sky_blue1]"
        "   [yellow]Renumber Markdown chapters & align chapter names[/yellow]\n"
        "[deep_sky_blue1]pyout  [/deep_sky_blue1]"
        "   [yellow]Check ': ' outputs of Python example(s)[/yellow]"
    )
    console.print(
        Panel(
            content,
            border_style="green1",
            title="Commands",
            title_align="left",
        )
    )


if __name__ == "__main__":
    main()
