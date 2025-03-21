# test_insert_top_level_separators.py
from pybooktools.update_example_output import insert_top_level_separators
from pybooktools.validate import validate_transformer, UseCase

use_cases = [
    UseCase(
        case_id=1,
        script="""
x = 42
def greet():
    print("Hello, world!")

if x > 10:
    greet()
else:
    print("Goodbye!")

while True:
    print("Hello, world!")
    break
        """,
        expected_output="""
x = 42
print("__$1$_tls__")
def greet():
    print("Hello, world!")
print("__$2$_tls__")

if x > 10:
    greet()
else:
    print("Goodbye!")
print("__$3$_tls__")

while True:
    print("Hello, world!")
    break
print("__$4$_tls__")
        """,
    ),
    UseCase(
        case_id=2,
        script="""
class Example:
    def method(self):
        pass

example = Example()
example.method()
        """,
        expected_output="""
class Example:
    def method(self):
        pass
print("__$1$_tls__")

example = Example()
print("__$2$_tls__")
example.method()
print("__$3$_tls__")
        """,
    ),
    UseCase(
        case_id=3,
        script="""
def outer():
    def inner():
        print("Inner")
    inner()

outer()
        """,
        expected_output="""
def outer():
    def inner():
        print("Inner")
    inner()
print("__$1$_tls__")

outer()
print("__$2$_tls__")
        """,
    ),
    UseCase(
        case_id=4,
        script="""
for i in range(3):
    print(i)
        """,
        expected_output="""
for i in range(3):
    print(i)
print("__$1$_tls__")
        """,
    ),
    UseCase(
        case_id=5,
        script="""
x = 10
if x > 5:
    print("x is greater than 5")
        """,
        expected_output="""
x = 10
print("__$1$_tls__")
if x > 5:
    print("x is greater than 5")
print("__$2$_tls__")
        """,
    ),
]

if __name__ == "__main__":
    validate_transformer(insert_top_level_separators, use_cases)

""" Output From: validate_transformer

================ Case 1 passed ================
================ Case 2 passed ================
================ Case 3 passed ================
================ Case 4 passed ================
================ Case 5 passed ================
"""
