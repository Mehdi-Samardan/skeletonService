import hashlib

# TODO: Testintg somr combination of hashing the slide names + the file content, to avoid edge cases where different slide combinations produce the same skeleton hash (e.g. if two different slide combinations coincidentally produce the same merged PPTX binary content, which is unlikely but possible).


def hash_pptx_content(file_path: str) -> str:
    """
    Produce a deterministic SHA-256 hash from the binary content of a merged PPTX file.

    Hashing the actual file content means identical skeletons (regardless of
    how they were requested) always resolve to the same cache key.
    """
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
