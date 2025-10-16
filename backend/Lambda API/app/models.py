from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    message_id: str
    chat_id: str
    created_at: str
    sender: str
    content: str


class Chat(BaseModel):
    chat_id: str
    chat_name: str
    user_id: str
    messages: Optional[List[ChatMessage]] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class User(BaseModel):
    user_id: str
    created_at: str
    username: str

class Document(BaseModel):
    document_id: str
    chat_id: str
    user_id: str
    name: str
    s3_path: str
    uploaded_at: str