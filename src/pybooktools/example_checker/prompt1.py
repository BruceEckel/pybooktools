from pathlib import Path


def number_output_strings(example_path: Path):
    if not example_path.is_file():
        print(f"{example_path} not found")
        return
    if example_path.suffix != ".py":
        print(f"{example_path} is not a Python file")
        return
    validate_dir = example_path.parent / "_validate"
    validate_dir.mkdir(exist_ok=True)
    example = example_path.read_text(encoding="utf-8")
    # Using libcst, find all unassigned strings that begin
    # with ':' and replace that ':' with a sequential number
    # followed by the ':' and the rest of the original string.
    # Store the result in the validate_dir with the stem of the
    # original file followed by _numbered.py
