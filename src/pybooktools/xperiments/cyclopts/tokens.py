from enum import Enum
from typing import Annotated

from cyclopts import App, Parameter

app = App(version_flags=[])


class DiagnosticFlag(Enum):
    VERBOSE = "-v"
    TRACE = "-t"
    DEBUG = "-d"

    @classmethod
    def __contains__(cls, token: str) -> bool:
        return token in {item.value for item in cls}


@app.command(name="-f", help="It's foo")
def foo(val: int, diagnostics: list[DiagnosticFlag] = None):
    print(f"FOO {val=}")
    print(f"{diagnostics=}")


@app.command(name="-b", help="It's bar")
def bar(flag: bool = False, diagnostics: list[DiagnosticFlag] = None):
    print(f"BAR {flag=}")
    print(f"{diagnostics=}")


@app.command(name="-z", help="It's baz")
def baz(files: list[str], diagnostics: list[DiagnosticFlag] = None):
    print(f"BAZ {files=}")
    print(f"{diagnostics=}")


@app.meta.default
def main(*tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)]):
    print(f"{tokens=}")
    token_list = list(tokens)
    diag_flags: list[DiagnosticFlag] = [DiagnosticFlag(token) for token in token_list if token in DiagnosticFlag]
    for flag in diag_flags:
        token_list.remove(flag.value)
    print(f"{token_list=}")
    print(f"{diag_flags=}")
    match token_list[0]:
        case "-f":
            foo(int(token_list[1]), diag_flags)
        case "-b":
            bar(bool(token_list[1]), diag_flags)
        case "-z":
            baz(token_list[1:], diag_flags)
        case _:
            app(["-h"])


if __name__ == "__main__":
    app.meta(["-f", "42", "-v", "-t"])
    app.meta(["-b", "0", "-v", "-d"])
    app.meta(["-z", "one", "two", "three", "-v", "-d"])
    app.meta(["-f", "42", "-d", "-v"])
    app.meta(["-b", "0", "-v", "-t"])
    app.meta(["-z", "one", "two", "three", "-t", "-d"])
    app.meta(["-f", "42"])
    app.meta(["-b", "0"])
    app.meta(["-z", "one", "two", "three"])
