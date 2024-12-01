#: test_trace_function_name.py
from pybooktools.tracing import trace
from pybooktools.util import display_function_name

print(f"{trace = }")
display_function_name("Foo")
trace.enable()
print(f"{trace = }")
display_function_name("Bar")
