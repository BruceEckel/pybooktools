# issue_201.py
import typer

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def main(nom: str):
    print(f"Hello {nom}")


@app.command()
def main2(nom: str):
    print(f"Bye {nom}")


if __name__ == "__main__":
    app()
