import uuid
import datetime
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
client = boto3.client("dynamodb")

USERS_TABLE_NAME = "deep-market-analyzer-users"
USERNAMES_TABLE_NAME = "deep-market-analyzer-usernames"  
CHATS_TABLE_NAME = "deep-market-analyzer-chats"

def create_tables(read_capacity=5, write_capacity=5):
    """Create Users, Usernames (helper), and Chats tables if they don't exist."""
    existing = {t["TableName"] for t in client.list_tables()["TableNames"]}

    if USERS_TABLE_NAME not in existing:
        print(f"Creating table {USERS_TABLE_NAME}...")
        client.create_table(
            TableName=USERS_TABLE_NAME,
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={"ReadCapacityUnits": read_capacity, "WriteCapacityUnits": write_capacity},
        )
    else:
        print(f"{USERS_TABLE_NAME} exists")

    if USERNAMES_TABLE_NAME not in existing:
        print(f"Creating table {USERNAMES_TABLE_NAME}...")
        client.create_table(
            TableName=USERNAMES_TABLE_NAME,
            KeySchema=[{"AttributeName": "username", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "username", "AttributeType": "S"}],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={"ReadCapacityUnits": read_capacity, "WriteCapacityUnits": write_capacity},
        )
    else:
        print(f"{USERNAMES_TABLE_NAME} exists")

    if CHATS_TABLE_NAME not in existing:
        print(f"Creating table {CHATS_TABLE_NAME}...")
        client.create_table(
            TableName=CHATS_TABLE_NAME,
            KeySchema=[{"AttributeName": "chat_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "chat_id", "AttributeType": "S"},
                {"AttributeName": "user_id", "AttributeType": "S"},
            ],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={"ReadCapacityUnits": read_capacity, "WriteCapacityUnits": write_capacity},
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user_id-index",
                    "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": read_capacity, "WriteCapacityUnits": write_capacity},
                }
            ],
        )
    else:
        print(f"{CHATS_TABLE_NAME} exists")

    # Wait until tables are active (simple wait)
    for t in (USERS_TABLE_NAME, USERNAMES_TABLE_NAME, CHATS_TABLE_NAME):
        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=t)
    print("All tables available.")



# User management 
def create_user(username: str) -> Dict[str, Any]:
    """
    Create a user with a UUID user_id and unique username.
    Uses a transactional write to ensure username uniqueness via the Usernames table.
    Returns the created user dict: {"user_id": "...", "username": "..."}
    Raises ClientError if username already exists.
    """
    user_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    transact_items = [
        {
            "Put": {
                "TableName": USERNAMES_TABLE_NAME,
                "Item": {"username": {"S": username}, "user_id": {"S": user_id}, "created_at": {"S": now}},
                "ConditionExpression": "attribute_not_exists(username)",
            }
        },
        {
            "Put": {
                "TableName": USERS_TABLE_NAME,
                "Item": {"user_id": {"S": user_id}, "username": {"S": username}, "created_at": {"S": now}},
            }
        },
    ]

    try:
        client.transact_write_items(TransactItems=transact_items)
    except ClientError as e:
        # If ConditionalCheckFailedException -> username exists
        raise

    return {"user_id": user_id, "username": username, "created_at": now}


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    table = dynamodb.Table(USERS_TABLE_NAME)
    resp = table.get_item(Key={"user_id": user_id})
    return resp.get("Item")


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Look up the username mapping table to get user_id, then fetch full user."""
    table = dynamodb.Table(USERNAMES_TABLE_NAME)
    resp = table.get_item(Key={"username": username})
    item = resp.get("Item")
    if not item:
        return None
    user_id = item["user_id"]
    return get_user_by_id(user_id)


# Chat management
def create_chat(user_id: str, chat_name: str) -> Dict[str, Any]:
    """
    Create a chat with generated chat_id, owner user_id, chat_name
    """
    chat_id = str(uuid.uuid4())
    table = dynamodb.Table(CHATS_TABLE_NAME)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    item = {
        "chat_id": chat_id,
        "user_id": user_id,
        "chat_name": chat_name,
        "created_at": now,
        "updated_at": now,
    }

    table.put_item(Item=item)
    return item


def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    table = dynamodb.Table(CHATS_TABLE_NAME)
    resp = table.get_item(Key={"chat_id": chat_id})
    return resp.get("Item")


def list_chats_for_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Query Chats table using the user_id global secondary index to list chats belonging to a user.
    """
    table = dynamodb.Table(CHATS_TABLE_NAME)
    resp = table.query(IndexName="user_id-index", KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id), Limit=limit)
    return resp.get("Items", [])


def update_chat_name(chat_id: str, new_name: str) -> None:
    table = dynamodb.Table(CHATS_TABLE_NAME)
    table.update_item(
        Key={"chat_id": chat_id},
        UpdateExpression="SET chat_name = :n, updated_at = :u",
        ExpressionAttributeValues={":n": new_name, ":u": datetime.datetime.now(datetime.timezone.utc).isoformat()},
    )


def delete_chat(chat_id: str) -> None:
    table = dynamodb.Table(CHATS_TABLE_NAME)
    table.delete_item(Key={"chat_id": chat_id})


