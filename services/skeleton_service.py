from services.storage_loader import StorageLoader
from services.hash_service import hash_template, hash_skeleton
from services.ppt_service import generate_ppt
from repositories.skeleton_repository import SkeletonRepository


class SkeletonService:
    def __init__(self):
        self.loader = StorageLoader()
        self.repo = SkeletonRepository()

    def generate(self, layout_name: str):

        layout = self.loader.get_layout(layout_name)
        if not layout:
            raise ValueError("Layout not found")

        slide_names = layout.get("content", [])

        template_hashes = []

        for slide_name in slide_names:
            template = self.loader.get_template(slide_name)

            if not template:
                continue

            template_hashes.append(hash_template(template))

        skeleton_hash = hash_skeleton(layout_name, template_hashes)

        existing = self.repo.find_by_hash(skeleton_hash)
        if existing:
            return {"cached": True, "data": existing}

        file_path = generate_ppt(skeleton_hash, slide_names)

        data = {
            "skeleton_hash": skeleton_hash,
            "layout_name": layout_name,
            "template_hashes": template_hashes,
            "file_path": file_path,
        }

        saved = self.repo.insert(data)

        return {"cached": False, "data": saved}
