#: __init__.py
# This has to be separate to avoid circular imports
from .tracer import Trace

trace = Trace()

__all__ = [
    "trace",
]
