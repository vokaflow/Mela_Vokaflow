from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING = "pending"

class MaintenanceMode(str, Enum):
    OFF = "off"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    EMERGENCY = "emergency"

class LogCategory(str, Enum):
    SECURITY = "security"
    SYSTEM = "system"
    USER_ACTION = "user_action"
    API = "api"
    ERROR = "error"
    AUDIT = "audit"

class AdminDashboard(BaseModel):
    system_health: Dict[str, Any] = Field(..., description="Estado de salud del sistema")
    user_stats: Dict[str, int] = Field(..., description="Estadísticas de usuarios")
    api_stats: Dict[str, Any] = Field(..., description="Estadísticas de API")
    resource_usage: Dict[str, float] = Field(..., description="Uso de recursos")
    recent_activities: List[Dict[str, Any]] = Field(..., description="Actividades recientes")
    alerts: List[Dict[str, Any]] = Field(..., description="Alertas del sistema")
    performance_metrics: Dict[str, Any] = Field(..., description="Métricas de rendimiento")
    security_status: Dict[str, Any] = Field(..., description="Estado de seguridad")

class AdminUser(BaseModel):
    id: str = Field(..., description="ID del usuario")
    username: str = Field(..., description="Nombre de usuario")
    email: str = Field(..., description="Email")
    full_name: Optional[str] = Field(None, description="Nombre completo")
    role: UserRole = Field(..., description="Rol del usuario")
    status: UserStatus = Field(..., description="Estado del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    last_login: Optional[datetime] = Field(None, description="Último login")
    login_count: int = Field(default=0, description="Número de logins")
    api_calls: int = Field(default=0, description="Llamadas API realizadas")
    storage_used: int = Field(default=0, description="Almacenamiento usado en MB")
    permissions: List[str] = Field(default_factory=list, description="Permisos específicos")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class UserUpdate(BaseModel):
    role: Optional[UserRole] = Field(None, description="Nuevo rol")
    status: Optional[UserStatus] = Field(None, description="Nuevo estado")
    permissions: Optional[List[str]] = Field(None, description="Nuevos permisos")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Nuevos metadatos")
    reason: Optional[str] = Field(None, description="Razón del cambio")

class GlobalSettings(BaseModel):
    site_name: str = Field(default="VokaFlow", description="Nombre del sitio")
    site_description: str = Field(default="AI Communication Platform", description="Descripción")
    max_users: int = Field(default=10000, description="Máximo de usuarios")
    max_api_calls_per_day: int = Field(default=10000, description="Máximo llamadas API por día")
    max_storage_per_user: int = Field(default=1024, description="Máximo almacenamiento por usuario (MB)")
    registration_enabled: bool = Field(default=True, description="Registro habilitado")
    email_verification_required: bool = Field(default=True, description="Verificación email requerida")
    maintenance_mode: MaintenanceMode = Field(default=MaintenanceMode.OFF, description="Modo mantenimiento")
    rate_limiting_enabled: bool = Field(default=True, description="Rate limiting habilitado")
    logging_level: str = Field(default="INFO", description="Nivel de logging")
    backup_enabled: bool = Field(default=True, description="Backups automáticos")
    security_features: Dict[str, bool] = Field(default_factory=dict, description="Características de seguridad")
    api_features: Dict[str, bool] = Field(default_factory=dict, description="Características de API")
    notification_settings: Dict[str, Any] = Field(default_factory=dict, description="Configuración notificaciones")

class AdminLog(BaseModel):
    id: str = Field(..., description="ID del log")
    timestamp: datetime = Field(..., description="Timestamp")
    category: LogCategory = Field(..., description="Categoría del log")
    level: str = Field(..., description="Nivel del log")
    user_id: Optional[str] = Field(None, description="ID del usuario")
    action: str = Field(..., description="Acción realizada")
    resource: Optional[str] = Field(None, description="Recurso afectado")
    ip_address: Optional[str] = Field(None, description="Dirección IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    details: Dict[str, Any] = Field(..., description="Detalles del evento")
    severity: str = Field(default="info", description="Severidad")

class MaintenanceConfig(BaseModel):
    mode: MaintenanceMode = Field(..., description="Modo de mantenimiento")
    start_time: Optional[datetime] = Field(None, description="Hora de inicio")
    end_time: Optional[datetime] = Field(None, description="Hora de fin")
    message: str = Field(default="System under maintenance", description="Mensaje para usuarios")
    allowed_ips: List[str] = Field(default_factory=list, description="IPs permitidas")
    allowed_users: List[str] = Field(default_factory=list, description="Usuarios permitidos")
    redirect_url: Optional[str] = Field(None, description="URL de redirección")
    reason: str = Field(..., description="Razón del mantenimiento")

class GlobalStats(BaseModel):
    users: Dict[str, int] = Field(..., description="Estadísticas de usuarios")
    api: Dict[str, Any] = Field(..., description="Estadísticas de API")
    system: Dict[str, Any] = Field(..., description="Estadísticas del sistema")
    content: Dict[str, int] = Field(..., description="Estadísticas de contenido")
    performance: Dict[str, float] = Field(..., description="Métricas de rendimiento")
    security: Dict[str, int] = Field(..., description="Estadísticas de seguridad")
    storage: Dict[str, Any] = Field(..., description="Estadísticas de almacenamiento")
    geographic: Dict[str, int] = Field(..., description="Distribución geográfica")

class SystemAlert(BaseModel):
    id: str = Field(..., description="ID de la alerta")
    type: str = Field(..., description="Tipo de alerta")
    severity: str = Field(..., description="Severidad")
    title: str = Field(..., description="Título")
    message: str = Field(..., description="Mensaje")
    created_at: datetime = Field(..., description="Fecha de creación")
    resolved: bool = Field(default=False, description="Resuelta")
    resolved_at: Optional[datetime] = Field(None, description="Fecha de resolución")
    metadata: Dict[str, Any] = Field(..., description="Metadatos")

class AdminAction(BaseModel):
    action_id: str = Field(..., description="ID de la acción")
    admin_user_id: str = Field(..., description="ID del admin")
    action_type: str = Field(..., description="Tipo de acción")
    target_type: str = Field(..., description="Tipo de objetivo")
    target_id: str = Field(..., description="ID del objetivo")
    description: str = Field(..., description="Descripción")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    success: bool = Field(..., description="Éxito de la acción")
    error_message: Optional[str] = Field(None, description="Mensaje de error")

class AdminResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class UserManagement(BaseModel):
    total_users: int = Field(..., description="Total de usuarios")
    active_users: int = Field(..., description="Usuarios activos")
    new_users_today: int = Field(..., description="Nuevos usuarios hoy")
    users_by_role: Dict[str, int] = Field(..., description="Usuarios por rol")
    users_by_status: Dict[str, int] = Field(..., description="Usuarios por estado")
    recent_registrations: List[AdminUser] = Field(..., description="Registros recientes")
    top_users_by_activity: List[AdminUser] = Field(..., description="Usuarios más activos")

class SecurityReport(BaseModel):
    failed_logins: int = Field(..., description="Intentos de login fallidos")
    suspicious_activities: int = Field(..., description="Actividades sospechosas")
    blocked_ips: List[str] = Field(..., description="IPs bloqueadas")
    security_events: List[Dict[str, Any]] = Field(..., description="Eventos de seguridad")
    vulnerability_scan: Dict[str, Any] = Field(..., description="Escaneo de vulnerabilidades")
    compliance_status: Dict[str, bool] = Field(..., description="Estado de cumplimiento")

class PerformanceReport(BaseModel):
    response_times: Dict[str, float] = Field(..., description="Tiempos de respuesta")
    throughput: Dict[str, int] = Field(..., description="Throughput")
    error_rates: Dict[str, float] = Field(..., description="Tasas de error")
    resource_utilization: Dict[str, float] = Field(..., description="Utilización de recursos")
    bottlenecks: List[str] = Field(..., description="Cuellos de botella")
    recommendations: List[str] = Field(..., description="Recomendaciones")

class AuditTrail(BaseModel):
    event_id: str = Field(..., description="ID del evento")
    timestamp: datetime = Field(..., description="Timestamp")
    user_id: str = Field(..., description="ID del usuario")
    action: str = Field(..., description="Acción")
    resource: str = Field(..., description="Recurso")
    old_value: Optional[Any] = Field(None, description="Valor anterior")
    new_value: Optional[Any] = Field(None, description="Nuevo valor")
    ip_address: str = Field(..., description="Dirección IP")
    success: bool = Field(..., description="Éxito")
    details: Dict[str, Any] = Field(..., description="Detalles")
