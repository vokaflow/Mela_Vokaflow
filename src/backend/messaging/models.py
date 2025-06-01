#!/usr/bin/env python3
"""
💬 Modelos de Mensajería - VokaFlow Enterprise
Modelos de datos para conversaciones, mensajes y tiempo real
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

Base = declarative_base()

class ConversationType(PyEnum):
    """Tipos de conversación"""
    CHAT = "chat"
    GROUP = "group"
    SUPPORT = "support"
    CHANNEL = "channel"

class MessageStatus(PyEnum):
    """Estados de mensaje"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class MessageType(PyEnum):
    """Tipos de mensaje"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"
    VIDEO = "video"
    TRANSLATION = "translation"

# Modelos SQLAlchemy
class Conversation(Base):
    """Modelo de conversación"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(ConversationType), default=ConversationType.CHAT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)  # User ID
    is_active = Column(Boolean, default=True)
    msg_metadata = Column(JSON, default={})
    
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    participants = relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Modelo de mensaje"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, nullable=False)  # ID del remitente
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reply_to_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    msg_metadata = Column(JSON, default={})
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")
    reply_to = relationship("Message", remote_side=[id])

class ConversationParticipant(Base):
    """Participantes de conversación"""
    __tablename__ = "conversation_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String(50), default="member")  # member, admin, moderator
    is_active = Column(Boolean, default=True)
    last_read_message_id = Column(Integer, nullable=True)
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="participants")

# Modelos Pydantic para API
class ConversationCreate(BaseModel):
    """Esquema para crear conversación"""
    title: str
    description: Optional[str] = None
    type: ConversationType = ConversationType.CHAT
    participants: List[int] = []
    msg_metadata: Dict[str, Any] = {}

class ConversationUpdate(BaseModel):
    """Esquema para actualizar conversación"""
    title: Optional[str] = None
    description: Optional[str] = None
    msg_metadata: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    """Esquema para crear mensaje"""
    content: str
    message_type: MessageType = MessageType.TEXT
    reply_to_id: Optional[int] = None
    msg_metadata: Dict[str, Any] = {}

class MessageResponse(BaseModel):
    """Respuesta de mensaje"""
    id: int
    conversation_id: int
    user_id: int
    content: str
    message_type: MessageType
    status: MessageStatus
    created_at: datetime
    updated_at: datetime
    reply_to_id: Optional[int] = None
    msg_metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Respuesta de conversación"""
    id: int
    title: str
    description: Optional[str] = None
    type: ConversationType
    created_at: datetime
    updated_at: datetime
    created_by: int
    is_active: bool
    msg_metadata: Dict[str, Any] = {}
    message_count: Optional[int] = 0
    last_message: Optional[MessageResponse] = None
    participants: List[int] = []
    
    class Config:
        from_attributes = True

class ParticipantAdd(BaseModel):
    """Esquema para añadir participante"""
    user_id: int
    role: str = "member"

class MessageSearch(BaseModel):
    """Esquema para búsqueda de mensajes"""
    query: str
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None
    message_type: Optional[MessageType] = None
    limit: int = 50
    offset: int = 0

class WebSocketMessage(BaseModel):
    """Mensaje WebSocket"""
    type: str  # message, notification, status
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None
    content: str
    timestamp: datetime
    msg_metadata: Dict[str, Any] = {}

class TypingIndicator(BaseModel):
    """Indicador de escritura"""
    conversation_id: int
    user_id: int
    is_typing: bool
    timestamp: datetime 