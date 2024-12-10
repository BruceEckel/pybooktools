
from pybooktools.aocl import ocl_format
from pathlib import Path

print('foo')
_o1 = ocl_format('foo')
print('bar')
_o2 = ocl_format('bar')


outfile = Path("C:\git\pybooktools\src\pybooktools\demos\.checksimple") / "simple_ocled.py"
outfile.write_text(f"""print('foo')
{_o1}
print('bar')
{_o2}
""", encoding="utf-8")
    