import os
from datetime import datetime, timezone
from pathlib import Path

from exceptions.custom_exceptions import (
    InvalidLayoutError,
    TemplateNotFoundError,
)
from services.hash_service import hash_pptx_content
from services.ppt_service import generate_ppt
from utils.logger import logger
from utils.validators import validate_slide_names


class SkeletonService:
    def generate(
        self,
        repository,
        slides: list[str],
    ) -> dict:
        """Generate (or retrieve from cache) a skeleton PPTX.

        Flow:
          1. Validate the slide list.
          2. Merge PPTX templates into a temporary file via GroupDocs.
          3. Hash the binary content of the merged file.
          4. Check MongoDB cache by content hash.
          5. Cache hit  → delete temp file, return existing record.
          6. Cache miss → move temp file to generated/{hash}.pptx, persist metadata.

        Args:
            repository: SkeletonRepository instance for DB access.
            slides:     Ordered list of slide names to merge.

        Returns:
            {"cached": bool, "data": {...skeleton metadata...}}
        """
        validate_slide_names(slides)
        logger.info(f"[SkeletonService] generate → {len(slides)} slides")

        # --- Generate merged PPTX to a temp location ---
        try:
            temp_path = generate_ppt(slides)
        except FileNotFoundError as exc:
            raise TemplateNotFoundError(str(exc)) from exc

        # --- Hash the binary content of the merged skeleton ---
        skeleton_hash = hash_pptx_content(temp_path)
        logger.info(f"[SkeletonService] content_hash={skeleton_hash[:16]}…")

        # --- Cache check ---
        existing = repository.find_by_hash(skeleton_hash)
        if existing:
            logger.info("[SkeletonService] cache hit — returning existing skeleton.")
            os.remove(temp_path)
            return {"cached": True, "data": existing}

        # --- Move temp file to final hash-named location ---
        final_path = Path("generated") / f"{skeleton_hash}.pptx"
        Path(temp_path).rename(final_path)

        # --- Persist metadata ---
        metadata = {
            "skeleton_hash": skeleton_hash,
            "slides": slides,
            "file_path": str(final_path),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        saved = repository.insert(metadata)
        logger.info(f"[SkeletonService] new skeleton stored → {final_path}")

        return {"cached": False, "data": saved}
