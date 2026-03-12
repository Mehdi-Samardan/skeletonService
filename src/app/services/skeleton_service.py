from datetime import datetime, timezone
from pathlib import Path

from app.exceptions.custom_exceptions import TemplateNotFoundError
from app.services.hash_service import hash_pptx_content, hash_slides
from app.services.ppt_service import generate_ppt
from app.utils.logger import logger
from app.utils.validators import validate_slide_names


class SkeletonService:
    def generate(self, repository, slides: list[str]) -> dict:
        """Generate (or retrieve from cache) a skeleton PPTX."""
        validate_slide_names(slides)
        logger.info(f"[SkeletonService] generate → {len(slides)} slides")

        slide_hashes = hash_slides(slides)
        logger.info(f"[SkeletonService] per-slide hashes computed for {len(slides)} slides")

        existing = repository.find_by_slide_hashes(slides, slide_hashes)
        if existing:
            logger.info("[SkeletonService] cache hit — returning existing skeleton.")
            return {"cached": True, "data": existing}

        try:
            temp_path = generate_ppt(slides)
        except FileNotFoundError as exc:
            raise TemplateNotFoundError(str(exc)) from exc

        skeleton_hash = hash_pptx_content(temp_path)
        logger.info(f"[SkeletonService] content_hash={skeleton_hash[:16]}…")

        final_path = Path("generated") / f"{skeleton_hash}.pptx"
        Path(temp_path).rename(final_path)

        metadata = {
            "skeleton_hash": skeleton_hash,
            "slides": slides,
            "slide_hashes": slide_hashes,
            "file_path": str(final_path),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        saved = repository.insert(metadata)
        logger.info(f"[SkeletonService] new skeleton stored → {final_path}")
        print(f"Generated skeleton PPTX saved at: {final_path}")

        return {"cached": False, "data": saved}
