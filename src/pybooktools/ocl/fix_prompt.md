Here's the file simple.py:

```python
print("foo")
print("bar")
```

After running auto_ocl.py on it, the resulting simple_2.py is:

```python
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path('.') / f"simple_ocl.py"

print('foo')
_o1 = ocl_format('foo')
print('bar')
_o2 = ocl_format('bar')


outfile.write_text("""
print('foo')
_o1 = ocl_format('foo')
print('bar')
_o2 = ocl_format('bar')

""", encoding="utf-8")
```

But it SHOULD be:

```python
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path('.') / f"simple_ocl.py"

print('foo')
_o1 = ocl_format('foo')
print('bar')
_o2 = ocl_format('bar')


outfile.write_text(f\"\"\"
print('foo')
{_o1}
print('bar')
{_o2}
\"\"\", encoding="utf-8")
```
