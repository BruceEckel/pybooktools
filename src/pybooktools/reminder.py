#: reminder.py
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    content = (
        "[deep_sky_blue1]z     [/deep_sky_blue1]"
        "    [yellow]Display this reminder[/yellow]\n"
        "[deep_sky_blue1]slug  [/deep_sky_blue1]"
        "    [yellow]Add/update sluglines in Python files[/yellow]\n"
        "[deep_sky_blue1]chapz  [/deep_sky_blue1]"
        "   [yellow]Renumber Markdown chapters & align chapter names[/yellow]\n"
        "[deep_sky_blue1]pyup[/deep_sky_blue1]"
        "      [yellow]Perform all steps to update examples with correct output[/yellow]\n"
        "[deep_sky_blue1]exnum[/deep_sky_blue1]"
        "     [yellow]Add numbers to[/yellow] [green]'\":' / '\"\"\":'[/green] [yellow]statements in Python files[/yellow]\n"
        "[deep_sky_blue1]etrack[/deep_sky_blue1]"
        "    [yellow]Add tracking statements in Python files[/yellow]\n"
        "[deep_sky_blue1]exup[/deep_sky_blue1]"
        "      [yellow]Update examples with correct output[/yellow]\n"
        "[deep_sky_blue1]xv[/deep_sky_blue1]"
        "        [yellow]Remove `_validation` directory[/yellow]"
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
