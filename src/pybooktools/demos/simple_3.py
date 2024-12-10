
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path('.') / f"simple_ocl.py"
outfile.write_text(f"""
print('foo')
{ocl_format('foo')}
print('bar')
{ocl_format('bar')}

""", encoding="utf-8")
    