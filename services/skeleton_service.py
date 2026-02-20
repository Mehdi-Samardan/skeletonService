# services/skeleton_service.py

from utils.hashing import generate_input_hash
from utils.logger import logger


class SkeletonService:
    def __init__(self, repository):
        self.repository = repository

    def generate(self, layouts: list[str], templates: list[str]) -> dict:
        """
        Main orchestration method for skeleton generation.
        """

        if not layouts:
            raise ValueError("Layouts list cannot be empty.")

        # 1️⃣ Input Hash üret
        input_hash = generate_input_hash(layouts, templates)

        logger.info(f"Generated input hash: {input_hash}")

        # 2️⃣ Cache kontrol
        existing = self.repository.get_by_hash(input_hash)

        if existing:
            logger.info("Skeleton found in cache.")
            return {"cached": True, "data": existing}

        # 3️⃣ Skeleton üretim (şimdilik stub)
        file_path = f"/generated/{input_hash}.pptx"

        metadata = {
            "hash": input_hash,
            "layouts": layouts,
            "templates": templates,
            "file_path": file_path,
        }

        # 4️⃣ Mongo’ya kaydet
        saved = self.repository.insert_layout(metadata)

        logger.info("New skeleton generated and stored.")

        return {"cached": False, "data": saved}
