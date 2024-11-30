from pybooktools.tracing import trace
from pybooktools.util import trace_function_name

print(f"{trace = }")
trace_function_name("Foo")
trace.enable()
print(f"{trace = }")
trace_function_name("Bar")
