import sys
from itertools import product

import pytest
from rich.console import Console
from rich.panel import Panel

from paths import app

console = Console(file=sys.stdout)


@pytest.mark.parametrize(
    "command, argument_list",
    product(
        ["-f1", "-f2", "-f3", "-f4"],
        [
            ["paths.py"],
            ["paths.py", "paths.py"],
            ["paths.py", "paths.py", "paths.py"],
            ["paths.py", "nonexistent.py"],
            ["nonexistent.py", "paths.py"],
            ["paths.py", "nonexistent1.py", "nonexistent2.py"],
            ["paths.py", "paths.py", "nonexistent3.py", "nonexistent4.py"],
        ]
    )
)
def test_examples(command, argument_list):
    """Test the examples function with different commands and argument lists."""
    cmdline = [command] + argument_list
    result = f"{cmdline} ==> "
    app(cmdline)
    console.print(Panel(result, title=command, style="bold"))
