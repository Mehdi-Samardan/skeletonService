from fastapi import APIRouter
from repositories.skeleton_repository import SkeletonRepository

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Welcome to the Skeleton Service API!"}


@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@router.get("/saved_layouts", tags=["Layouts"])
def get_saved_layouts():
    pass


@router.post("/generate_layout", tags=["Layouts"])
def generate_layout():
    pass


@router.post("/test-insert")
def test_insert():
    repo = SkeletonRepository()

    test_document = {
        "hash": "test_hash_123",
        "layouts": ["layoutA", "layoutB"],
        "file_path": "/fake/path/skeleton.pptx",
    }

    result = repo.insert_layout(test_document)

    return result
