from pathlib import Path


def create_demo_files(demo_dir: str, examples: dict[str, str]) -> list[Path]:
    demo_path = Path(demo_dir)
    demo_path.mkdir(exist_ok=True)

    results: list[Path] = []
    for filename, content in examples.items():
        (demo_path / filename).write_text(content, encoding="utf-8")
        results.append(demo_path / filename)
    results.append(demo_path / "nonexistent.py")
    return results
