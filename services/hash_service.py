import hashlib
import json


def hash_layout(layout_name: str, slide_names: list[str]) -> str:
    """
    Produce a deterministic SHA-256 hash from a layout name and its
    ordered list of slide names.

    Using JSON encoding preserves order, so ["A","B"] != ["B","A"].
    """
    payload = json.dumps({"layout": layout_name, "slides": slide_names}, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()
