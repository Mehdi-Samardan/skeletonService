from datetime import datetime, timezone

from exceptions.custom_exceptions import LayoutNotFoundError, TemplateNotFoundError
from services.hash_service import hash_layout
from services.ppt_service import generate_ppt
from services.storage_loader import StorageLoader
from utils.logger import logger
from utils.validators import validate_slide_names


class SkeletonService:
    def __init__(self) -> None:
        self.loader = StorageLoader()

    def generate(self, layout_name: str, repository) -> dict:
        """
        Generate (or retrieve from cache) a skeleton PPTX.

        Flow:
          1. Load slide list from the saved layout YAML.
          2. Validate slide names.
          3. Compute deterministic hash from layout name + slide names.
          4. Check MongoDB — cache hit → return existing record.
          5. Cache miss → merge PPTX templates, save file, persist metadata.

        Args:
            layout_name: Name of a saved layout (without .yaml extension).
            repository:  SkeletonRepository instance for DB access.

        Returns:
            {"cached": bool, "data": {...skeleton metadata...}}
        """
        logger.info(f"[SkeletonService] generate → layout='{layout_name}'")

        layout = self.loader.get_layout(layout_name)
        if not layout:
            raise LayoutNotFoundError(layout_name)

        slide_names: list[str] = layout.get("content", [])
        validate_slide_names(slide_names, layout_name)

        skeleton_hash = hash_layout(layout_name, slide_names)
        logger.info(f"[SkeletonService] hash={skeleton_hash[:16]}…")

        existing = repository.find_by_hash(skeleton_hash)
        if existing:
            logger.info("[SkeletonService] cache hit — returning existing skeleton.")
            return {"cached": True, "data": existing}

        try:
            file_path = generate_ppt(skeleton_hash, slide_names)
        except FileNotFoundError as exc:
            raise TemplateNotFoundError(str(exc)) from exc

        metadata = {
            "skeleton_hash": skeleton_hash,
            "layout_name": layout_name,
            "slides": slide_names,
            "file_path": file_path,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        saved = repository.insert(metadata)
        logger.info(f"[SkeletonService] new skeleton stored → {file_path}")

        return {"cached": False, "data": saved}
