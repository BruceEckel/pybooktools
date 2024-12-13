#: add_output.py
import re
from argparse import ArgumentParser
from pathlib import Path

from pybooktools.ptag import add_ptags
from pybooktools.util import run_script, valid_python, cleaned_dir


def main() -> None:
    print("append_output.py")
    parser = ArgumentParser(description="Add outputs to a Python example")
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
    # Remove comments starting with `#| `
    cleaned_code = re.sub(r"^## .*$", "", original_source, flags=re.MULTILINE)
    with_ptags = add_ptags(cleaned_code)
    ptagged = write_with_ext(with_ptags, "1_ptags")
    output = run_script(ptagged)
    print(output)
    # shutil.copy(outfile, example_path)
    # if not args.verbose:
    #     shutil.rmtree(check_dir)
    # if args.verbose:
    #     print(example_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
