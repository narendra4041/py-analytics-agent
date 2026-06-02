from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4


class ChatSessionCreate(BaseModel):
    title: str
    catalog: str
    schema: str


class ChatSession(BaseModel):
    id: str
    title: str
    catalog: str
    schema: str
    created_at: datetime


class MessageCreate(BaseModel):
    role: str
    content: str


class Message(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    created_at: datetime

class ExecuteCodeRequest(BaseModel):
    code: str

class GenerateCodeRequest(BaseModel):
    query: str
    catalog: str
    schema: str

class AgentChatRequest(BaseModel):
    chat_id: str
    message: str