from pathlib import Path

root = Path(r"C:\git\ThinkingInTypes.github.io\Chapters")
for path in root.glob("C9[0-9]_*.md"):
    old_stem = path.stem  # e.g., "C90_Annotation_Reference"
    parts = old_stem.split("_", 1)
    if len(parts) != 2:
        continue  # skip malformed names

    old_num = int(parts[0][1:])  # extract number after 'C'
    new_num = old_num - 89  # C90 → Z01, C91 → Z02, ...
    new_stem = f"Z{new_num:02}_{parts[1]}"
    new_path = path.with_name(new_stem + path.suffix)

    print(f"Renaming {path.name} -> {new_path.name}")
    path.rename(new_path)
