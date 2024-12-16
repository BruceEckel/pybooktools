# update_example_output.py
import re
import shutil
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from icecream import ic

from pybooktools.tls import insert_top_level_separators, tls_tags_to_dict
from pybooktools.util import cleaned_dir, ensure_slug_line, run_script
from pybooktools.validate.validate_python_file import valid_python


@dataclass
class ExampleUpdater:
    example_path: Path
    overwrite: bool
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
        self.example_path.write_text(self.cleaned_code, encoding="utf-8")
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
        self.write_with_ext("\n".join(with_outputs), "4_with_outputs")
        self.updated_code = "\n".join(with_outputs)
        if self.verbose:
            print(self.updated_code)
        if self.overwrite:
            self.example_path.write_text(self.updated_code, encoding="utf-8")
            print(f"Updated {self.example_name}")
        else:
            print(f"Original {self.example_name} NOT overwritten")
        if not self.verbose:
            self.remove_validate_dir()


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
    parser.add_argument(
        "-r",
        "--recurse",
        action="store_true",
        help="Find Python examples in subdirectories",
    )
    args = parser.parse_args()
    updater = ExampleUpdater(
        Path(args.pyfile).resolve(), args.no_overwrite, args.verbose
    )
    updater.update_output()


if __name__ == "__main__":
    main()
