from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@router.get("/saved_layouts", tags=["Layouts"])
def get_saved_layouts():
    pass


@router.post("/generate_layout", tags=["Layouts"])
def generate_layout():
    pass
