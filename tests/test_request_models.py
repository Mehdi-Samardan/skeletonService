import pytest
from pydantic import ValidationError

from models.request_models import GenerateSkeletonRequest


class TestGenerateSkeletonRequest:
    def test_slides_only(self):
        req = GenerateSkeletonRequest(slides=["Front slide", "Summary"])
        assert req.slides == ["Front slide", "Summary"]

    def test_no_slides_raises(self):
        with pytest.raises(ValidationError):
            GenerateSkeletonRequest()

    def test_empty_slides_list_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            GenerateSkeletonRequest(slides=[])

    def test_slides_with_subdirectory_name(self):
        req = GenerateSkeletonRequest(slides=["PPG/Front", "PPG/NPS motivation"])
        assert req.slides == ["PPG/Front", "PPG/NPS motivation"]

    def test_single_slide(self):
        req = GenerateSkeletonRequest(slides=["Front slide"])
        assert req.slides == ["Front slide"]

    def test_many_slides(self):
        slides = [f"Slide {i}" for i in range(10)]
        req = GenerateSkeletonRequest(slides=slides)
        assert req.slides == slides
