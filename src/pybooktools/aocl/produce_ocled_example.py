#: produce_ocled_example.py
from argparse import ArgumentParser
from pathlib import Path

from pybooktools.aocl import add_ocl
from pybooktools.util import run_script, valid_python


def main() -> None:
    parser = ArgumentParser(
        description="Process a Python file for OCL formatting."
    )
    parser.add_argument(
        "file", type=str, help="The path to the Python file to process."
    )
    args = parser.parse_args()

    example_path = Path(args.file)
    source_code_1 = add_ocl(valid_python(example_path))

    # Prepare source_code_3
    source_code_3 = f'''
from pybooktools.auto_ocl import ocl_format
from pathlib import Path

outfile = Path('.') / f"{example_path.stem}_ocl.py"
outfile.write_text(f"""
{source_code_2a}
""", encoding="utf-8")
    '''

    output_path = example_path.parent / f"{example_path.stem}_3.py"
    output_path.write_text(source_code_3, encoding="utf-8")

    run_script(output_path)


if __name__ == "__main__":
    main()
