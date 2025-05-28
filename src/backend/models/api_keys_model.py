from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import re

class ApiKeyScope(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    TRANSLATE = "translate"
    TTS = "tts"
    STT = "stt"
    VICKY = "vicky"
    VOICE = "voice"
    FILES = "files"
    ANALYTICS = "analytics"

class ApiKeyStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"

class ApiKeyEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

class ApiKeyType(str, Enum):
    SERVER = "server"
    CLIENT = "client"
    ADMIN = "admin"
    SYSTEM = "system"
    INTEGRATION = "integration"

class ApiKeyCreate(BaseModel):
    name: str = Field(..., description="Nombre descriptivo de la API key")
    scopes: List[ApiKeyScope] = Field(..., description="Permisos de la API key")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración (opcional)")
    environment: ApiKeyEnvironment = Field(default=ApiKeyEnvironment.DEVELOPMENT, description="Entorno")
    type: ApiKeyType = Field(default=ApiKeyType.SERVER, description="Tipo de API key")
    rate_limit: Optional[int] = Field(None, description="Límite de peticiones por minuto")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        if len(v) < 3:
            raise ValueError('El nombre debe tener al menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('El nombre no puede exceder 50 caracteres')
        return v
    
    @validator('scopes')
    def scopes_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos un scope')
        return v

class ApiKey(BaseModel):
    id: str = Field(..., description="ID único de la API key")
    key: str = Field(..., description="API key (valor secreto)")
    prefix: str = Field(..., description="Prefijo visible de la API key")
    name: str = Field(..., description="Nombre descriptivo")
    user_id: str = Field(..., description="ID del usuario propietario")
    scopes: List[ApiKeyScope] = Field(..., description="Permisos")
    status: ApiKeyStatus = Field(default=ApiKeyStatus.ACTIVE, description="Estado")
    environment: ApiKeyEnvironment = Field(..., description="Entorno")
    type: ApiKeyType = Field(..., description="Tipo de API key")
    created_at: datetime = Field(..., description="Fecha de creación")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    rate_limit: Optional[int] = Field(None, description="Límite de peticiones por minuto")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "ak_123456789",
                "key": "sk_live_abcdefghijklmnopqrstuvwxyz0123456789",
                "prefix": "sk_live_abc",
                "name": "Production API Key",
                "user_id": "user_123",
                "scopes": ["read", "write"],
                "status": "active",
                "environment": "production",
                "type": "server",
                "created_at": "2023-01-01T00:00:00Z",
                "expires_at": "2024-01-01T00:00:00Z",
                "last_used_at": "2023-06-15T14:30:00Z",
                "rate_limit": 100,
                "metadata": {
                    "created_by": "admin",
                    "project": "main-app"
                }
            }
        }

class ApiKeyPublic(BaseModel):
    id: str = Field(..., description="ID único de la API key")
    prefix: str = Field(..., description="Prefijo visible de la API key")
    name: str = Field(..., description="Nombre descriptivo")
    scopes: List[ApiKeyScope] = Field(..., description="Permisos")
    status: ApiKeyStatus = Field(..., description="Estado")
    environment: ApiKeyEnvironment = Field(..., description="Entorno")
    type: ApiKeyType = Field(..., description="Tipo de API key")
    created_at: datetime = Field(..., description="Fecha de creación")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    rate_limit: Optional[int] = Field(None, description="Límite de peticiones por minuto")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    usage_count: int = Field(default=0, description="Número de usos")
    is_expired: bool = Field(default=False, description="Indica si está expirada")
    days_until_expiry: Optional[int] = Field(None, description="Días hasta expiración")

class ApiKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nuevo nombre")
    status: Optional[ApiKeyStatus] = Field(None, description="Nuevo estado")
    scopes: Optional[List[ApiKeyScope]] = Field(None, description="Nuevos permisos")
    expires_at: Optional[datetime] = Field(None, description="Nueva fecha de expiración")
    rate_limit: Optional[int] = Field(None, description="Nuevo límite de peticiones")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Nuevos metadatos")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre no puede estar vacío')
            if len(v) < 3:
                raise ValueError('El nombre debe tener al menos 3 caracteres')
            if len(v) > 50:
                raise ValueError('El nombre no puede exceder 50 caracteres')
        return v

class ApiKeyUsage(BaseModel):
    api_key_id: str = Field(..., description="ID de la API key")
    endpoint: str = Field(..., description="Endpoint llamado")
    method: str = Field(..., description="Método HTTP")
    status_code: int = Field(..., description="Código de estado HTTP")
    response_time: float = Field(..., description="Tiempo de respuesta (ms)")
    timestamp: datetime = Field(..., description="Timestamp")
    ip_address: Optional[str] = Field(None, description="Dirección IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    request_size: Optional[int] = Field(None, description="Tamaño de la petición (bytes)")
    response_size: Optional[int] = Field(None, description="Tamaño de la respuesta (bytes)")
    error: Optional[str] = Field(None, description="Error si lo hubo")

class ApiKeyUsageSummary(BaseModel):
    api_key_id: str = Field(..., description="ID de la API key")
    api_key_name: str = Field(..., description="Nombre de la API key")
    api_key_prefix: str = Field(..., description="Prefijo de la API key")
    total_requests: int = Field(..., description="Total de peticiones")
    successful_requests: int = Field(..., description="Peticiones exitosas")
    failed_requests: int = Field(..., description="Peticiones fallidas")
    avg_response_time: float = Field(..., description="Tiempo de respuesta promedio (ms)")
    total_data_transferred: int = Field(..., description="Datos transferidos (bytes)")
    top_endpoints: List[Dict[str, Any]] = Field(..., description="Endpoints más usados")
    usage_by_day: Dict[str, int] = Field(..., description="Uso por día")
    last_used: Optional[datetime] = Field(None, description="Último uso")
    error_rate: float = Field(..., description="Tasa de error (%)")

class ApiKeyResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class ApiKeyCreateResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="API key created successfully")
    api_key: ApiKey = Field(..., description="API key creada")
    important_notice: str = Field(
        default="IMPORTANTE: Esta es la única vez que verás la API key completa. Guárdala en un lugar seguro.",
        description="Aviso importante"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
