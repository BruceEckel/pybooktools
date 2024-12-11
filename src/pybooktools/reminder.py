#: reminder.py
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    content = (
        "[deep_sky_blue1]c       [/deep_sky_blue1]"
        "    [yellow]Display these commands[/yellow]\n"
        "[deep_sky_blue1]ocl   [/deep_sky_blue1]"
        "      [yellow]Update examples with Output Comment Lines[/yellow]\n"
        "[deep_sky_blue1]bookup[/deep_sky_blue1]"
        "      [yellow]Update book examples from source repository[/yellow]\n"
        "[deep_sky_blue1]slug    [/deep_sky_blue1]"
        "    [yellow]Add or update sluglines in Python files[/yellow]\n"
        "[deep_sky_blue1]chapnum  [/deep_sky_blue1]"
        "   [yellow]Renumber Markdown chapters & align chapter names[/yellow]\n"
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
