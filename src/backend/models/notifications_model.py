from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SYSTEM = "system"
    USER = "user"
    SECURITY = "security"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Notification(BaseModel):
    id: Optional[str] = Field(None, description="ID único de la notificación")
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    type: NotificationType = Field(..., description="Tipo de notificación")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Prioridad")
    channel: NotificationChannel = Field(default=NotificationChannel.IN_APP, description="Canal de envío")
    status: NotificationStatus = Field(default=NotificationStatus.PENDING, description="Estado")
    user_id: Optional[str] = Field(None, description="ID del usuario destinatario")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    sent_at: Optional[datetime] = Field(None, description="Fecha de envío")
    read_at: Optional[datetime] = Field(None, description="Fecha de lectura")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")

class NotificationCreate(BaseModel):
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    type: NotificationType = Field(..., description="Tipo de notificación")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Prioridad")
    channel: NotificationChannel = Field(default=NotificationChannel.IN_APP, description="Canal de envío")
    user_id: Optional[str] = Field(None, description="ID del usuario destinatario")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")

class NotificationSend(BaseModel):
    recipients: List[str] = Field(..., description="Lista de destinatarios")
    title: str = Field(..., description="Título de la notificación")
    message: str = Field(..., description="Mensaje de la notificación")
    type: NotificationType = Field(..., description="Tipo de notificación")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Prioridad")
    channels: List[NotificationChannel] = Field(..., description="Canales de envío")
    schedule_at: Optional[datetime] = Field(None, description="Programar envío")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Nuevo título")
    message: Optional[str] = Field(None, description="Nuevo mensaje")
    status: Optional[NotificationStatus] = Field(None, description="Nuevo estado")
    read_at: Optional[datetime] = Field(None, description="Fecha de lectura")

class NotificationSettings(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    email_enabled: bool = Field(default=True, description="Notificaciones por email")
    sms_enabled: bool = Field(default=False, description="Notificaciones por SMS")
    push_enabled: bool = Field(default=True, description="Notificaciones push")
    in_app_enabled: bool = Field(default=True, description="Notificaciones in-app")
    types_enabled: List[NotificationType] = Field(default_factory=lambda: list(NotificationType), description="Tipos habilitados")
    priority_threshold: NotificationPriority = Field(default=NotificationPriority.LOW, description="Umbral de prioridad")
    quiet_hours_start: Optional[str] = Field(None, description="Inicio horas silenciosas (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Fin horas silenciosas (HH:MM)")
    timezone: str = Field(default="UTC", description="Zona horaria")

class NotificationPreferences(BaseModel):
    frequency: str = Field(default="immediate", description="Frecuencia de notificaciones")
    digest_enabled: bool = Field(default=False, description="Resumen diario habilitado")
    digest_time: str = Field(default="09:00", description="Hora del resumen diario")
    language: str = Field(default="es", description="Idioma de las notificaciones")
    sound_enabled: bool = Field(default=True, description="Sonidos habilitados")

class NotificationTemplate(BaseModel):
    id: Optional[str] = Field(None, description="ID de la plantilla")
    name: str = Field(..., description="Nombre de la plantilla")
    title_template: str = Field(..., description="Plantilla del título")
    message_template: str = Field(..., description="Plantilla del mensaje")
    type: NotificationType = Field(..., description="Tipo de notificación")
    variables: List[str] = Field(default_factory=list, description="Variables disponibles")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")

class NotificationStats(BaseModel):
    total_sent: int = Field(..., description="Total enviadas")
    total_delivered: int = Field(..., description="Total entregadas")
    total_read: int = Field(..., description="Total leídas")
    total_failed: int = Field(..., description="Total fallidas")
    delivery_rate: float = Field(..., description="Tasa de entrega %")
    read_rate: float = Field(..., description="Tasa de lectura %")
    by_channel: Dict[str, int] = Field(..., description="Estadísticas por canal")
    by_type: Dict[str, int] = Field(..., description="Estadísticas por tipo")

class NotificationResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class BulkNotificationResult(BaseModel):
    total_requested: int = Field(..., description="Total solicitadas")
    total_sent: int = Field(..., description="Total enviadas")
    total_failed: int = Field(..., description="Total fallidas")
    failed_recipients: List[str] = Field(default_factory=list, description="Destinatarios fallidos")
    errors: List[str] = Field(default_factory=list, description="Errores encontrados")
