import hashlib
from pathlib import Path

TEMPLATE_DIR = Path("storage/templates")


def hash_slide(slide_name: str) -> str:
    """Compute SHA-256 hash of an individual slide template PPTX binary."""
    path = TEMPLATE_DIR / f"{slide_name}.pptx"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def hash_slides(slide_names: list[str]) -> dict[str, str]:
    """Return a dict mapping each slide name to its SHA-256 hash."""
    return {name: hash_slide(name) for name in slide_names}


def hash_pptx_content(file_path: str) -> str:
    """
    Produce a deterministic SHA-256 hash from the binary content of a merged PPTX file.

    Hashing the actual file content means identical skeletons (regardless of
    how they were requested) always resolve to the same cache key.
    """
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
