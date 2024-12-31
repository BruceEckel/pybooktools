# reporting.py
import sys

from pybooktools.display import report


def panic(msg: str) -> None:
    report("Panic", msg)
    sys.exit()


def error(msg: str) -> None:
    report("Error", msg)
    sys.exit()


def warn(msg: str) -> None:
    report(
        "Warning",
        msg,
        msg_color="dark_goldenrod",
        title_color="cornflower_blue",
        style="light_slate_blue",
    )
