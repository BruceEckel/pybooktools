# flatten_dir_for_ai.py
from dataclasses import dataclass
from pathlib import Path
from typing import Generator


@dataclass
class DirectoryFlattener:
    directory: Path

    def flatten_directory(self) -> Path:
        """
        Create a single text file containing all Python files in the directory tree.
        """
        output_file = self.directory.parent / f"{self.directory.name}_ai_flattened.txt"
        python_files = self._get_python_files()

        output_content = "\n".join(
            self._format_file_content(path) for path in python_files
        )
        output_file.write_text(output_content, encoding="utf-8")
        return output_file

    def _get_python_files(self) -> Generator[Path, None, None]:
        """Recursively yield all Python files in the directory."""
        return self.directory.rglob("*.py")

    @staticmethod
    def _format_file_content(file_path: Path) -> str:
        """
        Format the content of a file with a tag indicating its path.
        """
        file_content = file_path.read_text(encoding="utf-8")
        return f"# Start of file: {file_path}\n{file_content}\n# End of file: {file_path}\n"


def main() -> None:
    """
    Main entry point for the script. Prompts for a directory and flattens it.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Flatten a Python directory tree into a single text file."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Path to the directory containing Python files to flatten.",
    )
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        print(f"Error: {directory} is not a valid directory.")
        return

    flattener = DirectoryFlattener(directory)
    output_file = flattener.flatten_directory()
    print(f"Flattened content written to: {output_file}")


if __name__ == "__main__":
    main()
