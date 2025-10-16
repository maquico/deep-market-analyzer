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
ERROR_TABLE_NOT_CONFIGURED = "DynamoDB messages table name not configured"
ERROR_GET_MESSAGES = "Error al obtener los mensajes"
ERROR_CREATE_MESSAGE = "Error al crear el mensaje"
ERROR_VERIFY_CHAT = "Error al verificar el chat"
ERROR_CHAT_NOT_FOUND = "Chat no encontrado"


@router.get("/chat/{chat_id}", response_model=list[ChatMessage], tags=["messages"])
def get_messages_by_chat(chat_id: str):
    """Obtener todos los mensajes de un chat específico"""
    if messages_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    
    try:
        response = messages_table.query(
            IndexName="chat_id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id)
        )
        messages = [ChatMessage(**msg) for msg in response.get("Items", [])]
        return messages
    except Exception as e:
        print(f"{ERROR_GET_MESSAGES}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_MESSAGES)


@router.post("/", response_model=ChatMessage, tags=["messages"])
def add_new_message(message: ChatMessage):
    """Crear un nuevo mensaje"""
    if messages_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)

    chat_exits = False
    if chats_table:
        try:
            response = chats_table.get_item(Key={"chat_id": message.chat_id})
            item = response.get("Item")
            if item:
                chat_exits = True
        except Exception as e:
            print(f"{ERROR_VERIFY_CHAT}: {e}")
            raise HTTPException(status_code=500, detail=ERROR_VERIFY_CHAT)

    if not chat_exits:
        raise HTTPException(status_code=404, detail=ERROR_CHAT_NOT_FOUND)
    
    message_data = {
        "message_id": str(uuid.uuid4()),
        "chat_id": message.chat_id,
        "created_at": datetime.datetime.now().isoformat(),
        "sender": message.sender,
        "content": message.content
    }
    try:
        messages_table.put_item(Item=message_data)
        return ChatMessage(**message_data)
    except Exception as e:
        print(f"{ERROR_CREATE_MESSAGE}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_CREATE_MESSAGE)
