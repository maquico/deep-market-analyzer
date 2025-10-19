"""
Configuración de DynamoDB usando la configuración centralizada.
Este módulo carga los secretos desde AWS Secrets Manager (producción) o .env (desarrollo).
"""
import boto3
from config import config

# Obtener el recurso de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=config.aws_region)

# Inicializar las tablas (pueden ser None si no están configuradas)
chats_table = dynamodb.Table(config.DYNAMO_CHATS_TABLE_NAME) if config.DYNAMO_CHATS_TABLE_NAME else None
users_table = dynamodb.Table(config.DYNAMO_USERS_TABLE_NAME) if config.DYNAMO_USERS_TABLE_NAME else None
usernames_table = dynamodb.Table(config.DYNAMO_USERNAMES_TABLE_NAME) if config.DYNAMO_USERNAMES_TABLE_NAME else None
messages_table = dynamodb.Table(config.DYNAMO_MESSAGES_TABLE_NAME) if config.DYNAMO_MESSAGES_TABLE_NAME else None
documents_table = dynamodb.Table(config.DYNAMO_DOCUMENTS_TABLE_NAME) if config.DYNAMO_DOCUMENTS_TABLE_NAME else None
images_table = dynamodb.Table(config.DYNAMO_IMAGES_TABLE_NAME) if config.DYNAMO_IMAGES_TABLE_NAME else None