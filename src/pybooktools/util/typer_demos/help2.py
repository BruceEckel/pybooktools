# help2.py
import typer

app = typer.Typer()


@app.command(context_settings={"help_option_names": ["--help", "-h"]})
def main(
        ctx: typer.Context,
) -> None:
    typer.echo(f"{ctx.help_option_names = }")


typer.run(main)
## ctx.help_option_names = ['--help']
