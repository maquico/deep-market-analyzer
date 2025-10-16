import boto3
import os
import uuid
import datetime
from fastapi import APIRouter, HTTPException
from app.models import Document
from app.dynamo import (
    documents_table
)

router = APIRouter()

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
            KeyConditionExpression=boto3.dynamodb.conditions.Key('chat_id').eq(chat_id)
        )
        return [Document(**item) for item in response.get("Items", [])]
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
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        return [Document(**item) for item in response.get("Items", [])]
    except Exception as e:
        print(f"{ERROR_GET_DOCUMENTS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_DOCUMENTS)