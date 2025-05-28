from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ProcessStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    SLEEPING = "sleeping"
    ZOMBIE = "zombie"
    DISK_SLEEP = "disk_sleep"

class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    DATABASE = "database"
    CONFIG = "config"

class SystemInfo(BaseModel):
    hostname: str = Field(..., description="Nombre del host")
    platform: str = Field(..., description="Plataforma del sistema")
    architecture: str = Field(..., description="Arquitectura del procesador")
    python_version: str = Field(..., description="Versión de Python")
    app_version: str = Field(..., description="Versión de la aplicación")
    uptime: str = Field(..., description="Tiempo de actividad")
    boot_time: datetime = Field(..., description="Tiempo de arranque")
    timezone: str = Field(..., description="Zona horaria")
    cpu_count: int = Field(..., description="Número de CPUs")
    memory_total: int = Field(..., description="Memoria total en bytes")
    disk_total: int = Field(..., description="Espacio total en disco")
    network_interfaces: List[Dict[str, Any]] = Field(..., description="Interfaces de red")

class SystemMetrics(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de las métricas")
    cpu_usage: float = Field(..., ge=0, le=100, description="Uso de CPU %")
    memory_usage: float = Field(..., ge=0, le=100, description="Uso de memoria %")
    disk_usage: float = Field(..., ge=0, le=100, description="Uso de disco %")
    network_io: Dict[str, int] = Field(..., description="I/O de red")
    disk_io: Dict[str, int] = Field(..., description="I/O de disco")
    load_average: List[float] = Field(..., description="Promedio de carga")
    active_connections: int = Field(..., description="Conexiones activas")
    processes_count: int = Field(..., description="Número de procesos")
    threads_count: int = Field(..., description="Número de hilos")
    file_descriptors: int = Field(..., description="Descriptores de archivo abiertos")

class SystemProcess(BaseModel):
    pid: int = Field(..., description="ID del proceso")
    name: str = Field(..., description="Nombre del proceso")
    status: ProcessStatus = Field(..., description="Estado del proceso")
    cpu_percent: float = Field(..., description="Uso de CPU %")
    memory_percent: float = Field(..., description="Uso de memoria %")
    memory_rss: int = Field(..., description="Memoria RSS en bytes")
    create_time: datetime = Field(..., description="Tiempo de creación")
    cmdline: List[str] = Field(..., description="Línea de comandos")
    username: str = Field(..., description="Usuario propietario")
    num_threads: int = Field(..., description="Número de hilos")

class SystemLog(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp del log")
    level: LogLevel = Field(..., description="Nivel del log")
    component: str = Field(..., description="Componente que generó el log")
    message: str = Field(..., description="Mensaje del log")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")
    source_file: Optional[str] = Field(None, description="Archivo fuente")
    line_number: Optional[int] = Field(None, description="Número de línea")

class BackupInfo(BaseModel):
    id: str = Field(..., description="ID del backup")
    type: BackupType = Field(..., description="Tipo de backup")
    status: str = Field(..., description="Estado del backup")
    created_at: datetime = Field(..., description="Fecha de creación")
    size: int = Field(..., description="Tamaño en bytes")
    file_path: str = Field(..., description="Ruta del archivo")
    checksum: str = Field(..., description="Checksum del archivo")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del backup")

class SystemConfig(BaseModel):
    debug_mode: bool = Field(default=False, description="Modo debug")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Nivel de logging")
    max_connections: int = Field(default=100, description="Máximo de conexiones")
    timeout_seconds: int = Field(default=30, description="Timeout en segundos")
    cache_enabled: bool = Field(default=True, description="Cache habilitado")
    cache_ttl: int = Field(default=3600, description="TTL del cache")
    backup_enabled: bool = Field(default=True, description="Backups automáticos")
    backup_interval: int = Field(default=86400, description="Intervalo de backup")
    monitoring_enabled: bool = Field(default=True, description="Monitoreo habilitado")
    alerts_enabled: bool = Field(default=True, description="Alertas habilitadas")
    maintenance_mode: bool = Field(default=False, description="Modo mantenimiento")

class SystemOperation(BaseModel):
    operation: str = Field(..., description="Tipo de operación")
    status: str = Field(..., description="Estado de la operación")
    started_at: datetime = Field(..., description="Inicio de la operación")
    completed_at: Optional[datetime] = Field(None, description="Fin de la operación")
    progress: float = Field(default=0, ge=0, le=100, description="Progreso %")
    message: str = Field(..., description="Mensaje de estado")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")

class SystemHealth(BaseModel):
    status: SystemStatus = Field(..., description="Estado general del sistema")
    score: float = Field(..., ge=0, le=100, description="Puntuación de salud")
    checks: List[Dict[str, Any]] = Field(..., description="Verificaciones realizadas")
    warnings: List[str] = Field(default_factory=list, description="Advertencias")
    errors: List[str] = Field(default_factory=list, description="Errores")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")
    last_check: datetime = Field(..., description="Última verificación")

class SystemResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class RestartRequest(BaseModel):
    force: bool = Field(default=False, description="Forzar reinicio")
    delay_seconds: int = Field(default=5, description="Retraso antes del reinicio")
    reason: Optional[str] = Field(None, description="Razón del reinicio")

class ShutdownRequest(BaseModel):
    force: bool = Field(default=False, description="Forzar apagado")
    delay_seconds: int = Field(default=10, description="Retraso antes del apagado")
    reason: Optional[str] = Field(None, description="Razón del apagado")

class BackupRequest(BaseModel):
    type: BackupType = Field(..., description="Tipo de backup")
    include_data: bool = Field(default=True, description="Incluir datos")
    include_config: bool = Field(default=True, description="Incluir configuración")
    include_logs: bool = Field(default=False, description="Incluir logs")
    compression: bool = Field(default=True, description="Comprimir backup")
    encryption: bool = Field(default=False, description="Encriptar backup")

class LogQuery(BaseModel):
    level: Optional[LogLevel] = Field(None, description="Filtrar por nivel")
    component: Optional[str] = Field(None, description="Filtrar por componente")
    start_time: Optional[datetime] = Field(None, description="Tiempo de inicio")
    end_time: Optional[datetime] = Field(None, description="Tiempo de fin")
    search: Optional[str] = Field(None, description="Buscar en mensaje")
    limit: int = Field(default=100, ge=1, le=1000, description="Límite de resultados")
