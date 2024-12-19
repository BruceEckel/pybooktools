#: __init__.py

from .reporting import report, panic, error, warn
from .tracer import Trace

trace = Trace()

__all__ = [
    "report",
    "panic",
    "error",
    "warn",
    "trace",
]
