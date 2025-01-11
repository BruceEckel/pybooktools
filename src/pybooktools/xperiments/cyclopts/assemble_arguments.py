# assemble_arguments.py
from dataclasses import dataclass
from typing import Annotated

from cyclopts import App, Parameter
from icecream import ic

app = App()


@dataclass
class User:
    id: int
    name: Annotated[str, Parameter(name="--fullname")]


@app.default
def main(_: User):
    pass


for argument in app.assemble_argument_collection():
    print(f"name: {argument.name:16} hint: {str(argument.hint):16} keys: {str(argument.keys)}")
ic(app.assemble_argument_collection())
