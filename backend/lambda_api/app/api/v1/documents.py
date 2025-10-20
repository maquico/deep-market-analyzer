import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from config import config
from app.models import Document
from app.dynamo import (
    documents_table
)


router = APIRouter()
# Configuración para presigned URLs
PRESIGNED_URL_EXPIRATION = 3600  # 1 hora


# Cliente S3 para generar presigned URLs
s3_client = boto3.client('s3')
S3_BUCKET = config.S3_BUCKET_NAME


def generate_presigned_url(s3_key: str) -> Optional[str]:
    """Genera un presigned URL para un archivo en S3"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        # print(f"Presigned URL generado para {s3_key}: {url}")
        return url
    except Exception as e:
        print(f"Error generando presigned URL: {e}")
        return None


def add_presigned_url_to_document(doc_dict: dict) -> dict:
    """Agrega un presigned URL fresco al documento"""
    if doc_dict.get('s3_key'):
        presigned_url = generate_presigned_url(doc_dict['s3_key'])
        if presigned_url:
            doc_dict['pdf_presigned_url'] = presigned_url
    return doc_dict

# Constantes de mensajes de error
ERROR_TABLE_NOT_CONFIGURED = "DynamoDB documents table name not configured"
ERROR_GET_DOCUMENTS = "Error al obtener los documentos"
ERROR_GET_DOCUMENT = "Error al obtener el documento"
ERROR_CREATE_DOCUMENT = "Error al crear el documento"
ERROR_DELETE_DOCUMENT = "Error al eliminar el documento"
MSG_DOCUMENT_DELETED = "Documento eliminado exitosamente"

@router.get("/chat/{chat_id}", response_model=list[Document], tags=["documents"])
def get_documents(chat_id: str):
    """Obtener documentos por ID de chat"""
    if documents_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = documents_table.query(
            IndexName="chat_id-index",
            KeyConditionExpression=Key('chat_id').eq(chat_id)
        )
        documents = []
        for item in response.get("Items", []):
            # Generar presigned URL fresco para cada documento
            item = add_presigned_url_to_document(item)
            documents.append(Document(**item))
        return documents
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)
    
@router.get('/{document_id}', response_model=Document, tags=["documents"])
def get_document(document_id: str):
    """Obtener un documento por ID"""
    if documents_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = documents_table.get_item(
            Key={'document_id': document_id}
        )
        item = response.get("Item")
        if item:
            # Generar presigned URL fresco
            item = add_presigned_url_to_document(item)
            return Document(**item)
        else:
            raise HTTPException(status_code=404, detail=ERROR_GET_DOCUMENT)
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENT}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENT)
    
@router.get('/user/{user_id}', response_model=list[Document], tags=["documents"])
def get_documents_by_user(user_id: str):
    """Obtener documentos por ID de usuario"""
    if documents_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = documents_table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        documents = []
        for item in response.get("Items", []):
            # Generar presigned URL fresco para cada documento
            item = add_presigned_url_to_document(item)
            documents.append(Document(**item))
        return documents
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)