from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from exceptions.custom_exceptions import (
    InvalidLayoutError,
    LayoutNotFoundError,
    TemplateNotFoundError,
)
from models.request_models import GenerateSkeletonRequest
from repositories.skeleton_repository import SkeletonRepository
from services.skeleton_service import SkeletonService
from services.storage_loader import StorageLoader
from utils.logger import logger

router = APIRouter()
_service = SkeletonService()
_loader = StorageLoader()


@router.get("/saved_layouts", status_code=status.HTTP_200_OK)
def get_saved_layouts() -> dict:
    """Return all available layouts and templates.

    Layouts:   storage/layouts/saved/*.yaml  → [{"name": "...", "content": [...]}, ...]
    Templates: storage/templates/**/*.yaml   → [{"name": "PPG/Front", "content": {...}}, ...]
    """
    try:
        layouts = _loader.get_all_layouts()
        templates = _loader.get_all_templates()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return {"layouts": layouts, "templates": templates}


@router.post("/generate-skeleton", status_code=status.HTTP_200_OK)
def generate_skeleton(body: GenerateSkeletonRequest) -> dict:
    """Generate (or retrieve from cache) a skeleton PPTX.

    Body (at least one field required):
        layout_name (str):   Name of a saved layout — loads its slide list from YAML.
        slides (list[str]):  Custom ordered list of slide names — overrides layout_name.

    Both fields may be sent together; 'slides' takes priority.

    Returns:
        {"cached": bool, "data": {skeleton metadata}}
    """
    logger.info(
        f"POST /generate-skeleton  layout='{body.layout_name}'  "
        f"slides={len(body.slides) if body.slides else None}"
    )

    repo = SkeletonRepository()

    try:
        result = _service.generate(
            repository=repo,
            layout_name=body.layout_name,
            slides=body.slides,
        )
    except LayoutNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except (InvalidLayoutError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error.") from exc

    return result


@router.get("/skeletons/{skeleton_hash}", status_code=status.HTTP_200_OK)
def download_skeleton(skeleton_hash: str) -> FileResponse:
    """Download a generated skeleton PPTX file by its hash.

    Args:
        skeleton_hash: The full SHA-256 hash returned by POST /generate-skeleton.

    Returns:
        The .pptx file as a binary download.
    """
    skeleton_path = Path("generated") / f"{skeleton_hash}.pptx"

    if not skeleton_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skeleton not found for hash: {skeleton_hash}",
        )

    return FileResponse(
        path=str(skeleton_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{skeleton_hash}.pptx",
    )
