import os
import json


GENERATED_FOLDER = "generated"


def ensure_generated_folder():
    os.makedirs(GENERATED_FOLDER, exist_ok=True)


def save_skeleton_locally(hash_value: str, skeleton: dict) -> str:
    """
    Saves skeleton JSON locally using hash as filename.
    Returns file path.
    """

    ensure_generated_folder()

    file_path = os.path.join(GENERATED_FOLDER, f"{hash_value}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(skeleton, f, indent=2)

    return file_path
