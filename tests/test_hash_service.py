import pytest

from services.hash_service import hash_layout


class TestHashLayout:
    def test_returns_64_char_hex_string(self):
        result = hash_layout("Full report", ["Front slide", "Summary"])
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_input_same_hash(self):
        h1 = hash_layout("Full report", ["Front slide", "Summary"])
        h2 = hash_layout("Full report", ["Front slide", "Summary"])
        assert h1 == h2

    def test_different_layout_name_different_hash(self):
        h1 = hash_layout("Full report", ["Front slide"])
        h2 = hash_layout("One pager", ["Front slide"])
        assert h1 != h2

    def test_different_slides_different_hash(self):
        h1 = hash_layout("Full report", ["Front slide", "Summary"])
        h2 = hash_layout("Full report", ["Summary", "Front slide"])
        assert h1 != h2

    def test_slide_order_matters(self):
        """["A","B"] must not equal ["B","A"]."""
        h1 = hash_layout("layout", ["A", "B", "C"])
        h2 = hash_layout("layout", ["C", "B", "A"])
        assert h1 != h2

    def test_empty_slides_different_from_nonempty(self):
        h1 = hash_layout("layout", [])
        h2 = hash_layout("layout", ["slide"])
        assert h1 != h2

    def test_unicode_slide_names(self):
        result = hash_layout("rapport", ["Voorkant", "Samenvatting"])
        assert len(result) == 64

    def test_single_slide(self):
        result = hash_layout("One pager", ["Final sheet"])
        assert len(result) == 64
