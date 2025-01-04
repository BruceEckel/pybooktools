import itertools
from typing import Annotated

from cyclopts import App, Parameter

app = App()


@app.command
def foo(val: int):
    print(f"FOO {val=}")


@app.command
def bar(flag: bool):
    print(f"BAR {flag=}")


@app.meta.default
def main(*tokens: Annotated[str, Parameter(allow_leading_hyphen=True)]):
    # tokens is ``["foo", "123", "AND", "foo", "456", "AND", "bar", "--flag"]``
    delimiter = "AND"

    groups = [list(group) for key, group in itertools.groupby(tokens, lambda x: x == delimiter) if not key] or [[]]
    # groups is ``[['foo', '123'], ['foo', '456'], ['bar', '--flag']]``

    for group in groups:
        # Execute each group
        app(group)


if __name__ == "__main__":
    app.meta(["foo", "123", "AND", "foo", "456", "AND", "bar", "--flag"])
    # FOO val=123
    # FOO val=456
    # BAR flag=True
