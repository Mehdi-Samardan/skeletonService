from fastapi import APIRouter, Depends

from repositories.skeleton_repository import SkeletonRepository
from services.skeleton_service import SkeletonService
from utils.yaml_loader import load_all_yaml_from_directory
from utils.yaml_loader import load_yaml_file
from utils.hashing import generate_input_hash

router = APIRouter()


# -----------------------------
# Dependency Injection
# -----------------------------
def get_service() -> SkeletonService:
    repo = SkeletonRepository()
    return SkeletonService(repo)


# -----------------------------
# Basic
# -----------------------------
@router.get("/")
def read_root():
    return {"message": "Welcome to the Skeleton Service API!"}


@router.get("/health")
def health_check():
    return {"status": "ok"}


# -----------------------------
# Generate Skeleton
# -----------------------------
@router.post("/generate-skeleton/{layout_name}")
def generate_skeleton(
    layout_name: str, service: SkeletonService = Depends(get_service)
):
    return service.generate(layout_name)


# -----------------------------
# Saved Layouts
# -----------------------------
@router.get("/saved_layouts")
def get_saved_layouts():
    layouts = load_all_yaml_from_directory("storage/layouts/saved")
    templates = load_all_yaml_from_directory("storage/templates")

    return {"layouts": layouts, "templates": templates}


# -----------------------------
# Test Endpoints
# -----------------------------
@router.get("/test-yaml")
def test_yaml():
    return load_yaml_file("storage/layouts/saved/Full report.yaml")


@router.get("/test-hash")
def test_hash():
    return {"hash": generate_input_hash({"test": 1})}


@router.post("/test-insert")
def test_insert():
    repo = SkeletonRepository()

    test_document = {
        "hash": "test_hash_1234",
        "layouts": ["layoutA", "layoutB"],
        "file_path": "/fake/path/skeleton.pptx",
    }

    return repo.insert_layout(test_document)
