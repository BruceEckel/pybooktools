# parameters.py
from dataclasses import dataclass
from typing import Annotated

from cyclopts import App, Parameter

app = App()


@dataclass
class User:
    id: Annotated[int, Parameter(name=("--id", "-i"))]  # default behavior
    email: Annotated[str, Parameter(name=("--email", "-e"))]  # overrides
    pwd: Annotated[str, Parameter(name=("--password", "-p"))]  # dot-notation with parent


@app.command
def create(user: User):
    print(f"Creating {user=}")


app()
