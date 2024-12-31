# reminder.py
from rich.panel import Panel

from pybooktools.util import console

cc = "deep_sky_blue1"  # Command Color
dc = "yellow"  # Description Color

reminders = f"""
[{cc}]cr        [/{cc}][{dc}]Display these commands[/{dc}]
[{cc}]px        [/{cc}][{dc}]Add/Update Output Comment Lines in Python examples[/{dc}]
[{cc}]bookup    [/{cc}][{dc}]Update book examples from source repository[/{dc}]
[{cc}]slug      [/{cc}][{dc}]Add or update sluglines in Python files[/{dc}]
[{cc}]chapnum   [/{cc}][{dc}]Renumber Markdown chapters & align chapter names[/{dc}]
""".strip()


def main() -> None:
    console.print(
        Panel(
            reminders,
            border_style="green1",
            title="Commands",
            title_align="left",
        )
    )


if __name__ == "__main__":
    main()
