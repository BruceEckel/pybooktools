#: artifacts.py
from pathlib import Path

from .panic import panic


def validation_dir(example_path: Path) -> Path:
    return example_path.parent / "_validation"


def opt_msg(msg: str) -> str:
    return f"{msg}: " if msg else ""


def valid_python_file(pyfile: Path, msg: str = "") -> Path:
    if not pyfile.is_file():
        panic(f"{opt_msg(msg)}{pyfile} not found")
    if pyfile.suffix != ".py":
        panic(f"{opt_msg(msg)}{pyfile} is not a Python file")
    validation_dir(pyfile).mkdir(exist_ok=True)
    return pyfile


def artifact_path(
        example_path: Path, id_ext: str, function_name: str = "", file_ext="py"
) -> Path:
    if not example_path.exists():
        panic(f"{opt_msg(function_name)}{example_path} does not exist")
    if not validation_dir(example_path).exists():
        panic(
            f"{opt_msg(function_name)}{validation_dir(example_path)} does not exist"
        )
    artifact_path = (
            validation_dir(example_path)
            / f"{example_path.stem}_{id_ext}.{file_ext}"
    )
    return artifact_path


def get_artifact(
        example_path: Path, id_ext: str, function_name: str = "", file_ext="py"
) -> Path:
    artifact = artifact_path(example_path, id_ext, function_name, file_ext)
    if not artifact.exists():
        panic(f"{opt_msg(function_name)}{artifact} does not exist")
    return artifact
