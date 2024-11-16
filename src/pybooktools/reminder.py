from rich.console import Console

console = Console()


def main() -> None:
    console.print("[green1]Available commands:[/green1]")
    console.print(
        "  [bold blue]slug[/bold blue]   Add/update sluglines in Python files"
    )
    console.print(
        "  [bold blue]upcon[/bold blue]  Update 'console ==' statements in Python files"
    )
    console.print(
        "  [bold blue]uplist[/bold blue] Update code listings in Markdown files"
    )
    console.print(
        "  [bold blue]chapz[/bold blue]  Renumber Markdown chapters & align chapter names"
    )


if __name__ == "__main__":
    main()
