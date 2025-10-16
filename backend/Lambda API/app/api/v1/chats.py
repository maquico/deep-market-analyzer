import boto3
import os
import uuid
import datetime
from fastapi import APIRouter, HTTPException
from app.models import Chat, ChatMessage
from app.dynamo import (
    chats_table,
    messages_table
)


router = APIRouter()

# Constantes de mensajes de error
ERROR_TABLE_NOT_CONFIGURED = "DynamoDB chats table name not configured"
ERROR_CHAT_NOT_FOUND = "Chat no encontrado"
ERROR_GET_CHATS = "Error al obtener los chats"
ERROR_GET_CHAT = "Error al obtener el chat"
ERROR_CREATE_CHAT = "Error al crear el chat"
ERROR_DELETE_CHAT = "Error al eliminar el chat"
MSG_CHAT_DELETED = "Chat eliminado exitosamente"


@router.get("/", response_model=list[Chat], tags=["chats"])
def get_chats():
    """Obtener todos los chats (sin mensajes)"""
    if chats_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    
    try:
        response = chats_table.scan()
        # No cargar mensajes aquí, solo los metadatos del chat
        chats = []
        for item in response.get("Items", []):
            # Agregar messages vacío o campo count
            item["messages"] = []
            chats.append(Chat(**item))
        return chats
    except Exception as e:
        print(f"{ERROR_GET_CHATS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_CHATS)
    
@router.get("/{chat_id}", response_model=Chat, tags=["chats"])
def get_chat(chat_id: str):
    """Obtener un chat por su ID"""
    if chats_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = chats_table.get_item(Key={"chat_id": chat_id})
        item = response.get("Item")
        if item:
            if messages_table:
                msg_response = messages_table.query(
                    IndexName="chat_id-index",
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id)
                )
                messages = [ChatMessage(**msg) for msg in msg_response.get("Items", [])]
                item["messages"] = messages
            return Chat(**item)
        raise HTTPException(status_code=404, detail=ERROR_CHAT_NOT_FOUND)
    except HTTPException:
        raise
    except Exception as e:
        print(f"{ERROR_GET_CHAT}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_CHAT)
    
@router.get("/user/{user_id}", response_model=list[Chat], tags=["chats"])
def get_chats_by_user(user_id: str):
    """Obtener todos los chats de un usuario específico (sin mensajes)"""
    if chats_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    
    try:
        response = chats_table.query(
            IndexName="user_id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        chats = []
        for item in response.get("Items", []):
            # No cargar mensajes aquí, solo los metadatos del chat
            item["messages"] = []
            chats.append(Chat(**item))
        return chats
    except Exception as e:
        print(f"{ERROR_GET_CHATS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_CHATS)

@router.post("/", response_model=Chat, tags=["chats"])
def create_chat(chat_name: str, user_id: str):
    if chats_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)

    chat_id = str(uuid.uuid4())
    chat = {
        "chat_id": chat_id,
        "chat_name": chat_name,
        "user_id": user_id,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    try:
        chats_table.put_item(Item=chat)
        return Chat(**chat)
    except Exception as e:
        print(f"{ERROR_CREATE_CHAT}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_CREATE_CHAT)
    
@router.delete("/{chat_id}", tags=["chats"])
def delete_chat(chat_id: str):
    if chats_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        chats_table.delete_item(Key={"chat_id": chat_id})
        return {"message": MSG_CHAT_DELETED}
    except Exception as e:
        print(f"{ERROR_DELETE_CHAT}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_DELETE_CHAT)
    

