from rich.jupyter import JupyterMixin
from rich.rule import Rule
from rich.text import Text

from pybooktools.util import console


# def display_path_list(paths: list[Path], title: str = "") -> None:
#     console.rule("[orange3]{title}")
#     for name in [p.name for p in paths]:
#         console.print(f"\t[sea_green2]{name}[/sea_green2]")
#     console.rule()


def rule_demo() -> list[Rule]:
    r = Rule("[orange3]The Title")
    t = Text("Some Text")
    r2 = Rule()
    return [r, t, r2]


def display(rich_list: list[JupyterMixin]) -> None:
    for rich_item in rich_list:
        console.print(rich_item)


if __name__ == "__main__":
    # display_available_python_files([])
    display(rule_demo())
