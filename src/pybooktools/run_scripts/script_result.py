# script_result.py
from typing import NamedTuple


class ScriptResult(NamedTuple):
    return_code: int
    result_value: str
