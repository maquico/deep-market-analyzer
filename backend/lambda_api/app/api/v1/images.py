import boto3
import os
import uuid
import datetime
from fastapi import APIRouter, HTTPException
from app.models import Image
from app.dynamo import (
    images_table
)

router = APIRouter()

# Constantes de mensajes de error
ERROR_TABLE_NOT_CONFIGURED = "DynamoDB images table name not configured"
ERROR_GET_DOCUMENTS = "Error al obtener las imágenes"
ERROR_GET_DOCUMENT = "Error al obtener la imagen"
ERROR_CREATE_DOCUMENT = "Error al crear la imagen"
ERROR_DELETE_DOCUMENT = "Error al eliminar la imagen"
MSG_DOCUMENT_DELETED = "Imagen eliminada exitosamente"

@router.get("/chat/{chat_id}", response_model=list[Image], tags=["images"])
def get_images_by_chat(chat_id: str):
    """Obtener documentos por ID de chat"""
    if images_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = images_table.query(
            IndexName="chat_id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id)
        )
        return [Image(**item) for item in response.get("Items", [])]
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)

@router.get('/{image_id}', response_model=Image, tags=["images"])
def get_image_by_id(image_id: str):
    """Get an image by its ID"""
    if images_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = images_table.get_item(
            Key={'image_id': image_id}
        )
        item = response.get("Item")
        if item:
            return Image(**item)
        else:
            raise HTTPException(status_code=404, detail=ERROR_GET_DOCUMENT)
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENT}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENT)
    
@router.get('/user/{user_id}', response_model=list[Image], tags=["images"])
def get_images_by_user(user_id: str):
    """Obtener documentos por ID de usuario"""
    if images_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = images_table.query(
            IndexName="user_id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        return [Image(**item) for item in response.get("Items", [])]
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)