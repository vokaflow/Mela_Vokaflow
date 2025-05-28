#!/usr/bin/env python3
"""
Modelos para conversaciones en VokaFlow
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class MessageBase(BaseModel):
    """Base para mensajes"""
    role: str  # user, assistant, system
    content: str

class MessageCreate(MessageBase):
    """Crear mensaje"""
    conversation_id: Optional[str] = None

class MessageResponse(MessageBase):
    """Respuesta de mensaje"""
    id: int
    conversation_id: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = {}
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    """Base para conversaciones"""
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    """Crear conversación"""
    user_id: Optional[int] = None

class ConversationResponse(ConversationBase):
    """Respuesta de conversación"""
    id: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: int = 0
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True
