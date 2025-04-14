# prettier.py
from pathlib import Path

from invoke import task


@task(
    help={
        "target": "File or directory to format (default: current directory)",
        "prose_wrap": "How to wrap markdown text: 'always', 'never', or 'preserve'",
        "print_width": "Maximum line length before wrapping (default: 80)",
    }
)
def prettier(
    ctx,
    target: str = ".",
    prose_wrap: str = "preserve",
    print_width: int = 100,
) -> None:
    """
    invoke prettier (by itself on directory) --target=(file|dir)

    This task runs `npx prettier` using the provided options. It defaults to
    formatting the current directory with prose wrapping preserved and a
    print width of 80 characters.
    """
    path = Path(target)
    if not path.exists():
        print(f"❌ Target does not exist: {target}")
        return

    command = (
        f"npx prettier --write {path} "
        f"--prose-wrap {prose_wrap} "
        f"--print-width {print_width}"
    )

    ctx.run(command, echo=True)
