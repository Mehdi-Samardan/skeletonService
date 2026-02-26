import hashlib
import json


def hash_template(template: dict) -> str:
    raw = json.dumps(template, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def hash_skeleton(layout_name: str, template_hashes: list[str]) -> str:
    combined = layout_name + "".join(template_hashes)
    return hashlib.sha256(combined.encode()).hexdigest()
