# app_default.py
from cyclopts import App
from icecream import ic

app = App(version_flags=[])


@app.default
def foo(arg: list[int]):
    print(f"{type(arg) = }")
    ic(arg)


app()
