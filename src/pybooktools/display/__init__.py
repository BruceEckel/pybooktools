"""
Standardized nice display functions.
Works particularly well with classes that define a __rich__ method.
https://rich.readthedocs.io
Use:
- Panel.fit
- Possibly tables: https://rich.readthedocs.io/en/stable/tables.html
"""

from .report import report, display_dict, display_path_list, display

__all__ = [
    "report",
    "display_path_list",
    "display_dict",
    "display",
]
