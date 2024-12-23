# typer_demo.py
import typer

app = typer.Typer(context_settings={"help_option_names": ["--help", "-h"]})


@app.command(context_settings={"help_option_names": ["--help", "-h"]})
def main(
        ctx: typer.Context,
        arg: str = typer.Argument(
            None,
            help="Just some argument",
        ),
        flag1: bool = typer.Option(False, "--flag1", "-1", help="Flag number one"),
        flag2: bool = typer.Option(False, "--flag2", "-2", help="Flag number two"),
) -> None:
    print(ctx.get_help())
    typer.secho(f"arg: {arg}", fg="red")
    typer.secho(f"flag1: {flag1}", fg="red")
    typer.secho(f"flag2: {flag2}", fg="red")
    typer.secho(f"{ctx.args = }")
    typer.secho(f"{ctx.params = }")
    typer.secho(f"{ctx.command = }")
    typer.secho(f"{ctx.help_option_names = }")


typer.run(main)
##  Usage: typer_demo_1_tls_tags.py [OPTIONS]
## [ARG]
## +- Arguments ----------------------------------
## -------------------------------+
## |   arg      [ARG]  Just some argument
## [default: None]                        |
## +----------------------------------------------
## -------------------------------+
## +- Options ------------------------------------
## -------------------------------+
## | --flag1  -1        Flag number one
## |
## | --flag2  -2        Flag number two
## |
## | --help             Show this message and
## exit.                              |
## +----------------------------------------------
## -------------------------------+
## arg: None
## flag1: False
## flag2: False
## ctx.args = []
## ctx.params = {'arg': None, 'flag1': False,
## 'flag2': False}
## ctx.command = <TyperCommand main>
## ctx.help_option_names = ['--help']
