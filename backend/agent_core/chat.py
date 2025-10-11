from typing import Dict, Any
import datetime
import uuid
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
client = boto3.client("dynamodb")

MESSAGES_TABLE_NAME = "deep-market-analyzer-messages"


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
