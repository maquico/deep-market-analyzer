import os
import boto3
import uuid
import datetime
from fastapi import APIRouter, HTTPException
from app.models import User
from app.dynamo import (users_table, dynamodb)

router = APIRouter()

# Constantes de mensajes de error
ERROR_TABLE_NOT_CONFIGURED = "DynamoDB users table name not configured"
ERROR_GET_USERS = "Error al obtener los usuarios"
ERROR_GET_USER = "Error al obtener el usuario"
ERROR_CREATE_USER = "Error al crear el usuario"
ERROR_DELETE_USER = "Error al eliminar el usuario"
ERROR_USER_NOT_FOUND = "Usuario no encontrado"
MSG_USER_DELETED = "Usuario eliminado correctamente"

@router.get("/", tags=["users"])
async def get_users():
    """Obtener todos los usuarios"""
    if users_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = users_table.scan()
        return {"users": [User(**item) for item in response.get("Items", [])]}
    except Exception as e:
        print(f"{ERROR_GET_USERS}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_USERS)
    
@router.get("/{user_id}", tags=["users"])
async def get_user(user_id: int):
    """Obtener un usuario por ID"""
    if users_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = users_table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        if item:
            return User(**item)
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    except HTTPException:
        raise
    except Exception as e:
        print(f"{ERROR_GET_USER}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_GET_USER)

@router.post("/users", tags=["users"])
async def create_user(name: str, email: str):
    """Crear un nuevo usuario"""
    if users_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)

    user_id = str(uuid.uuid4())
    user = {
        "user_id": user_id,
        "username": name,
        "created_at": datetime.datetime.now().isoformat()
    }
    try:
        users_table.put_item(Item=user)
        return User(**user)
    except Exception as e:
        print(f"{ERROR_CREATE_USER}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_CREATE_USER)

@router.delete("/{user_id}", tags=["users"])
async def delete_user(user_id: str):
    """Eliminar un usuario por ID"""
    if users_table is None:
        raise HTTPException(status_code=500, detail=ERROR_TABLE_NOT_CONFIGURED)
    try:
        response = users_table.delete_item(
            Key={"user_id": user_id},
            ConditionExpression="attribute_exists(user_id)"
        )
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
            return {"message": MSG_USER_DELETED}
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    except Exception as e:
        print(f"{ERROR_DELETE_USER}: {e}")
        raise HTTPException(status_code=500, detail=ERROR_DELETE_USER)
