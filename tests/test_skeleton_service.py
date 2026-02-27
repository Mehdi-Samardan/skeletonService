from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from exceptions.custom_exceptions import InvalidLayoutError, LayoutNotFoundError, TemplateNotFoundError
from services.skeleton_service import SkeletonService


@pytest.fixture()
def tmp_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Minimal storage structure for SkeletonService tests."""
    layouts_dir = tmp_path / "storage" / "layouts" / "saved"
    skeletons_dir = tmp_path / "storage" / "layouts" / "skeletons"
    templates_dir = tmp_path / "storage" / "templates"
    layouts_dir.mkdir(parents=True)
    skeletons_dir.mkdir(parents=True)
    templates_dir.mkdir(parents=True)

    (layouts_dir / "One pager.yaml").write_text(
        yaml.dump(["One pager - front - cohort - coverage", "One pager - back - revenue"]),
        encoding="utf-8",
    )

    # Minimal PPTX stubs — pptx library needs valid files; we patch generate_ppt instead.
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


class TestGenerateWithLayoutName:
    def test_cache_hit_returns_cached(self, service, mock_repo):
        cached_doc = {
            "skeleton_hash": "aabbcc",
            "layout_name": "One pager",
            "slides": ["One pager - front - cohort - coverage", "One pager - back - revenue"],
            "file_path": "storage/layouts/skeletons/aabbcc.pptx",
            "created_at": "2026-01-01T00:00:00+00:00",
        }
        mock_repo.find_by_hash.return_value = cached_doc

        with patch("services.skeleton_service.generate_ppt") as mock_gen:
            result = service.generate(repository=mock_repo, layout_name="One pager")

        assert result["cached"] is True
        assert result["data"] == cached_doc
        mock_gen.assert_not_called()

    def test_cache_miss_generates_new_skeleton(self, service, mock_repo):
        with patch("services.skeleton_service.generate_ppt", return_value="storage/layouts/skeletons/xyz.pptx"):
            result = service.generate(repository=mock_repo, layout_name="One pager")

        assert result["cached"] is False
        assert result["data"]["layout_name"] == "One pager"
        assert "skeleton_hash" in result["data"]
        assert "file_path" in result["data"]
        assert "created_at" in result["data"]

    def test_missing_layout_raises(self, service, mock_repo):
        with pytest.raises(LayoutNotFoundError, match="nonexistent"):
            service.generate(repository=mock_repo, layout_name="nonexistent")

    def test_template_not_found_raises(self, service, mock_repo):
        with patch("services.skeleton_service.generate_ppt", side_effect=FileNotFoundError("missing.pptx")):
            with pytest.raises(TemplateNotFoundError):
                service.generate(repository=mock_repo, layout_name="One pager")


class TestGenerateWithCustomSlides:
    def test_custom_slides_used_directly(self, service, mock_repo):
        slides = ["Front slide", "Summary"]
        with patch("services.skeleton_service.generate_ppt", return_value="storage/layouts/skeletons/abc.pptx"):
            result = service.generate(repository=mock_repo, slides=slides)

        assert result["cached"] is False
        assert result["data"]["slides"] == slides
        assert result["data"]["layout_name"] == "custom"

    def test_custom_slides_with_layout_name(self, service, mock_repo):
        """When both are provided, slides take priority but layout_name is preserved."""
        slides = ["Front slide"]
        with patch("services.skeleton_service.generate_ppt", return_value="storage/layouts/skeletons/abc.pptx"):
            result = service.generate(
                repository=mock_repo,
                layout_name="One pager",
                slides=slides,
            )

        assert result["data"]["layout_name"] == "One pager"
        assert result["data"]["slides"] == slides

    def test_invalid_slide_entry_raises(self, service, mock_repo):
        with pytest.raises(InvalidLayoutError):
            service.generate(repository=mock_repo, slides=["  "])

    def test_no_args_raises(self, service, mock_repo):
        with pytest.raises(InvalidLayoutError, match="Either"):
            service.generate(repository=mock_repo)

    def test_hash_is_deterministic(self, service, mock_repo):
        slides = ["Front slide", "Summary"]
        call_hashes = []

        def capture_insert(data):
            call_hashes.append(data["skeleton_hash"])
            return {**data, "_id": "abc123"}

        mock_repo.insert.side_effect = capture_insert

        with patch("services.skeleton_service.generate_ppt", return_value="path.pptx"):
            service.generate(repository=mock_repo, slides=slides)

        mock_repo.find_by_hash.return_value = None
        with patch("services.skeleton_service.generate_ppt", return_value="path.pptx"):
            service.generate(repository=mock_repo, slides=slides)

        assert call_hashes[0] == call_hashes[1]
