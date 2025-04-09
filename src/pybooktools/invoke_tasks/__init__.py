"""
Aggregate tasks from individual task modules in
this package.
"""

from invoke import Collection

from pybooktools.invoke_tasks.run_all import examples
from pybooktools.invoke_tasks.validate_output import validate

namespace = Collection(
    examples,
    validate,
)
