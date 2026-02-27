"""Integration tests for the FastAPI routes.

All MongoDB calls and PPTX generation are mocked so tests run
without any external dependencies.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch MongoDB connection before importing the app
with patch("database.connect_to_mongo"), patch("database.close_mongo_connection"):
    from main import app

client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_repo(cached_doc=None, insert_result=None):
    repo = MagicMock()
    repo.find_by_hash.return_value = cached_doc
    if insert_result is None:
        insert_result = {
            "skeleton_hash": "abc123def456",
            "layout_name": "One pager",
            "slides": ["One pager - front - cohort - coverage", "One pager - back - revenue"],
            "file_path": "storage/layouts/skeletons/abc123def456.pptx",
            "created_at": "2026-01-01T00:00:00+00:00",
            "_id": "507f1f77bcf86cd799439011",
        }
    repo.insert.return_value = insert_result
    return repo


# ---------------------------------------------------------------------------
# GET /saved_layouts
# ---------------------------------------------------------------------------

class TestGetSavedLayouts:
    def test_returns_200(self):
        with patch("api.routes._loader") as mock_loader:
            mock_loader.get_all_layouts.return_value = [
                {"name": "One pager", "content": ["One pager - front - cohort - coverage"]}
            ]
            mock_loader.get_all_templates.return_value = [
                {"name": "Final sheet", "content": {"Texts": {}}}
            ]
            response = client.get("/saved_layouts")

        assert response.status_code == 200

    def test_response_has_layouts_and_templates_keys(self):
        with patch("api.routes._loader") as mock_loader:
            mock_loader.get_all_layouts.return_value = []
            mock_loader.get_all_templates.return_value = []
            response = client.get("/saved_layouts")

        body = response.json()
        assert "layouts" in body
        assert "templates" in body

    def test_layouts_is_list(self):
        with patch("api.routes._loader") as mock_loader:
            mock_loader.get_all_layouts.return_value = [
                {"name": "One pager", "content": ["slide1"]}
            ]
            mock_loader.get_all_templates.return_value = []
            response = client.get("/saved_layouts")

        assert isinstance(response.json()["layouts"], list)

    def test_file_not_found_returns_500(self):
        with patch("api.routes._loader") as mock_loader:
            mock_loader.get_all_layouts.side_effect = FileNotFoundError("missing dir")
            response = client.get("/saved_layouts")

        assert response.status_code == 500


# ---------------------------------------------------------------------------
# POST /generate-skeleton
# ---------------------------------------------------------------------------

class TestGenerateSkeleton:
    def test_with_layout_name_returns_200(self):
        doc = {
            "skeleton_hash": "aabbccdd",
            "layout_name": "One pager",
            "slides": ["slide1"],
            "file_path": "storage/layouts/skeletons/aabbccdd.pptx",
            "created_at": "2026-01-01T00:00:00+00:00",
            "_id": "id1",
        }
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.return_value = {"cached": False, "data": doc}
            response = client.post("/generate-skeleton", json={"layout_name": "One pager"})

        assert response.status_code == 200

    def test_with_custom_slides_returns_200(self):
        doc = {
            "skeleton_hash": "xxyyzz",
            "layout_name": "custom",
            "slides": ["Front slide", "Summary"],
            "file_path": "storage/layouts/skeletons/xxyyzz.pptx",
            "created_at": "2026-01-01T00:00:00+00:00",
            "_id": "id2",
        }
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.return_value = {"cached": False, "data": doc}
            response = client.post(
                "/generate-skeleton",
                json={"slides": ["Front slide", "Summary"]},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["slides"] == ["Front slide", "Summary"]

    def test_response_has_cached_and_data_fields(self):
        doc = {"skeleton_hash": "h", "layout_name": "l", "slides": [], "file_path": "f", "created_at": "d", "_id": "i"}
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.return_value = {"cached": True, "data": doc}
            response = client.post("/generate-skeleton", json={"layout_name": "One pager"})

        body = response.json()
        assert "cached" in body
        assert "data" in body

    def test_cache_hit_returns_cached_true(self):
        doc = {"skeleton_hash": "h", "layout_name": "l", "slides": [], "file_path": "f", "created_at": "d", "_id": "i"}
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.return_value = {"cached": True, "data": doc}
            response = client.post("/generate-skeleton", json={"layout_name": "One pager"})

        assert response.json()["cached"] is True

    def test_no_fields_returns_422(self):
        response = client.post("/generate-skeleton", json={})
        assert response.status_code == 422

    def test_blank_layout_name_returns_422(self):
        response = client.post("/generate-skeleton", json={"layout_name": "   "})
        assert response.status_code == 422

    def test_empty_slides_list_returns_422(self):
        response = client.post("/generate-skeleton", json={"slides": []})
        assert response.status_code == 422

    def test_layout_not_found_returns_404(self):
        from exceptions.custom_exceptions import LayoutNotFoundError
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.side_effect = LayoutNotFoundError("missing layout")
            response = client.post("/generate-skeleton", json={"layout_name": "missing layout"})

        assert response.status_code == 404

    def test_template_not_found_returns_422(self):
        from exceptions.custom_exceptions import TemplateNotFoundError
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.side_effect = TemplateNotFoundError("missing.pptx")
            response = client.post("/generate-skeleton", json={"layout_name": "One pager"})

        assert response.status_code == 422

    def test_unexpected_error_returns_500(self):
        with (
            patch("api.routes._service") as mock_svc,
            patch("api.routes.SkeletonRepository"),
        ):
            mock_svc.generate.side_effect = RuntimeError("something broke")
            response = client.post("/generate-skeleton", json={"layout_name": "One pager"})

        assert response.status_code == 500


# ---------------------------------------------------------------------------
# GET /skeletons/{hash}
# ---------------------------------------------------------------------------

class TestDownloadSkeleton:
    def test_existing_skeleton_returns_200(self, tmp_path):
        skeleton_hash = "abc123"
        skeleton_file = tmp_path / f"{skeleton_hash}.pptx"
        skeleton_file.write_bytes(b"PK fake pptx content")

        generated_dir = Path("generated")
        generated_dir.mkdir(parents=True, exist_ok=True)
        real_skeleton = generated_dir / f"{skeleton_hash}.pptx"
        real_skeleton.write_bytes(b"PK fake pptx content")
        response = client.get(f"/skeletons/{skeleton_hash}")
        real_skeleton.unlink(missing_ok=True)

        assert response.status_code == 200

    def test_missing_skeleton_returns_404(self):
        response = client.get("/skeletons/0000000000000000000000000000000000000000000000000000000000000000")
        assert response.status_code == 404

    def test_response_content_type_is_pptx(self, tmp_path):
        skeleton_hash = "deadbeef01"
        generated_dir = Path("generated")
        generated_dir.mkdir(parents=True, exist_ok=True)
        real_skeleton = generated_dir / f"{skeleton_hash}.pptx"
        real_skeleton.write_bytes(b"PK fake pptx content")

        response = client.get(f"/skeletons/{skeleton_hash}")
        real_skeleton.unlink(missing_ok=True)

        assert response.status_code == 200
        assert "presentationml" in response.headers["content-type"]
