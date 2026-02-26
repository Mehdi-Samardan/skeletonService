import os
from pathlib import Path

import yaml
from yaml import YAMLError


def load_yaml_file(file_path: str) -> object:
    """Load and return the contents of a single YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data if data is not None else {}


def load_all_yaml_from_directory(directory_path: str, recursive: bool = False) -> list[dict]:
    """Load all YAML files from a directory.

    Args:
        directory_path: Path to the directory to scan.
        recursive: When True, also scan subdirectories. Names will include
                   the relative path, e.g. "PPG/Front" instead of "Front".

    Returns:
        List of dicts: [{"name": "...", "content": {...}}, ...]
    """
    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    pattern = "**/*.yaml" if recursive else "*.yaml"
    yaml_files = sorted(directory.glob(pattern))

    results = []
    for file_path in yaml_files:
        try:
            data = load_yaml_file(str(file_path))
        except yaml.YAMLError:
            # Skip malformed YAML files silently (broken source templates).
            continue

        if recursive:
            relative = file_path.relative_to(directory)
            name = str(relative.with_suffix("")).replace(os.sep, "/")
        else:
            name = file_path.stem

        results.append({"name": name, "content": data})

    return results
