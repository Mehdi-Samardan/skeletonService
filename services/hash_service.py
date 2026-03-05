import hashlib


def hash_pptx_content(file_path: str) -> str:
    """
    Produce a deterministic SHA-256 hash from the binary content of a merged PPTX file.

    Hashing the actual file content means identical skeletons (regardless of
    how they were requested) always resolve to the same cache key.
    """
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
