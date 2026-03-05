from pydantic import BaseModel, field_validator


class GenerateSkeletonRequest(BaseModel):
    """Request body for POST /generate-skeleton.

    Accepts only a list of slide names:
      - {"slides": ["Front slide", "Summary"]}
    """

    slides: list[str]

    @field_validator("slides", mode="before")
    @classmethod
    def slides_not_empty(cls, value: list) -> list:
        if len(value) == 0:
            raise ValueError("slides list must not be empty.")
        return value
