from utils.yaml_loader import load_yaml_file
from services.pptx_builder import merge_pptx
from utils.logger import logger


class SkeletonService:
    def __init__(self, repository):
        self.repository = repository

    def generate(self, layout_name: str) -> dict:

        logger.info(f"Generating skeleton for: {layout_name}")

        layout_path = f"storage/layouts/saved/{layout_name}.yaml"
        slide_names = load_yaml_file(layout_path)

        if not isinstance(slide_names, list):
            raise ValueError("Layout YAML must be a list.")

        # Merge
        file_path, file_hash = merge_pptx(slide_names)

        # Cache kontrol
        existing = self.repository.get_by_hash(file_hash)
        if existing:
            return {"cached": True, "data": existing}

        metadata = {
            "hash": file_hash,
            "layout_name": layout_name,
            "file_path": file_path,
        }

        saved = self.repository.insert_layout(metadata)

        return {"cached": False, "data": saved}
