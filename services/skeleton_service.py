from datetime import datetime, timezone

from exceptions.custom_exceptions import (
    InvalidLayoutError,
    LayoutNotFoundError,
    TemplateNotFoundError,
)
from services.hash_service import hash_layout
from services.ppt_service import generate_ppt
from services.storage_loader import StorageLoader
from utils.logger import logger
from utils.validators import validate_slide_names


class SkeletonService:
    def __init__(self) -> None:
        self.loader = StorageLoader()

    def generate(
        self,
        repository,
        layout_name: str | None = None,
        slides: list[str] | None = None,
    ) -> dict:
        """Generate (or retrieve from cache) a skeleton PPTX.

        Resolution order:
          1. If 'slides' is provided, use it directly.
          2. Else load the slide list from the saved layout YAML for 'layout_name'.
          3. Hash the combination → check MongoDB cache.
          4. Cache miss → merge PPTX templates, persist metadata, return result.

        Args:
            repository:  SkeletonRepository instance for DB access.
            layout_name: Name of a saved layout (without .yaml extension). Optional.
            slides:      Explicit ordered list of slide names. Optional.

        Returns:
            {"cached": bool, "data": {...skeleton metadata...}}
        """
        # --- Resolve slide list ---
        if slides:
            resolved_slides = slides
            resolved_layout_name = layout_name or "custom"
            logger.info(
                f"[SkeletonService] generate → custom slides ({len(resolved_slides)} slides)"
            )
        else:
            if not layout_name:
                raise InvalidLayoutError(
                    "Either 'layout_name' or 'slides' must be provided."
                )

            layout = self.loader.get_layout(layout_name)
            if not layout:
                raise LayoutNotFoundError(layout_name)

            resolved_slides = layout.get("content", [])
            resolved_layout_name = layout_name
            logger.info(f"[SkeletonService] generate → layout='{layout_name}'")

        validate_slide_names(resolved_slides, resolved_layout_name)

        # --- Hash + cache check ---
        skeleton_hash = hash_layout(resolved_layout_name, resolved_slides)
        logger.info(f"[SkeletonService] hash={skeleton_hash[:16]}…")

        existing = repository.find_by_hash(skeleton_hash)
        if existing:
            logger.info("[SkeletonService] cache hit — returning existing skeleton.")
            return {"cached": True, "data": existing}

        # --- Generate new skeleton ---
        try:
            file_path = generate_ppt(skeleton_hash, resolved_slides)
        except FileNotFoundError as exc:
            raise TemplateNotFoundError(str(exc)) from exc

        # --- Persist metadata --- (adding more ?)
        metadata = {
            "skeleton_hash": skeleton_hash,
            "layout_name": resolved_layout_name,
            "slides": resolved_slides,
            "file_path": file_path,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        saved = repository.insert(metadata)
        logger.info(f"[SkeletonService] new skeleton stored → {file_path}")

        return {"cached": False, "data": saved}
