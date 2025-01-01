# update_example_output.py
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from rich.text import Text

from pybooktools.util import console
from .example_updater import ExampleUpdater


class RichHelpFormatter(RawDescriptionHelpFormatter):
    def format_help(self) -> str:
        help_text = super().format_help()
        console.print(Text(help_text, style="bold green"))
        return ""


def process(file_path: Path, verbose=False, wrap: bool = True) -> None:
    ExampleUpdater(file_path, verbose=verbose).update_output(wrap=wrap)


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
    parser.add_argument(
        "--nowrap",
        action="store_true",
        help="Do not wrap output lines",
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

    wrap = False if args.nowrap else True

    if args.pyfiles:
        for file_name in args.pyfiles:
            file_path = Path(file_name)
            if file_path.is_file() and file_path.suffix == ".py":
                process(file_path, args.verbose, wrap=wrap)
            else:
                print(f"Error: File not found: {file_name}")
    elif args.all:
        for file_path in Path.cwd().glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            process(file_path, args.verbose, wrap=wrap)
    elif args.recurse:
        for file_path in Path.cwd().rglob("*.py"):
            process(file_path, args.verbose, wrap=wrap)


if __name__ == "__main__":
    main()
