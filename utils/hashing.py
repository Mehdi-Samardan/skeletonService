import hashlib
import json


def generate_input_hash(data: dict) -> str:
    """
    Generates deterministic SHA256 hash from dictionary input.
    Ensures consistent ordering.
    """

    normalized = json.dumps(data, sort_keys=True)

    return hashlib.sha256(normalized.encode()).hexdigest()
