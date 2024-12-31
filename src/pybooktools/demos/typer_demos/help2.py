# help2.py
import typer

app = typer.Typer(
    context_settings={"help_option_names": ["--help", "-h"]},
    add_completion=False,
)


@app.command(no_args_is_help=True)  # no_args_is_help must be in app.command
def main(ctx: typer.Context) -> None:  # Always pass ctx arg to get "-h" flag in help
    """help2.py in typer demos"""
    typer.echo(f"{ctx.help_option_names = }")
    # typer.echo(ctx.get_help())


app()
## ctx.help_option_names = ['--help']
