# Exception Catcher 

Succinctly catches and displays exceptions using a succinct form.
If you know code will fail with an exception, do this:

```python
from exception_catcher import Catch

print("Simple".center(25, "-"))
with Catch():
    1 / 0
## Error: division by zero
```

Displaying failing expressions one at a time this way is normally all you'll need.
If you have a number of failing expressions in a row, you can express them as a block using the lambda form:

```python
from exception_catcher import Catch

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
 ```

The first failure doesn't abort the context; all the expressions are executed.

- This will be applied to my own examples, so I can adjust those examples to fit my needs.
- Most of the time, when I need this, I will know that a function fails and can just use the simple form.
- I probably won't use the lambda form much, if at all, but if I need it, it's there. 
