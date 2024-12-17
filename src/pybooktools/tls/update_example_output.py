# update_example_output.py
import re
import shutil
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import dataclass
from pathlib import Path

from icecream import ic
from rich.console import Console
from rich.text import Text

from pybooktools.tls import insert_top_level_separators, tls_tags_to_dict
from pybooktools.util import cleaned_dir, ensure_slug_line, run_script
from pybooktools.validate.validate_python_file import valid_python

console = Console()


class RichHelpFormatter(RawDescriptionHelpFormatter):
    def format_help(self) -> str:
        help_text = super().format_help()
        console.print(Text(help_text, style="bold green"))
        return ""


@dataclass
class ExampleUpdater:
    example_path: Path
    verbose: bool
    example_name: str = None
    validate_dir: Path = None
    original_source: str = None
    cleaned_code: str = None
    updated_code: str = None

    def __post_init__(self):
        self.example_name = self.example_path.name
        self.validate_dir = cleaned_dir(self.example_path, ".validate_")
        # Also checks that file exists:
        self.original_source = ensure_slug_line(
            valid_python(self.example_path), self.example_path
        )
        old_ocls_removed = re.sub(
            r"^#\s*\|.*(\n|$)", "", self.original_source, flags=re.MULTILINE
        )
        # Remove comments starting with `## `
        self.cleaned_code = re.sub(
            r"^\s*## .*(\n|$)", "", old_ocls_removed, flags=re.MULTILINE
        )

    def write_with_ext(self, text: str, ext: str, ftype="py") -> Path:
        outpath = self.validate_dir / f"{self.example_path.stem}_{ext}.{ftype}"
        outpath.write_text(text, encoding="utf-8")
        return outpath

    def remove_validate_dir(self):
        shutil.rmtree(self.validate_dir)

    def update_output(self) -> None:
        with_tls_tags = insert_top_level_separators(self.cleaned_code)
        tls_tagged = self.write_with_ext(with_tls_tags, "1_tls_tags")
        output = run_script(tls_tagged)
        self.write_with_ext(output, "2_output", "txt")
        tls_tag_dict = tls_tags_to_dict(output)
        if self.verbose:
            ic(tls_tag_dict)
        self.write_with_ext(
            ic.format(tls_tag_dict), "3_tls_tag_dict", ftype="txt"
        )
        if self.verbose:
            print(self.example_path.read_text(encoding="utf-8"))
            print("with_tls_tags:\n", with_tls_tags)
        with_outputs = []
        for line in with_tls_tags.splitlines():
            for key, value in tls_tag_dict.items():
                if key in line:
                    with_outputs.extend(value)
                    break
            else:
                with_outputs.append(line)
        with_outputs.append("")
        self.updated_code = "\n".join(with_outputs)
        self.write_with_ext(self.updated_code, "4_updated")
        if self.verbose:
            print(self.updated_code)
            print(f"Original {self.example_name} NOT overwritten")
        else:
            self.example_path.write_text(self.updated_code, encoding="utf-8")
            print(f"Updated {self.example_name}")
            self.remove_validate_dir()


def process(file_path: Path, verbose=False) -> None:
    ExampleUpdater(file_path, verbose=verbose).update_output()


def main() -> None:
    parser = ArgumentParser(
        description="Update embedded outputs in Python examples",
        usage="%(prog)s [-h] [-v] [-r | -a] [pyfile ...]",
        epilog=(
            "Examples:\n"
            "  script.py file1.py file2.py   # Process specific files\n"
            "  script.py -a                  # Process all Python files in the current directory\n"
            "  script.py -r                  # Process all Python files recursively in subdirectories\n"
        ),
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "pyfiles", nargs="*", type=str, help="The Python example file(s)"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Trace info, save intermediate files, don't overwrite original file",
    )

    # Add mutually exclusive group for -a and -r
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r",
        "--recurse",
        action="store_true",
        help="Find Python examples in subdirectories",
    )
    group.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Process all Python examples in the current directory",
    )

    args = parser.parse_args()

    if not args.pyfiles and not args.all and not args.recurse:
        parser.print_help()
        print("\nError: No files specified and no mode selected (-a or -r)\n")
        parser.exit(1)

    if args.pyfiles:
        for file_name in args.pyfiles:
            file_path = Path(file_name)
            if file_path.is_file() and file_path.suffix == ".py":
                process(file_path, args.verbose)
            else:
                print(f"Error: File not found: {file_name}")
    elif args.all:
        for file_path in Path.cwd().glob("*.py"):
            process(file_path, args.verbose)
    elif args.recurse:
        for file_path in Path.cwd().rglob("*.py"):
            process(file_path, args.verbose)


if __name__ == "__main__":
    main()
