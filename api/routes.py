from fastapi import APIRouter, Depends

from repositories.skeleton_repository import SkeletonRepository
from services.skeleton_service import SkeletonService
from models.request_models import SkeletonRequest
from utils.yaml_loader import load_all_yaml_from_directory

from utils.yaml_loader import load_yaml_file
from utils.hashing import generate_input_hash

router = APIRouter()


# Dependency Injection
def get_service() -> SkeletonService:
    repo = SkeletonRepository()
    return SkeletonService(repo)


@router.get("/")
def read_root():
    return {"message": "Welcome to the Skeleton Service API!"}


@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@router.post("/generate_layout", tags=["Layouts"])
def generate_layout():
    return {"message": "Not implemented yet"}


@router.post("/test-insert")
def test_insert():
    repo = SkeletonRepository()

    test_document = {
        "hash": "test_hash_1234",
        "layouts": ["layoutA", "layoutB"],
        "file_path": "/fake/path/skeleton.pptx",
    }

    result = repo.insert_layout(test_document)

    return result


@router.get("/test-yaml")
def test_yaml():
    data = load_yaml_file("storage/layouts/saved/Full report.yaml")
    return data


@router.get("/test-hash")
def test_hash():
    return {"hash": generate_input_hash(["B", "A"], ["T1", "T2"])}


@router.post("/generate-skeleton")
def generate_skeleton(
    request: SkeletonRequest, service: SkeletonService = Depends(get_service)
):
    return service.generate(layouts=request.layouts, templates=request.templates)


@router.get("/saved_layouts")
def get_saved_layouts():
    layouts = load_all_yaml_from_directory("storage/layouts/saved")
    templates = load_all_yaml_from_directory("storage/templates")

    return {"layouts": layouts, "templates": templates}
