# simple_demo.py
from exception_catcher import Catch

print("Simple".center(25, "-"))
with Catch():
    1 / 0
## Error: division by zero

print("Lambda form".center(25, "-"))
with Catch() as _:
    _(lambda: 1 / 0)
    _(lambda: 1 / 0)
    _(lambda: 1 / 0)
    print("No lambda aborts the context:")
    1 / 0
    print("This doesn't run:")
    _(lambda: 1 / 0)
## Error: division by zero
## Error: division by zero
## Error: division by zero
## No lambda aborts the context:
## Error: division by zero
