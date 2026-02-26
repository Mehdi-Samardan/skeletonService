from exceptions.custom_exceptions import InvalidLayoutError


def validate_slide_names(slide_names: object, layout_name: str = "") -> list[str]:
    """Validate that slide_names is a non-empty list of non-blank strings."""
    context = f" (layout: '{layout_name}')" if layout_name else ""

    if not isinstance(slide_names, list):
        raise InvalidLayoutError(
            f"Layout YAML{context} must contain a list of slide names, "
            f"got {type(slide_names).__name__}."
        )

    if not slide_names:
        raise InvalidLayoutError(f"Layout YAML{context} must not be empty.")

    for i, name in enumerate(slide_names):
        if not isinstance(name, str) or not name.strip():
            raise InvalidLayoutError(
                f"Entry {i} in layout{context} must be a non-blank string."
            )

    return slide_names
