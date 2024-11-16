from rich.console import Console

console = Console()


def main() -> None:
    console.print("[green1]Available commands:[/green1]")
    console.print(
        "  [deep_sky_blue1]slug[/deep_sky_blue1]   [yellow]Add/update sluglines in Python files[/yellow]"
    )
    console.print(
        "  [deep_sky_blue1]upcon[/deep_sky_blue1]  [yellow]Update[/yellow] 'console ==' [yellow]statements in Python files[/yellow]"
    )
    console.print(
        "  [deep_sky_blue1]uplist[/deep_sky_blue1] [yellow]Update code listings in Markdown files[/yellow]"
    )
    console.print(
        "  [deep_sky_blue1]chapz[/deep_sky_blue1]  [yellow]Renumber Markdown chapters & align chapter names[/yellow]"
    )


if __name__ == "__main__":
    main()
