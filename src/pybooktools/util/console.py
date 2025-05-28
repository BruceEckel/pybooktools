# console.py
from rich.console import Console

from pybooktools.util import config

console = Console(width=config.LINE_LENGTH)
