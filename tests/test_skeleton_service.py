from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from exceptions.custom_exceptions import InvalidLayoutError, TemplateNotFoundError
from services.skeleton_service import SkeletonService


@pytest.fixture()
def tmp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Minimal storage structure for SkeletonService tests."""
    (tmp_path / "generated").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def service(tmp_storage: Path) -> SkeletonService:
    return SkeletonService()


@pytest.fixture()
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.find_by_hash.return_value = None  # cache miss by default
    repo.insert.side_effect = lambda data: {**data, "_id": "abc123"}
    return repo


def _make_temp_pptx(tmp_path: Path, content: bytes = b"PK fake pptx") -> str:
    """Create a fake temp PPTX file and return its path string."""
    import uuid
    p = tmp_path / "generated" / f"{uuid.uuid4()}.pptx"
    p.write_bytes(content)
    return str(p)


class TestGenerateWithCustomSlides:
    def test_cache_hit_returns_cached(self, service, mock_repo, tmp_storage):
        cached_doc = {
            "skeleton_hash": "aabbcc",
            "slides": ["Front slide", "Summary"],
            "file_path": "generated/aabbcc.pptx",
            "created_at": "2026-01-01T00:00:00+00:00",
        }
        mock_repo.find_by_hash.return_value = cached_doc

        temp_file = _make_temp_pptx(tmp_storage)
        with (
            patch("services.skeleton_service.generate_ppt", return_value=temp_file),
            patch("services.skeleton_service.hash_pptx_content", return_value="aabbcc"),
        ):
            result = service.generate(repository=mock_repo, slides=["Front slide", "Summary"])

        assert result["cached"] is True
        assert result["data"] == cached_doc

    def test_cache_miss_generates_new_skeleton(self, service, mock_repo, tmp_storage):
        temp_file = _make_temp_pptx(tmp_storage)
        content_hash = "deadbeef" * 8

        with (
            patch("services.skeleton_service.generate_ppt", return_value=temp_file),
            patch("services.skeleton_service.hash_pptx_content", return_value=content_hash),
        ):
            result = service.generate(repository=mock_repo, slides=["Front slide", "Summary"])

        assert result["cached"] is False
        assert result["data"]["skeleton_hash"] == content_hash
        assert result["data"]["slides"] == ["Front slide", "Summary"]
        assert "file_path" in result["data"]
        assert "created_at" in result["data"]

    def test_template_not_found_raises(self, service, mock_repo):
        with (
            patch("services.skeleton_service.generate_ppt", side_effect=FileNotFoundError("missing.pptx")),
        ):
            with pytest.raises(TemplateNotFoundError):
                service.generate(repository=mock_repo, slides=["missing"])

    def test_invalid_slide_entry_raises(self, service, mock_repo):
        with pytest.raises(InvalidLayoutError):
            service.generate(repository=mock_repo, slides=["  "])

    def test_hash_is_deterministic(self, service, mock_repo, tmp_storage):
        """Same slide content → same content hash → same cache key."""
        slides = ["Front slide", "Summary"]
        content_hash = "cafebabe" * 8
        captured_hashes = []

        def capture_insert(data):
            captured_hashes.append(data["skeleton_hash"])
            return {**data, "_id": "abc123"}

        mock_repo.insert.side_effect = capture_insert

        temp1 = _make_temp_pptx(tmp_storage, b"same content")
        with (
            patch("services.skeleton_service.generate_ppt", return_value=temp1),
            patch("services.skeleton_service.hash_pptx_content", return_value=content_hash),
        ):
            service.generate(repository=mock_repo, slides=slides)

        mock_repo.find_by_hash.return_value = None
        temp2 = _make_temp_pptx(tmp_storage, b"same content")
        with (
            patch("services.skeleton_service.generate_ppt", return_value=temp2),
            patch("services.skeleton_service.hash_pptx_content", return_value=content_hash),
        ):
            service.generate(repository=mock_repo, slides=slides)

        assert captured_hashes[0] == captured_hashes[1]

    def test_cache_hit_deletes_temp_file(self, service, mock_repo, tmp_storage):
        """On cache hit the temp file must be deleted."""
        cached_doc = {
            "skeleton_hash": "aabbcc",
            "slides": ["Front slide"],
            "file_path": "generated/aabbcc.pptx",
            "created_at": "2026-01-01T00:00:00+00:00",
        }
        mock_repo.find_by_hash.return_value = cached_doc

        temp_file = _make_temp_pptx(tmp_storage)
        with (
            patch("services.skeleton_service.generate_ppt", return_value=temp_file),
            patch("services.skeleton_service.hash_pptx_content", return_value="aabbcc"),
        ):
            service.generate(repository=mock_repo, slides=["Front slide"])

        from pathlib import Path
        assert not Path(temp_file).exists()
