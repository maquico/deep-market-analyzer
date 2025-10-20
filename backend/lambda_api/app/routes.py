from fastapi import APIRouter
from app.models import Item

router = APIRouter()

@router.get("/items")
async def get_items():
    return {"items": []}

@router.post("/items")
async def create_item(item: Item):
    return {"item": item, "message": "Item creado exitosamente"}
