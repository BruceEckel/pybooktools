I would like a function that takes arguments such as any of the `a_n` here:

```python
a_1 = 1
a_2 = "foo"
a_3 = "A really long line that just keeps going am I finished yet? Yes!"
a_4 = {1:2, 3:4}
a_5 = {"a", "b", "c"}
a_6 = 3.14159
a_7 = f"The value of pi is {a_6}. Of course that has been rounded off"
```

If you pass it any arg:

```python
def ocl_format(arg: Any) -> str:
    ...
```

It will evaluate the result and produce the same output as `print()`, but formatted such that:
    1. It starts with `#| `
    2. Each resulting line is no wider than 47 characters ()

For the above examples, `ocl_format` will produce:

For | ocl_format produces this string 
a_1: "#| 1"
a_2: "#| foo"
a_3: "#| A really long line that just keeps going am\n#| I finished yet? Yes!"
a_4: "#| {1:2, 3:4}
a_5: '#| {"a", "b", "c"}'
a_6: "#| 3.14159"
a_7: "#| The value of pi is 3.14159. Of course that\n#|has been rounded off"
