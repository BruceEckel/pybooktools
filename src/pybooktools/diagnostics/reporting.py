# reporting.py
import sys

from pybooktools.display import report


def panic(msg: str) -> None:
    report(msg, "Panic")
    sys.exit()


def error(msg: str) -> None:
    report(msg, "Error")
    sys.exit()


def warn(msg: str) -> None:
    report(
        msg,
        "Warning",
        msg_color="dark_goldenrod",
        title_color="cornflower_blue",
        style="light_slate_blue",
    )
