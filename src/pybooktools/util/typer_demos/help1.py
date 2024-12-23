# help1.py
import typer

app = typer.Typer(context_settings={"help_option_names": ["--help", "-h"]})


@app.command()
def main(
        ctx: typer.Context,
) -> None:
    typer.echo(f"{ctx.help_option_names = }")


typer.run(main)
