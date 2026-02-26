# api/routes.py

from fastapi import APIRouter
from services.storage_loader import StorageLoader

router = APIRouter()
loader = StorageLoader()


@router.get("/saved_layouts")
def list_saved_layouts():
    layouts = loader.list_saved_layouts()

    return {"layouts": [{"name": layout["name"]} for layout in layouts]}


@router.get("/saved_layouts/{template_name}")
def get_template(template_name: str):
    data = loader.load_template_yaml(template_name)

    return {"name": template_name, "content": data}
