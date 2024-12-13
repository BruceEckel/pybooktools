# update_example_output.py
import re
import shutil
from argparse import ArgumentParser
from pathlib import Path

from icecream import ic

from pybooktools.error_reporting import error
from pybooktools.ptag import add_ptags, ensure_slug_line
from pybooktools.ptag.ptag_results_to_dict import ptags_to_dict
from pybooktools.util import run_script, valid_python, cleaned_dir


def main() -> None:
    parser = ArgumentParser(description="Add outputs to a Python example")
    parser.add_argument("pyfile", type=str, help="The Python example file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Add informative output"
    )
    parser.add_argument(
        "-n",
        "--no_overwrite",
        action="store_true",
        help="Don't overwrite original file",
    )
    args = parser.parse_args()
    example_path = Path(args.pyfile).resolve()
    # Also checks that file exists:
    original_source = ensure_slug_line(valid_python(example_path), example_path)
    check_dir = cleaned_dir(example_path, ".check_")
    if not check_dir.exists():
        error(f"{check_dir} not created")
    else:
        assert check_dir.is_dir()
        print(check_dir)

    def write_with_ext(python_script: str, ext: str, ftype="py") -> Path:
        assert check_dir.exists()
        assert check_dir.is_dir()
        outpath = check_dir / f"{example_path.stem}_{ext}.{ftype}"
        outpath.write_text(python_script, encoding="utf-8")
        return outpath

    old_ocls_removed = re.sub(
        r"^#\s*\|.*(\n|$)", "", original_source, flags=re.MULTILINE
    )

    # Remove comments starting with `## `
    cleaned_code = re.sub(
        r"^\s*## .*(\n|$)", "", old_ocls_removed, flags=re.MULTILINE
    )
    example_path.write_text(cleaned_code, encoding="utf-8")
    with_ptags = add_ptags(cleaned_code)
    ptagged = write_with_ext(with_ptags, "1_ptags")
    output = run_script(ptagged)
    ptag_dict = ptags_to_dict(output)
    if args.verbose:
        ic(ptag_dict)
    write_with_ext(ic.format(ptag_dict), "2_ptag_dict", ftype="txt")
    if args.verbose:
        print(example_path.read_text(encoding="utf-8"))
        print("with_ptags:\n", with_ptags)
    with_outputs = []
    for line in with_ptags.splitlines():
        for key, value in ptag_dict.items():
            if key in line:
                with_outputs.extend(value)
                break
        else:
            with_outputs.append(line)
    with_outputs.append("")
    write_with_ext("\n".join(with_outputs), "3_with_outputs")
    if args.verbose:
        ic(with_outputs)
    result = "\n".join(with_outputs)
    if args.verbose:
        print(result)
    if not args.no_overwrite:
        example_path.write_text(result, encoding="utf-8")
        print(f"Updated {example_path.name}")
    else:
        print(f"Original {example_path.name} NOT overwritten")

    if not args.verbose:
        shutil.rmtree(check_dir)


if __name__ == "__main__":
    main()
