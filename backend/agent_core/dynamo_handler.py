from typing import Dict, Any
import datetime
import uuid
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
client = boto3.client("dynamodb")

MESSAGES_TABLE_NAME = "deep-market-analyzer-messages"
IMAGES_TABLE_NAME = "deep-market-analyzer-images"
DOCUMENTS_TABLE_NAME = "deep-market-analyzer-documents"


def add_message_to_chat(chat_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store a message as its own item in the MESSAGES table.
    - Generates a uuid message_id
    - Adds created_at (UTC ISO)
    - Stores chat_id on the message for easy queries
    Returns the saved message dict (including message_id and created_at).
    """
    table = dynamodb.Table(MESSAGES_TABLE_NAME)

    # copy input (do not mutate caller dict)
    msg = message.copy()

    # generate id and timestamp
    message_id = str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # enrich the item
    item = {
        "message_id": message_id,  
        "chat_id": chat_id,
        "created_at": created_at,
        **msg,
    }

    try:
        table.put_item(Item=item)
    except ClientError as e:
        # propagate or handle as you prefer
        raise

    return item

def add_image_record(image_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store an image record as its own item in the IMAGES table.
    - Generates a uuid image_id if not provided
    - Adds created_at (UTC ISO)
    Returns the saved image record dict (including image_id and created_at).
    """
    table = dynamodb.Table(IMAGES_TABLE_NAME)

    # copy input (do not mutate caller dict)
    img = image_record.copy()

    # generate id and timestamp
    if "image_id" not in img:
        img["image_id"] = str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # enrich the item
    item = {
        "created_at": created_at,
        **img,
    }

    try:
        table.put_item(Item=item)
    except ClientError as e:
        # propagate or handle as you prefer
        raise

    return item

def add_document_record(document_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store a document record as its own item in the DOCUMENTS table.
    - Generates a uuid document_id if not provided
    - Adds created_at (UTC ISO)
    Returns the saved document record dict (including document_id and created_at).
    """
    table = dynamodb.Table(DOCUMENTS_TABLE_NAME)

    # copy input (do not mutate caller dict)
    doc = document_record.copy()

    # generate id and timestamp
    if "document_id" not in doc:
        doc["document_id"] = str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # enrich the item
    item = {
        "created_at": created_at,
        **doc,
    }

    try:
        table.put_item(Item=item)
    except ClientError as e:
        # propagate or handle as you prefer
        raise

    return item
