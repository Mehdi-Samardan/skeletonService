from pydantic import BaseModel, field_validator


class GenerateSkeletonRequest(BaseModel):
    """Request body for POST /generate-skeleton."""

    layout_name: str

    @field_validator("layout_name")
    @classmethod
    def layout_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("layout_name must not be blank.")
        return value.strip()
