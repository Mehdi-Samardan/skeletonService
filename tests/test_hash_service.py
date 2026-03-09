import pytest

from app.services.hash_service import hash_pptx_content


class TestHashPptxContent:
    def test_returns_64_char_hex_string(self, tmp_path):
        f = tmp_path / "test.pptx"
        f.write_bytes(b"fake pptx content")
        result = hash_pptx_content(str(f))
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_same_content_same_hash(self, tmp_path):
        f1 = tmp_path / "a.pptx"
        f2 = tmp_path / "b.pptx"
        content = b"identical content"
        f1.write_bytes(content)
        f2.write_bytes(content)
        assert hash_pptx_content(str(f1)) == hash_pptx_content(str(f2))

    def test_different_content_different_hash(self, tmp_path):
        f1 = tmp_path / "a.pptx"
        f2 = tmp_path / "b.pptx"
        f1.write_bytes(b"content A")
        f2.write_bytes(b"content B")
        assert hash_pptx_content(str(f1)) != hash_pptx_content(str(f2))

    def test_empty_file_produces_valid_hash(self, tmp_path):
        f = tmp_path / "empty.pptx"
        f.write_bytes(b"")
        result = hash_pptx_content(str(f))
        assert len(result) == 64

    def test_binary_content_hashed_correctly(self, tmp_path):
        f = tmp_path / "binary.pptx"
        f.write_bytes(bytes(range(256)))
        result = hash_pptx_content(str(f))
        assert len(result) == 64

    def test_single_byte_difference_changes_hash(self, tmp_path):
        f1 = tmp_path / "a.pptx"
        f2 = tmp_path / "b.pptx"
        f1.write_bytes(b"hello world")
        f2.write_bytes(b"hello World")
        assert hash_pptx_content(str(f1)) != hash_pptx_content(str(f2))

    def test_deterministic_across_calls(self, tmp_path):
        f = tmp_path / "test.pptx"
        f.write_bytes(b"some pptx bytes 123")
        h1 = hash_pptx_content(str(f))
        h2 = hash_pptx_content(str(f))
        assert h1 == h2
