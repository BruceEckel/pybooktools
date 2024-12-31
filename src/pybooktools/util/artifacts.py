# artifacts.py
from pathlib import Path

from pybooktools.util.display import error


def validation_dir(example_path: Path) -> Path:
    return example_path.parent / "_validation"


def opt_msg(msg: str) -> str:
    return f"{msg}: " if msg else ""


def artifact_path(
        example_path: Path, id_ext: str, function_name: str = "", file_ext="py"
) -> Path:
    if not example_path.exists():
        error(f"{opt_msg(function_name)}{example_path} does not exist")
    if not validation_dir(example_path).exists():
        error(
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
        error(f"{opt_msg(function_name)}{artifact} does not exist")
    return artifact
