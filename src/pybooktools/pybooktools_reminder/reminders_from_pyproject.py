# reminders_from_pyproject.py
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

cc = "deep_sky_blue1"  # Command Color
dc = "yellow"  # Description Color


@dataclass
class Command:
    name: str
    description: str


def find_pyproject(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.exists():
            return candidate
    return None


def extract_commands(toml_path: Path) -> list[Command]:
    lines = toml_path.read_text(encoding="utf-8").splitlines()
    commands: list[Command] = []
    in_scripts = False
    pending_comment: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts:
            if stripped.startswith("[") and stripped.endswith("]"):
                break  # End of the section
            if stripped.startswith("#"):
                pending_comment = stripped.lstrip("#").strip()
                continue
            if "=" in line:
                name = line.split("=")[0].strip()
                if pending_comment:
                    commands.append(Command(name=name, description=pending_comment))
                    pending_comment = None
                else:
                    commands.append(Command(name=name, description=""))
    return commands


def format_reminders(commands: list[Command]) -> str:
    return "\n".join(
        f"[{cc}]{cmd.name:<14}[/{cc}][{dc}]{cmd.description}[/{dc}]"
        for cmd in commands
    )


def main() -> None:
    start_dir = Path(__file__).resolve().parent
    pyproject_path = find_pyproject(start_dir)
    if not pyproject_path:
        console.print("[red]pyproject.toml not found[/red]")
        return

    commands = extract_commands(pyproject_path)
    reminders = format_reminders(commands)

    console.print(
        Panel(
            reminders,
            border_style="green1",
            title="Commands",
            title_align="left",
        )
    )


if __name__ == "__main__":
    main()
