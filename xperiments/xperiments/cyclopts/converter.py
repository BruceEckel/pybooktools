# converter.py
"""Demonstrate conversion from list[int] to str"""
from typing import Annotated, Sequence

from cyclopts import App, Parameter, Token
from icecream import ic

app = App(version_flags=[], help=__doc__)


def convert(type_, tokens: Sequence[Token]) -> str:
    ic(type_)
    ic(tokens)
    return "".join([t.value for t in tokens])


@app.default
def _(arg: Annotated[list[int], Parameter(converter=convert)]):
    print(f"{type(arg) = }")
    ic(arg)


app()

"""
Test with:
> python -m doctest converter.py

Example:
    >>> from converter import app
    >>> from unittest.mock import patch
    >>> with patch("sys.argv", ["converter.py", "42", "99", "11"]):
    ...     app()
    ic| type_: list[int]
    ic| tokens: (Token(keyword=None, value='42', source='cli', index=0, keys=(), implicit_value=<UNSET>),
                 Token(keyword=None, value='99', source='cli', index=0, keys=(), implicit_value=<UNSET>),
                 Token(keyword=None, value='11', source='cli', index=0, keys=(), implicit_value=<UNSET>))
    type(arg) = <class 'str'>
    ic| arg: '429911'

Help Example:
    >>> with patch("sys.argv", ["converter.py", "-h"]):
    ...     app()  # doctest: +ELLIPSIS
    Usage:  COMMAND [ARGS] [OPTIONS]
    ...
    ╭─ Commands ──...
    │ --help -h  Display this message and exit.                                                                            │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ...

Error Example:
    >>> with patch("sys.argv", ["converter.py"]):
    ...     app()
    ╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ Parameter "--arg" requires an argument.                                                                              │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
"""

