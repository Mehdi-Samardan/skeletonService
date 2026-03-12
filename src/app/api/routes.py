from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.exceptions.custom_exceptions import InvalidLayoutError, TemplateNotFoundError
from app.models.request_models import GenerateSkeletonRequest
from app.repositories.skeleton_repository import SkeletonRepository
from app.services.skeleton_service import SkeletonService
from app.services.storage_loader import StorageLoader
from app.utils.logger import logger

router = APIRouter()
_service = SkeletonService()
_loader = StorageLoader()


@router.get("/saved_layouts", status_code=status.HTTP_200_OK)
def get_saved_layouts() -> dict:
    """Return all available layouts and templates."""
    try:
        layouts = _loader.get_all_layouts()
        templates = _loader.get_all_templates()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    finally:
        logger.info("Getting saved layouts and templates")
    return {"layouts": layouts, "templates": templates}


@router.post("/generate-skeleton", status_code=status.HTTP_200_OK)
def generate_skeleton(body: GenerateSkeletonRequest) -> dict:
    """Generate (or retrieve from cache) a skeleton PPTX."""
    
    print("Starting skeleton generation process...")
    logger.info(f"POST /generate-skeleton  slides={len(body.slides)}")
    repo = SkeletonRepository()

    try:
        result = _service.generate(repository=repo, slides=body.slides)
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
    """Download a generated skeleton PPTX file by its hash."""
    skeleton_path = Path("generated") / f"{skeleton_hash}.pptx"
    if not skeleton_path.exists():
        logger.warning(f"Skeleton not found for hash: {skeleton_hash}, please check the hash and try again.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skeleton not found for hash: {skeleton_hash}"
        )
        

    return FileResponse(
        path=str(skeleton_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{skeleton_hash}.pptx",
    )
