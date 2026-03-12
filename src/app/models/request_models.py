from pydantic import BaseModel, field_validator


class GenerateSkeletonRequest(BaseModel):
    """Request body for POST /generate-skeleton."""

    slides: list[str]

    @field_validator("slides", mode="before")
    @classmethod
    def slides_not_empty(cls, value: list) -> list:
        if len(value) == 0:
            print("Validation error: slides list is empty. (Must contain at least one slide name.)")
            raise ValueError("slides list must not be empty.")
        return value
