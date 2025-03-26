# example_updater.py
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from icecream import ic

from pybooktools.update_example_output.insert_tls_tags import insert_top_level_separators
from pybooktools.update_example_output.run_script import run_script
from pybooktools.update_example_output.tls_results_to_dict import tls_tags_to_dict
from pybooktools.util.path_utils import cleaned_dir
from pybooktools.util.python_example_validator import python_example_validator


@dataclass
class ExampleUpdater:
    example_path: Path
    verbose: bool
    example_name: Optional[str] = None
    validate_dir: Optional[Path] = None
    original_source: Optional[str] = None
    cleaned_code: Optional[str] = None
    updated_code: Optional[str] = None

    def __post_init__(self):
        self.example_name = self.example_path.name
        self.validate_dir = cleaned_dir(self.example_path, ".validate_")
        python_example_validator(self.example_path)
        self.original_source = self.example_path.read_text(encoding="utf-8")
        # Remove comments starting with `## `
        self.cleaned_code = re.sub(
            r"^\s*##.*(\n|$)", "", self.original_source, flags=re.MULTILINE
        )
        self.__write_with_ext(self.cleaned_code, "0_cleaned")

    def __write_with_ext(self, text: str, ext: str, ftype="py") -> Path:
        outpath = self.validate_dir / f"{self.example_path.stem}_{ext}.{ftype}"
        outpath.write_text(text, encoding="utf-8")
        return outpath

    def remove_validate_dir(self):
        shutil.rmtree(self.validate_dir)

    def update_output(self, wrap: bool = True) -> str:
        if self.verbose:
            print(f"update_output Updating {self.example_name}")
        with_tls_tags = insert_top_level_separators(self.cleaned_code)
        tls_tagged = self.__write_with_ext(with_tls_tags, "1_tls_tags")
        returncode, result_value = run_script(tls_tagged)
        if returncode != 0:
            if not self.verbose:
                self.remove_validate_dir()
            return f"Failed: {self.example_path.parent}/{self.example_name}    {returncode = }"
        self.__write_with_ext(result_value, "2_output", "txt")
        tls_tag_dict = tls_tags_to_dict(result_value, wrap=wrap)
        self.__write_with_ext(
            "\n".join(tls_tag_dict.keys()), "3_tls_tag_keys", ftype="txt"
        )
        if self.verbose:
            ic(tls_tag_dict)
        self.__write_with_ext(
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
        self.__write_with_ext(self.updated_code, "4_updated")
        if self.verbose:
            print(self.updated_code)
            print(f"Original {self.example_name} NOT overwritten")
        else:
            if self.original_source != self.updated_code:
                self.example_path.write_text(self.updated_code, encoding="utf-8")
                print(f"Updated {self.example_name}")
            self.remove_validate_dir()
        return ""
