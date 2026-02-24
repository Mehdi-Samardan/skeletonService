from utils.hashing import generate_input_hash
from utils.logger import logger
from utils.yaml_loader import load_yaml_file
from datetime import datetime
from utils.local_storage import save_skeleton_locally
from services.pptx_builder import build_pptx_from_skeleton


class SkeletonService:
    def __init__(self, repository):
        self.repository = repository

    # -----------------------------
    # Build skeleton from layout YAML
    # -----------------------------
    def build_skeleton(self, layout_content: list) -> dict:
        """
        Converts layout YAML (list of slide names)
        into structured skeleton JSON.
        """

        if not isinstance(layout_content, list):
            raise ValueError("Layout YAML must be a list of slide names.")

        slides = []

        for index, slide_name in enumerate(layout_content, start=1):
            slides.append(
                {
                    "order": index,
                    "slide_name": slide_name,
                    "template": None,  # template mapping next phase
                }
            )

        return {"slides": slides}

    # -----------------------------
    # Main generation method
    # -----------------------------
    def generate(self, layout_name: str) -> dict:
        """
        Main orchestration method.
        """

        layout_data = load_yaml_file(f"storage/layouts/saved/{layout_name}.yaml")

        skeleton = self.build_skeleton(layout_data)

        skeleton_hash = generate_input_hash(skeleton)

        logger.info(f"Generated skeleton hash: {skeleton_hash}")

        existing = self.repository.get_by_hash(skeleton_hash)
        if existing:
            logger.info("Skeleton found in cache.")
            return {"cached": True, "data": existing}

        pptx_path = build_pptx_from_skeleton(skeleton_hash, skeleton)

        metadata = {
            "hash": skeleton_hash,
            "layout_name": layout_name,
            "file_path": pptx_path,
            "skeleton": skeleton,
            "created_at": datetime.utcnow().isoformat(),
        }

        # 6️⃣ Save to Mongo
        saved = self.repository.insert_layout(metadata)

        logger.info("New skeleton generated and stored.")

        return {"cached": False, "data": saved}
