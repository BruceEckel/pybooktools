"""
Aggregate tasks from individual task modules in
this package.
"""

from invoke import Collection

from pybooktools.invoke_tasks.prettier import prettier
from pybooktools.invoke_tasks.run_all import examples
from pybooktools.invoke_tasks.semantic_breaks import rewrite_with_semantic_breaks
from pybooktools.invoke_tasks.validate_output import validate

namespace = Collection(
    examples,
    validate,
    # rewrite_with_semantic_breaks,
)
