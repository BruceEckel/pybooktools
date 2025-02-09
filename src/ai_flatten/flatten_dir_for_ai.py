# flatten_dir_for_ai.py
import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, List

header = """
What follows is intended to be used as input to AI models that can understand Python code.

The files are "flattened" into a single text file with one file per Python file.
Each file starts with a comment indicating the file's path, followed by the file's content.
The end of each file is marked with a comment indicating the end of the file.

Please absorb these files, and produce requested corrections in the same format.
When producing corrections, please use the same file path format as the original files.
When producing corrections, only include the files that are modified.
"""


@dataclass
class DirectoryFlattener:
    directory: Path
    ignore_patterns: List[str] = field(default_factory=lambda: [
        ".*"  # Ignore directories starting with '.'
    ])

    def flatten_directory(self) -> Path:
        """
        Create a single text file containing all Python files in the directory tree,
        excluding directories that match ignore patterns.
        """
        output_file = self.directory.parent / f"{self.directory.name}_ai_flattened.txt"
        output_content = "\n".join(
            self._format(path) for path in self._python_files()
        )
        print(f"{output_content = }")
        output_file.write_text(header + output_content, encoding="utf-8")
        return output_file

    def _python_files(self) -> Generator[Path, None, None]:
        """Recursively yield all Python files in the directory, skipping ignored directories."""
        for file_path in self.directory.rglob("*.py"):
            if not self._ignore(file_path):
                print(f"{file_path = }")
                yield file_path

    def _ignore(self, file_path: Path) -> bool:
        """
        Check if the file or directory path should be ignored based on the ignore patterns.
        """
        ignore = any(re.fullmatch(pattern, part) for pattern in self.ignore_patterns for part in file_path.parts)
        print(f"{file_path = }  {ignore = }")
        return ignore

    @staticmethod
    def _format(file_path: Path) -> str:
        """
        Format the content of a file with a tag indicating its path.
        """
        file_content = file_path.read_text(encoding="utf-8")
        return f"# Start of file: {file_path}\n{file_content}\n# End of file: {file_path}\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Flatten a Python directory tree into a single text file"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing Python files to flatten",
    )
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    print(f"{directory = }")
    if not directory.is_dir():
        print(f"Error: {directory} is not a valid directory.")
        return

    flattener = DirectoryFlattener(directory)
    print(f"{flattener = }")
    output_file = flattener.flatten_directory()
    print(f"Flattened content written to: {output_file}")


if __name__ == "__main__":
    main()
