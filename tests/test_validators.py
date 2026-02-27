import pytest

from exceptions.custom_exceptions import InvalidLayoutError
from utils.validators import validate_slide_names


class TestValidateSlideNames:
    def test_valid_list_returns_same_list(self):
        names = ["Front slide", "Summary", "Final sheet"]
        result = validate_slide_names(names)
        assert result == names

    def test_valid_single_element(self):
        result = validate_slide_names(["Front slide"])
        assert result == ["Front slide"]

    def test_not_a_list_raises(self):
        with pytest.raises(InvalidLayoutError, match="must contain a list"):
            validate_slide_names("Front slide")

    def test_dict_raises(self):
        with pytest.raises(InvalidLayoutError, match="must contain a list"):
            validate_slide_names({"slide": "Front slide"})

    def test_none_raises(self):
        with pytest.raises(InvalidLayoutError, match="must contain a list"):
            validate_slide_names(None)

    def test_empty_list_raises(self):
        with pytest.raises(InvalidLayoutError, match="must not be empty"):
            validate_slide_names([])

    def test_blank_string_entry_raises(self):
        with pytest.raises(InvalidLayoutError, match="Entry 1"):
            validate_slide_names(["Front slide", "  ", "Summary"])

    def test_non_string_entry_raises(self):
        with pytest.raises(InvalidLayoutError, match="Entry 0"):
            validate_slide_names([42, "Summary"])

    def test_none_entry_raises(self):
        with pytest.raises(InvalidLayoutError, match="Entry 2"):
            validate_slide_names(["Front slide", "Summary", None])

    def test_layout_name_in_error_message(self):
        with pytest.raises(InvalidLayoutError, match="my_layout"):
            validate_slide_names([], layout_name="my_layout")

    def test_subdirectory_slide_name_valid(self):
        result = validate_slide_names(["PPG/Front", "PPG/NPS motivation"])
        assert result == ["PPG/Front", "PPG/NPS motivation"]
