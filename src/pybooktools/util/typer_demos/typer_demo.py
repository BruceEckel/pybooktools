# typer_demo.py
import typer

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def main(
        ctx: typer.Context,
        arg: str = typer.Argument(
            None,
            help="Just some argument",
        ),
        flag1: bool = typer.Option(False, "--flag1", "-1", help="Flag number one"),
        flag2: bool = typer.Option(False, "--flag2", "-2", help="Flag number two"),
) -> None:
    # print(ctx.get_help())
    typer.secho(f"arg: {arg}", fg="red")
    typer.secho(f"flag1: {flag1}", fg="red")
    typer.secho(f"flag2: {flag2}", fg="red")
    typer.secho(f"{ctx.args = }")
    typer.secho(f"{ctx.params = }")
    typer.secho(f"{ctx.command = }")
    typer.secho(f"{ctx.help_option_names = }")


app()
