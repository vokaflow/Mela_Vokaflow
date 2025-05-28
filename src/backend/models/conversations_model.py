from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PAUSED = "paused"

class ConversationType(str, Enum):
    CHAT = "chat"
    VOICE = "voice"
    TRANSLATION = "translation"
    SUPPORT = "support"
    TRAINING = "training"

class Message(BaseModel):
    id: Optional[str] = Field(None, description="ID único del mensaje")
    role: MessageRole = Field(..., description="Rol del mensaje")
    content: str = Field(..., description="Contenido del mensaje")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos del mensaje")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del mensaje")
    edited: bool = Field(default=False, description="Si el mensaje fue editado")
    edited_at: Optional[datetime] = Field(None, description="Fecha de edición")
    attachments: Optional[List[str]] = Field(None, description="URLs de archivos adjuntos")
    tokens: Optional[int] = Field(None, description="Número de tokens")

class MessageCreate(BaseModel):
    role: MessageRole = Field(..., description="Rol del mensaje")
    content: str = Field(..., description="Contenido del mensaje")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos del mensaje")
    attachments: Optional[List[str]] = Field(None, description="URLs de archivos adjuntos")

class Conversation(BaseModel):
    id: Optional[str] = Field(None, description="ID único de la conversación")
    title: str = Field(..., description="Título de la conversación")
    description: Optional[str] = Field(None, description="Descripción de la conversación")
    type: ConversationType = Field(default=ConversationType.CHAT, description="Tipo de conversación")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE, description="Estado")
    user_id: str = Field(..., description="ID del usuario propietario")
    participants: List[str] = Field(default_factory=list, description="IDs de participantes")
    messages: List[Message] = Field(default_factory=list, description="Mensajes de la conversación")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    last_message_at: Optional[datetime] = Field(None, description="Último mensaje")
    message_count: int = Field(default=0, description="Número de mensajes")
    settings: Optional[Dict[str, Any]] = Field(None, description="Configuraciones específicas")
    tags: List[str] = Field(default_factory=list, description="Etiquetas")

class ConversationCreate(BaseModel):
    title: str = Field(..., description="Título de la conversación")
    description: Optional[str] = Field(None, description="Descripción")
    type: ConversationType = Field(default=ConversationType.CHAT, description="Tipo")
    participants: List[str] = Field(default_factory=list, description="Participantes adicionales")
    settings: Optional[Dict[str, Any]] = Field(None, description="Configuraciones")
    tags: List[str] = Field(default_factory=list, description="Etiquetas")

class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Nuevo título")
    description: Optional[str] = Field(None, description="Nueva descripción")
    status: Optional[ConversationStatus] = Field(None, description="Nuevo estado")
    participants: Optional[List[str]] = Field(None, description="Nuevos participantes")
    settings: Optional[Dict[str, Any]] = Field(None, description="Nuevas configuraciones")
    tags: Optional[List[str]] = Field(None, description="Nuevas etiquetas")

class ConversationSummary(BaseModel):
    id: str = Field(..., description="ID de la conversación")
    title: str = Field(..., description="Título")
    type: ConversationType = Field(..., description="Tipo")
    status: ConversationStatus = Field(..., description="Estado")
    message_count: int = Field(..., description="Número de mensajes")
    last_message_at: Optional[datetime] = Field(None, description="Último mensaje")
    last_message_preview: Optional[str] = Field(None, description="Vista previa del último mensaje")
    unread_count: int = Field(default=0, description="Mensajes no leídos")
    created_at: datetime = Field(..., description="Fecha de creación")

class ConversationStats(BaseModel):
    total_conversations: int = Field(..., description="Total de conversaciones")
    active_conversations: int = Field(..., description="Conversaciones activas")
    total_messages: int = Field(..., description="Total de mensajes")
    average_messages_per_conversation: float = Field(..., description="Promedio de mensajes")
    conversations_by_type: Dict[str, int] = Field(..., description="Por tipo")
    conversations_by_status: Dict[str, int] = Field(..., description="Por estado")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Actividad reciente")

class ConversationResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class MessageResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Message processed successfully")
    data: Message = Field(..., description="Mensaje procesado")
    conversation_id: str = Field(..., description="ID de la conversación")
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationExport(BaseModel):
    conversation_id: str = Field(..., description="ID de la conversación")
    format: str = Field(default="json", description="Formato de exportación")
    include_metadata: bool = Field(default=True, description="Incluir metadatos")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Rango de fechas")

class ConversationSearch(BaseModel):
    query: str = Field(..., description="Término de búsqueda")
    conversation_ids: Optional[List[str]] = Field(None, description="IDs específicas")
    message_role: Optional[MessageRole] = Field(None, description="Rol de mensaje")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    limit: int = Field(default=50, description="Límite de resultados")
