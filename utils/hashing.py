import hashlib


def generate_input_hash(layouts: list[str], templates: list[str]) -> str:
    """
    Generate deterministic SHA256 hash based on layouts and templates.
    """

    # 1️⃣ Normalize
    normalized_layouts = sorted(layouts)
    normalized_templates = sorted(templates)

    # 2️⃣ Tek string oluştur
    combined_string = (
        "LAYOUTS:"
        + "|".join(normalized_layouts)
        + "::TEMPLATES:"
        + "|".join(normalized_templates)
    )

    # 3️⃣ Encode
    encoded = combined_string.encode("utf-8")

    # 4️⃣ Hash üret
    hash_object = hashlib.sha256(encoded)

    # 5️⃣ Hex format
    return hash_object.hexdigest()
