from fastapi import APIRouter
from app.api.v1 import chats, users, messages, documents

# Router principal de v1
api_router = APIRouter()

# Incluir todas las rutas de v1
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])