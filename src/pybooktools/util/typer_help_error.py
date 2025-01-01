# typer_help_error.py
from dataclasses import dataclass

import typer
from rich.panel import Panel

from pybooktools.util import console


@dataclass
class HelpError:
    ctx: typer.Context

    def __call__(self, msg: str) -> None:
        typer.echo(self.ctx.get_help())
        console.print(Panel(
            f"[orange3]{msg}[/orange3]",
            title=f"[bold red]Error[/bold red]",
            title_align="left",
            style="bold red"))
        self.ctx.exit(1)


if __name__ == "__main__":
    app = typer.Typer(
        context_settings={"help_option_names": ["--help", "-h"]},
        add_completion=False,
        # rich_markup_mode="rich",
    )


    @app.command(no_args_is_help=True)
    def test(ctx: typer.Context, arg: str = typer.Argument(...)):
        """For testing HelpError"""
        console.rule("starting test")
        help_error = HelpError(ctx)
        print(f"{ctx.get_help() = }")
        if arg == "error":
            help_error("testing...")
        if arg == "foo":
            help_error("help_error with foo")
        print(f"{arg = }")


    app()
