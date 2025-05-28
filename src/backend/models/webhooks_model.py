from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import re

class WebhookEvent(str, Enum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    TRANSLATION_COMPLETED = "translation.completed"
    TTS_COMPLETED = "tts.completed"
    STT_COMPLETED = "stt.completed"
    VOICE_SAMPLE_CREATED = "voice_sample.created"
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ENDED = "conversation.ended"
    FILE_UPLOADED = "file.uploaded"
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    SYSTEM_ALERT = "system.alert"
    PAYMENT_COMPLETED = "payment.completed"
    SUBSCRIPTION_UPDATED = "subscription.updated"

class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    SUSPENDED = "suspended"

class WebhookMethod(str, Enum):
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"

class WebhookDeliveryStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"

class WebhookCreate(BaseModel):
    name: str = Field(..., description="Nombre descriptivo del webhook")
    url: HttpUrl = Field(..., description="URL de destino del webhook")
    events: List[WebhookEvent] = Field(..., description="Eventos que activarán el webhook")
    method: WebhookMethod = Field(default=WebhookMethod.POST, description="Método HTTP")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers personalizados")
    secret: Optional[str] = Field(None, description="Secreto para firmar el payload")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout en segundos")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Intentos de reintento")
    retry_delay: int = Field(default=60, ge=1, le=3600, description="Delay entre reintentos (segundos)")
    active: bool = Field(default=True, description="Estado activo/inactivo")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        if len(v) < 3:
            raise ValueError('El nombre debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El nombre no puede exceder 100 caracteres')
        return v
    
    @validator('events')
    def events_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos un evento')
        return v
    
    @validator('headers')
    def headers_must_be_valid(cls, v):
        if v:
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError('Los headers deben ser strings')
                if len(key) > 100 or len(value) > 500:
                    raise ValueError('Headers demasiado largos')
        return v

class Webhook(BaseModel):
    id: str = Field(..., description="ID único del webhook")
    name: str = Field(..., description="Nombre descriptivo")
    url: HttpUrl = Field(..., description="URL de destino")
    events: List[WebhookEvent] = Field(..., description="Eventos suscritos")
    method: WebhookMethod = Field(..., description="Método HTTP")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers personalizados")
    secret: Optional[str] = Field(None, description="Secreto para firmar")
    timeout: int = Field(..., description="Timeout en segundos")
    retry_attempts: int = Field(..., description="Intentos de reintento")
    retry_delay: int = Field(..., description="Delay entre reintentos")
    status: WebhookStatus = Field(..., description="Estado del webhook")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización")
    last_triggered_at: Optional[datetime] = Field(None, description="Última activación")
    total_deliveries: int = Field(default=0, description="Total de entregas")
    successful_deliveries: int = Field(default=0, description="Entregas exitosas")
    failed_deliveries: int = Field(default=0, description="Entregas fallidas")
    user_id: str = Field(..., description="ID del usuario propietario")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "wh_123456789",
                "name": "User Events Webhook",
                "url": "https://api.example.com/webhooks/users",
                "events": ["user.created", "user.updated"],
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer token123",
                    "Content-Type": "application/json"
                },
                "secret": "webhook_secret_123",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 60,
                "status": "active",
                "created_at": "2023-01-01T00:00:00Z",
                "total_deliveries": 150,
                "successful_deliveries": 145,
                "failed_deliveries": 5,
                "user_id": "user_123"
            }
        }

class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nuevo nombre")
    url: Optional[HttpUrl] = Field(None, description="Nueva URL")
    events: Optional[List[WebhookEvent]] = Field(None, description="Nuevos eventos")
    method: Optional[WebhookMethod] = Field(None, description="Nuevo método")
    headers: Optional[Dict[str, str]] = Field(None, description="Nuevos headers")
    secret: Optional[str] = Field(None, description="Nuevo secreto")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="Nuevo timeout")
    retry_attempts: Optional[int] = Field(None, ge=0, le=10, description="Nuevos intentos")
    retry_delay: Optional[int] = Field(None, ge=1, le=3600, description="Nuevo delay")
    active: Optional[bool] = Field(None, description="Nuevo estado activo")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Nuevos metadatos")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre no puede estar vacío')
            if len(v) < 3:
                raise ValueError('El nombre debe tener al menos 3 caracteres')
            if len(v) > 100:
                raise ValueError('El nombre no puede exceder 100 caracteres')
        return v

class WebhookDelivery(BaseModel):
    id: str = Field(..., description="ID único de la entrega")
    webhook_id: str = Field(..., description="ID del webhook")
    event_type: WebhookEvent = Field(..., description="Tipo de evento")
    payload: Dict[str, Any] = Field(..., description="Payload enviado")
    status: WebhookDeliveryStatus = Field(..., description="Estado de la entrega")
    http_status: Optional[int] = Field(None, description="Código HTTP de respuesta")
    response_body: Optional[str] = Field(None, description="Cuerpo de la respuesta")
    response_headers: Optional[Dict[str, str]] = Field(None, description="Headers de respuesta")
    attempt_count: int = Field(default=1, description="Número de intento")
    duration_ms: Optional[int] = Field(None, description="Duración en milisegundos")
    error_message: Optional[str] = Field(None, description="Mensaje de error")
    created_at: datetime = Field(..., description="Fecha de creación")
    delivered_at: Optional[datetime] = Field(None, description="Fecha de entrega")
    next_retry_at: Optional[datetime] = Field(None, description="Próximo reintento")

class WebhookTest(BaseModel):
    webhook_id: Optional[str] = Field(None, description="ID del webhook a probar")
    url: HttpUrl = Field(..., description="URL de prueba")
    event_type: WebhookEvent = Field(..., description="Tipo de evento a simular")
    method: WebhookMethod = Field(default=WebhookMethod.POST, description="Método HTTP")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers personalizados")
    custom_payload: Optional[Dict[str, Any]] = Field(None, description="Payload personalizado")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout en segundos")

class WebhookTestResult(BaseModel):
    success: bool = Field(..., description="Éxito de la prueba")
    http_status: int = Field(..., description="Código HTTP")
    response_body: str = Field(..., description="Cuerpo de respuesta")
    response_headers: Dict[str, str] = Field(..., description="Headers de respuesta")
    duration_ms: int = Field(..., description="Duración en milisegundos")
    payload_sent: Dict[str, Any] = Field(..., description="Payload enviado")
    error_message: Optional[str] = Field(None, description="Mensaje de error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la prueba")

class WebhookResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class WebhookStats(BaseModel):
    webhook_id: str = Field(..., description="ID del webhook")
    webhook_name: str = Field(..., description="Nombre del webhook")
    total_deliveries: int = Field(..., description="Total de entregas")
    successful_deliveries: int = Field(..., description="Entregas exitosas")
    failed_deliveries: int = Field(..., description="Entregas fallidas")
    success_rate: float = Field(..., description="Tasa de éxito (%)")
    avg_response_time: float = Field(..., description="Tiempo de respuesta promedio (ms)")
    last_delivery: Optional[datetime] = Field(None, description="Última entrega")
    most_common_event: Optional[str] = Field(None, description="Evento más común")
    deliveries_by_status: Dict[str, int] = Field(..., description="Entregas por estado")
    deliveries_by_event: Dict[str, int] = Field(..., description="Entregas por evento")
    recent_deliveries: List[WebhookDelivery] = Field(..., description="Entregas recientes")

class WebhookEventPayload(BaseModel):
    event_id: str = Field(..., description="ID único del evento")
    event_type: WebhookEvent = Field(..., description="Tipo de evento")
    timestamp: datetime = Field(..., description="Timestamp del evento")
    data: Dict[str, Any] = Field(..., description="Datos del evento")
    user_id: Optional[str] = Field(None, description="ID del usuario relacionado")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "evt_123456789",
                "event_type": "user.created",
                "timestamp": "2023-01-01T00:00:00Z",
                "data": {
                    "user_id": "user_123",
                    "username": "john_doe",
                    "email": "john@example.com",
                    "created_at": "2023-01-01T00:00:00Z"
                },
                "user_id": "user_123",
                "metadata": {
                    "source": "api",
                    "version": "1.0"
                }
            }
        }

class WebhookSignature(BaseModel):
    timestamp: str = Field(..., description="Timestamp de la firma")
    signature: str = Field(..., description="Firma HMAC")
    
class WebhookSecurityConfig(BaseModel):
    verify_ssl: bool = Field(default=True, description="Verificar certificados SSL")
    allowed_ips: Optional[List[str]] = Field(None, description="IPs permitidas")
    require_signature: bool = Field(default=True, description="Requerir firma")
    signature_header: str = Field(default="X-Webhook-Signature", description="Header de firma")
    timestamp_header: str = Field(default="X-Webhook-Timestamp", description="Header de timestamp")
    max_age_seconds: int = Field(default=300, description="Edad máxima del timestamp")

class WebhookFilter(BaseModel):
    status: Optional[WebhookStatus] = Field(None, description="Filtrar por estado")
    event_type: Optional[WebhookEvent] = Field(None, description="Filtrar por evento")
    created_after: Optional[datetime] = Field(None, description="Creados después de")
    created_before: Optional[datetime] = Field(None, description="Creados antes de")
    search: Optional[str] = Field(None, description="Buscar en nombre o URL")
