from fastapi import APIRouter, Depends
from repositories.skeleton_repository import SkeletonRepository
from services.skeleton_service import SkeletonService
from utils.yaml_loader import load_all_yaml_from_directory

router = APIRouter()


def get_service() -> SkeletonService:
    repo = SkeletonRepository()
    return SkeletonService(repo)


@router.post("/generate-skeleton/{layout_name}")
def generate_skeleton(
    layout_name: str,
    service: SkeletonService = Depends(get_service),
):
    return service.generate(layout_name)


@router.get("/saved_layouts")
def get_saved_layouts():
    layouts = load_all_yaml_from_directory("storage/layouts/saved")
    templates = load_all_yaml_from_directory("storage/templates")

    return {"layouts": layouts, "templates": templates}
