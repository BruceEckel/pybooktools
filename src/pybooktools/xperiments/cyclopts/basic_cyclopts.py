# basic_cyclopts.py
from cyclopts import App

app = App()


@app.default
def _(strings: list[str] = None):
    if strings:
        print(f"{strings = }")
    else:
        print("no args")


app()
