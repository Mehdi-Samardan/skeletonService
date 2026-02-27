import os
import tempfile
from pathlib import Path

import pytest
import yaml

from services.storage_loader import StorageLoader


@pytest.fixture()
def tmp_storage(tmp_path: Path) -> Path:
    """Create a minimal temporary storage directory structure."""
    layouts_dir = tmp_path / "storage" / "layouts" / "saved"
    templates_dir = tmp_path / "storage" / "templates"
    ppg_dir = templates_dir / "PPG"
    layouts_dir.mkdir(parents=True)
    ppg_dir.mkdir(parents=True)

    # Saved layouts
    (layouts_dir / "Full report.yaml").write_text(
        yaml.dump(["Front slide", "Summary", "Final sheet"]), encoding="utf-8"
    )
    (layouts_dir / "One pager.yaml").write_text(
        yaml.dump(["One pager - front - cohort - coverage", "One pager - back - revenue"]),
        encoding="utf-8",
    )

    # Root-level template
    (templates_dir / "Final sheet.yaml").write_text(
        yaml.dump({"Texts": {"title": {"English": "Final", "Dutch": "Einde"}}}),
        encoding="utf-8",
    )

    # Subdirectory template
    (ppg_dir / "Front.yaml").write_text(
        yaml.dump({"Texts": {"title": {"English": "PPG Front"}}}),
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def loader(tmp_storage: Path, monkeypatch: pytest.MonkeyPatch) -> StorageLoader:
    """Return a StorageLoader pointing at the tmp storage."""
    monkeypatch.chdir(tmp_storage)
    return StorageLoader()


class TestGetAllLayouts:
    def test_returns_list(self, loader: StorageLoader):
        result = loader.get_all_layouts()
        assert isinstance(result, list)

    def test_returns_two_layouts(self, loader: StorageLoader):
        result = loader.get_all_layouts()
        assert len(result) == 2

    def test_layout_has_name_and_content(self, loader: StorageLoader):
        result = loader.get_all_layouts()
        for item in result:
            assert "name" in item
            assert "content" in item

    def test_full_report_content_is_list(self, loader: StorageLoader):
        result = loader.get_all_layouts()
        full = next(r for r in result if r["name"] == "Full report")
        assert isinstance(full["content"], list)
        assert "Front slide" in full["content"]


class TestGetLayout:
    def test_existing_layout_returns_dict(self, loader: StorageLoader):
        result = loader.get_layout("Full report")
        assert result is not None
        assert result["name"] == "Full report"
        assert isinstance(result["content"], list)

    def test_missing_layout_returns_none(self, loader: StorageLoader):
        result = loader.get_layout("Nonexistent layout")
        assert result is None

    def test_one_pager_has_two_slides(self, loader: StorageLoader):
        result = loader.get_layout("One pager")
        assert len(result["content"]) == 2


class TestGetAllTemplates:
    def test_returns_list(self, loader: StorageLoader):
        result = loader.get_all_templates()
        assert isinstance(result, list)

    def test_includes_root_template(self, loader: StorageLoader):
        result = loader.get_all_templates()
        names = [t["name"] for t in result]
        assert "Final sheet" in names

    def test_includes_subdirectory_template(self, loader: StorageLoader):
        result = loader.get_all_templates()
        names = [t["name"] for t in result]
        assert "PPG/Front" in names

    def test_template_has_content(self, loader: StorageLoader):
        result = loader.get_all_templates()
        final = next(t for t in result if t["name"] == "Final sheet")
        assert "Texts" in final["content"]


class TestGetTemplate:
    def test_existing_template_returns_content(self, loader: StorageLoader):
        result = loader.get_template("Final sheet")
        assert result is not None
        assert "Texts" in result

    def test_missing_template_returns_none(self, loader: StorageLoader):
        result = loader.get_template("Does not exist")
        assert result is None
