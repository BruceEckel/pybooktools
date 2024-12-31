# no_args_is_help.py
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def create():
    """
    Doc string for create command
    """
    print("Creating user: Hiro Hamada")


@app.command()
def delete():
    """
    Doc string for delete command
    """
    print("Deleting user: Hiro Hamada")


if __name__ == "__main__":
    app()
