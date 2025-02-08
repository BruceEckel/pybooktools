# un_flatten.py
#: unflatten_python_directory.py

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Tuple


@dataclass
class DirectoryUnflattener:
    flattened_file: Path
    output_directory: Path

    def unflatten_directory(self) -> None:
        """
        Reconstruct the original directory structure from the flattened file.
        """
        top_level_dir = self.detect_top_level_directory()
        file_sections = self._extract_file_sections()

        for file_path, content in file_sections:
            relative_path = self._strip_to_top_level(file_path, top_level_dir)
            output_file = self.output_directory / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(content, encoding="utf-8")

    def detect_top_level_directory(self) -> str:
        """
        Detect the top-level directory from the first path in the flattened file.
        """
        pattern = re.compile(r"# Start of file: (.+?)\n")
        flattened_content = self.flattened_file.read_text(encoding="utf-8")

        match = pattern.search(flattened_content)
        if match:
            first_path = Path(match.group(1))
            return first_path.parts[0]
        raise RuntimeError("Could not detect the top-level directory from the flattened file.")

    @staticmethod
    def _strip_to_top_level(file_path: Path, top_level_dir: str) -> Path:
        """
        Strip the file path to start from the top-level directory.
        """
        parts = file_path.parts
        try:
            top_level_index = parts.index(top_level_dir)
            return Path(*parts[top_level_index:])
        except ValueError:
            raise RuntimeError(f"Path {file_path} does not contain the top-level directory '{top_level_dir}'")

    def _extract_file_sections(self) -> Generator[Tuple[Path, str], None, None]:
        """
        Extract each file's path and content from the flattened file.
        """
        pattern = re.compile(r"# Start of file: (.+?)\n(.*?)\n# End of file: \1", re.DOTALL)
        flattened_content = self.flattened_file.read_text(encoding="utf-8")

        for match in pattern.finditer(flattened_content):
            file_path_str, file_content = match.groups()
            yield Path(file_path_str), file_content


def main() -> None:
    """
    Main entry point for the script. Prompts for a flattened file and optional output directory.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Unflatten a file back into the original directory structure."
    )
    parser.add_argument(
        "flattened_file",
        type=str,
        help="Path to the flattened file to unflatten.",
    )
    parser.add_argument(
        "output_directory",
        type=str,
        nargs="?",
        help="Path to the output directory where the files will be reconstructed. Defaults to a directory named after "
             "the top-level directory.",
    )
    args = parser.parse_args()

    flattened_file = Path(args.flattened_file).resolve()

    if not flattened_file.is_file():
        print(f"Error: {flattened_file} is not a valid file.")
        return

    # Detect the top-level directory from the flattened file
    unflattener = DirectoryUnflattener(flattened_file, Path())
    top_level_dir = unflattener.detect_top_level_directory()

    # Set default output directory if not provided
    output_directory = Path(args.output_directory).resolve() \
        if args.output_directory \
        else flattened_file.parent / top_level_dir

    output_directory.mkdir(parents=True, exist_ok=True)
    unflattener.output_directory = output_directory
    unflattener.unflatten_directory()

    print(f"Files reconstructed in: {output_directory}")


if __name__ == "__main__":
    main()
