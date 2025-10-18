from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Any


class ChatMessage(BaseModel):
    message_id: str
    chat_id: str
    created_at: str
    sender: str
    content: Union[str, List[Any]]  # Puede ser string o lista de objetos
    
    @field_validator('content')
    @classmethod
    def extract_text_from_content(cls, v):
        """
        Si content es una lista, extrae y concatena solo los textos.
        Si es string, lo devuelve tal cual.
        """
        if isinstance(v, list):
            texts = []
            for item in v:
                if isinstance(item, dict):
                    # Extraer el texto del campo 'text' si existe
                    if item.get('type') == 'text' and 'text' in item:
                        texts.append(item['text'])
                elif isinstance(item, str):
                    texts.append(item)
            return '\n'.join(texts) if texts else ''
        return v


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

class MessageRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None
    user_id: Optional[str] = None
    chat_name: Optional[str] = 'New Chat'

class MessageResponse(BaseModel):
    message: str
    chat_id: str
    success: bool
    user_id: Optional[str] = None
    message_id: Optional[str] = None