# utils/yaml_loader.py

import os
import yaml
from pathlib import Path


def load_yaml_file(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data if data else {}


def load_all_yaml_from_directory(directory_path: str) -> list[dict]:
    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    yaml_files = list(directory.glob("*.yaml"))

    results = []

    for file_path in yaml_files:
        data = load_yaml_file(str(file_path))

        results.append({"name": file_path.stem, "content": data})

    return results
