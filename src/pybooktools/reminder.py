# reminder.py
from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    content = (
        "[deep_sky_blue1]cr      [/deep_sky_blue1]"
        "    [yellow]Display these commands[/yellow]\n"
        "[deep_sky_blue1]px    [/deep_sky_blue1]"
        "      [yellow]Add/Update Output Comment Lines in Python examples[/yellow]\n"
        "[deep_sky_blue1]bookup[/deep_sky_blue1]"
        "      [yellow]Update book examples from source repository[/yellow]\n"
        "[deep_sky_blue1]slug    [/deep_sky_blue1]"
        "    [yellow]Add or update sluglines in Python files[/yellow]\n"
        "[deep_sky_blue1]chapnum  [/deep_sky_blue1]"
        "   [yellow]Renumber Markdown chapters & align chapter names[/yellow]"
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
