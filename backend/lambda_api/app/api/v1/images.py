import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models import Image
from app.dynamo import (
    images_table
)

router = APIRouter()

# Cliente S3 para generar presigned URLs
s3_client = boto3.client('s3')
PRESIGNED_URL_EXPIRATION = 3600  # 1 hora


def generate_presigned_url(s3_bucket: str, s3_key: str) -> Optional[str]:
    """Genera un presigned URL para una imagen en S3"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket, 'Key': s3_key},
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        # print(f"Presigned URL generado para {s3_key}: {url}")
        return url
    except Exception as e:
        print(f"Error generando presigned URL: {e}")
        return None


def add_presigned_url_to_image(image_dict: dict) -> dict:
    """Agrega un presigned URL fresco a la imagen"""
    if image_dict.get('s3_bucket') and image_dict.get('s3_key'):
        presigned_url = generate_presigned_url(
            image_dict['s3_bucket'], 
            image_dict['s3_key']
        )
        if presigned_url:
            image_dict['image_presigned_url'] = presigned_url
    return image_dict

# Constantes de mensajes de error
ERROR_TABLE_NOT_CONFIGURED = "DynamoDB images table name not configured"
ERROR_GET_DOCUMENTS = "Error al obtener las imágenes"
ERROR_GET_DOCUMENT = "Error al obtener la imagen"
ERROR_CREATE_DOCUMENT = "Error al crear la imagen"
ERROR_DELETE_DOCUMENT = "Error al eliminar la imagen"
MSG_DOCUMENT_DELETED = "Imagen eliminada exitosamente"

@router.get("/chat/{chat_id}", response_model=list[Image], tags=["images"])
def get_images_by_chat(chat_id: str):
    """Obtener imágenes por ID de chat"""
    if images_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = images_table.query(
            IndexName="chat_id-index",
            KeyConditionExpression=Key('chat_id').eq(chat_id)
        )
        images = []
        for item in response.get("Items", []):
            # Generar presigned URL fresco para cada imagen
            item = add_presigned_url_to_image(item)
            images.append(Image(**item))
        return images
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)

@router.get('/{image_id}', response_model=Image, tags=["images"])
def get_image_by_id(image_id: str):
    """Obtener una imagen por su ID"""
    if images_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = images_table.get_item(
            Key={'image_id': image_id}
        )
        item = response.get("Item")
        if item:
            # Generar presigned URL fresco
            item = add_presigned_url_to_image(item)
            return Image(**item)
        else:
            raise HTTPException(status_code=404, detail=ERROR_GET_DOCUMENT)
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENT}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENT)
    
@router.get('/user/{user_id}', response_model=list[Image], tags=["images"])
def get_images_by_user(user_id: str):
    """Obtener imágenes por ID de usuario"""
    if images_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = images_table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        images = []
        for item in response.get("Items", []):
            # Generar presigned URL fresco para cada imagen
            item = add_presigned_url_to_image(item)
            images.append(Image(**item))
        return images
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)