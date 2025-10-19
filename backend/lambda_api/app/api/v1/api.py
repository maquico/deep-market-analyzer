from fastapi import APIRouter
from app.api.v1 import chats, users, messages, documents, agent, images

# Router principal de v1
api_router = APIRouter(redirect_slashes=False)

# Incluir todas las rutas de v1
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(users.router)
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
