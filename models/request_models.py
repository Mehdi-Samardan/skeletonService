from pydantic import BaseModel, field_validator, model_validator


class GenerateSkeletonRequest(BaseModel):
    """Request body for POST /generate-skeleton.

    Accepts either:
      - {"layout_name": "Full report"}           → loads slides from saved layout YAML
      - {"slides": ["Front slide", "Summary"]}   → uses the provided slide list directly
      - {"layout_name": "...", "slides": [...]}  → slides override the saved layout
    """

    layout_name: str | None = None
    slides: list[str] | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "GenerateSkeletonRequest":
        if not self.layout_name and not self.slides:
            raise ValueError("Provide either 'layout_name' or 'slides' (or both).")
        return self

    @field_validator("layout_name", mode="before")
    @classmethod
    def layout_name_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not str(value).strip():
            raise ValueError("layout_name must not be blank.")
        return value.strip() if value else None

    @field_validator("slides", mode="before")
    @classmethod
    def slides_not_empty(cls, value: list | None) -> list | None:
        if value is not None and len(value) == 0:
            raise ValueError("slides list must not be empty.")
        return value
