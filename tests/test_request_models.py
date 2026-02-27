import pytest
from pydantic import ValidationError

from models.request_models import GenerateSkeletonRequest


class TestGenerateSkeletonRequest:
    def test_layout_name_only(self):
        req = GenerateSkeletonRequest(layout_name="Full report")
        assert req.layout_name == "Full report"
        assert req.slides is None

    def test_slides_only(self):
        req = GenerateSkeletonRequest(slides=["Front slide", "Summary"])
        assert req.layout_name is None
        assert req.slides == ["Front slide", "Summary"]

    def test_both_fields(self):
        req = GenerateSkeletonRequest(layout_name="Full report", slides=["Front slide"])
        assert req.layout_name == "Full report"
        assert req.slides == ["Front slide"]

    def test_neither_field_raises(self):
        with pytest.raises(ValidationError, match="Provide either"):
            GenerateSkeletonRequest()

    def test_blank_layout_name_raises(self):
        with pytest.raises(ValidationError):
            GenerateSkeletonRequest(layout_name="   ")

    def test_layout_name_is_stripped(self):
        req = GenerateSkeletonRequest(layout_name="  Full report  ")
        assert req.layout_name == "Full report"

    def test_empty_slides_list_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            GenerateSkeletonRequest(slides=[])

    def test_slides_with_subdirectory_name(self):
        req = GenerateSkeletonRequest(slides=["PPG/Front", "PPG/NPS motivation"])
        assert req.slides == ["PPG/Front", "PPG/NPS motivation"]

    def test_layout_name_none_explicit_with_slides(self):
        req = GenerateSkeletonRequest(layout_name=None, slides=["Front slide"])
        assert req.layout_name is None
        assert req.slides == ["Front slide"]
