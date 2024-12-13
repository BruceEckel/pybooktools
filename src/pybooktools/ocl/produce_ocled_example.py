#: produce_ocled_example.py
import shutil
from argparse import ArgumentParser
from pathlib import Path

from pybooktools.ocl import add_ocl, embed_ocl_results
from pybooktools.util import run_script, valid_python, cleaned_dir


def main() -> None:
    parser = ArgumentParser(description="Add OCLs to a Python example")
    parser.add_argument("pyfile", type=str, help="The Python example file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Add informative output"
    )
    args = parser.parse_args()
    example_path = Path(args.pyfile).resolve()
    check_dir = cleaned_dir(example_path, ".check_")

    def write_with_ext(python_script: str, ext: str) -> Path:
        outpath = check_dir / f"{example_path.stem}_{ext}.py"
        outpath.write_text(python_script, encoding="utf-8")
        return outpath

    original_source = valid_python(example_path)
    with_ocls = add_ocl(original_source)
    write_with_ext(with_ocls, "1_ocls")
    embedded_ocl_results = embed_ocl_results(with_ocls)
    write_with_ext(embedded_ocl_results, "1a_embedded")
    outfile = check_dir / f"{example_path.stem}_3_ocled.py"

    ocl_generator = f'''
from pybooktools.ocl import ocl_format
from pathlib import Path

{with_ocls}

outfile = Path(r"{outfile}")
outfile.write_text(f"""\
{embedded_ocl_results}\
""", encoding="utf-8")
    '''

    run_script(write_with_ext(ocl_generator, "2_generator"))
    # print(outfile.read_text(encoding="utf-8"))
    shutil.copy(outfile, example_path)
    if not args.verbose:
        shutil.rmtree(check_dir)
    if args.verbose:
        print(example_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
