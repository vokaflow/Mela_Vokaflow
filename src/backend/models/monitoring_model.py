from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import re

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class AlertCategory(str, Enum):
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    APPLICATION = "application"
    NETWORK = "network"
    DATABASE = "database"
    STORAGE = "storage"
    USER = "user"

class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class UptimeStatus(str, Enum):
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class Alert(BaseModel):
    id: str = Field(..., description="ID único de la alerta")
    title: str = Field(..., description="Título de la alerta")
    description: str = Field(..., description="Descripción detallada")
    severity: AlertSeverity = Field(..., description="Severidad de la alerta")
    status: AlertStatus = Field(..., description="Estado de la alerta")
    category: AlertCategory = Field(..., description="Categoría de la alerta")
    source: str = Field(..., description="Fuente que generó la alerta")
    component: str = Field(..., description="Componente afectado")
    metric_name: Optional[str] = Field(None, description="Nombre de la métrica relacionada")
    metric_value: Optional[float] = Field(None, description="Valor de la métrica")
    threshold: Optional[float] = Field(None, description="Umbral que se superó")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de actualización")
    acknowledged_at: Optional[datetime] = Field(None, description="Fecha de reconocimiento")
    resolved_at: Optional[datetime] = Field(None, description="Fecha de resolución")
    acknowledged_by: Optional[str] = Field(None, description="Usuario que reconoció")
    resolved_by: Optional[str] = Field(None, description="Usuario que resolvió")
    tags: List[str] = Field(default_factory=list, description="Etiquetas")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "alert_123456789",
                "title": "High CPU Usage",
                "description": "CPU usage has exceeded 90% for more than 5 minutes",
                "severity": "high",
                "status": "active",
                "category": "performance",
                "source": "system_monitor",
                "component": "api_server",
                "metric_name": "cpu_usage_percent",
                "metric_value": 92.5,
                "threshold": 90.0,
                "created_at": "2023-01-01T00:00:00Z",
                "tags": ["cpu", "performance", "server"],
                "metadata": {
                    "hostname": "api-server-01",
                    "region": "us-east-1"
                }
            }
        }

class AlertCreate(BaseModel):
    title: str = Field(..., description="Título de la alerta")
    description: str = Field(..., description="Descripción detallada")
    severity: AlertSeverity = Field(..., description="Severidad de la alerta")
    category: AlertCategory = Field(..., description="Categoría de la alerta")
    source: str = Field(..., description="Fuente que genera la alerta")
    component: str = Field(..., description="Componente afectado")
    metric_name: Optional[str] = Field(None, description="Nombre de la métrica")
    metric_value: Optional[float] = Field(None, description="Valor actual de la métrica")
    threshold: Optional[float] = Field(None, description="Umbral configurado")
    tags: List[str] = Field(default_factory=list, description="Etiquetas")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    @validator('title')
    def title_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        if len(v) < 5:
            raise ValueError('El título debe tener al menos 5 caracteres')
        if len(v) > 200:
            raise ValueError('El título no puede exceder 200 caracteres')
        return v
    
    @validator('description')
    def description_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('La descripción no puede estar vacía')
        if len(v) < 10:
            raise ValueError('La descripción debe tener al menos 10 caracteres')
        if len(v) > 1000:
            raise ValueError('La descripción no puede exceder 1000 caracteres')
        return v

class Metric(BaseModel):
    name: str = Field(..., description="Nombre de la métrica")
    type: MetricType = Field(..., description="Tipo de métrica")
    value: Union[float, int] = Field(..., description="Valor actual")
    unit: str = Field(..., description="Unidad de medida")
    description: str = Field(..., description="Descripción de la métrica")
    timestamp: datetime = Field(..., description="Timestamp de la medición")
    labels: Dict[str, str] = Field(default_factory=dict, description="Etiquetas de la métrica")
    source: str = Field(..., description="Fuente de la métrica")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "cpu_usage_percent",
                "type": "gauge",
                "value": 75.5,
                "unit": "percent",
                "description": "CPU usage percentage",
                "timestamp": "2023-01-01T00:00:00Z",
                "labels": {
                    "hostname": "api-server-01",
                    "region": "us-east-1"
                },
                "source": "system_monitor"
            }
        }

class MetricSeries(BaseModel):
    name: str = Field(..., description="Nombre de la métrica")
    type: MetricType = Field(..., description="Tipo de métrica")
    unit: str = Field(..., description="Unidad de medida")
    description: str = Field(..., description="Descripción")
    data_points: List[Dict[str, Any]] = Field(..., description="Puntos de datos")
    labels: Dict[str, str] = Field(default_factory=dict, description="Etiquetas")
    source: str = Field(..., description="Fuente")
    start_time: datetime = Field(..., description="Tiempo de inicio")
    end_time: datetime = Field(..., description="Tiempo de fin")
    interval: str = Field(..., description="Intervalo de muestreo")

class SystemMetrics(BaseModel):
    cpu: Dict[str, float] = Field(..., description="Métricas de CPU")
    memory: Dict[str, float] = Field(..., description="Métricas de memoria")
    disk: Dict[str, float] = Field(..., description="Métricas de disco")
    network: Dict[str, float] = Field(..., description="Métricas de red")
    processes: Dict[str, int] = Field(..., description="Métricas de procesos")
    load_average: List[float] = Field(..., description="Promedio de carga")
    timestamp: datetime = Field(..., description="Timestamp de las métricas")

class ApplicationMetrics(BaseModel):
    api_requests_total: int = Field(..., description="Total de peticiones API")
    api_requests_per_second: float = Field(..., description="Peticiones por segundo")
    api_response_time_avg: float = Field(..., description="Tiempo de respuesta promedio")
    api_response_time_p95: float = Field(..., description="Percentil 95 tiempo respuesta")
    api_error_rate: float = Field(..., description="Tasa de error")
    active_connections: int = Field(..., description="Conexiones activas")
    database_connections: int = Field(..., description="Conexiones a BD")
    cache_hit_rate: float = Field(..., description="Tasa de acierto de caché")
    queue_size: int = Field(..., description="Tamaño de cola")
    timestamp: datetime = Field(..., description="Timestamp de las métricas")

class UptimeRecord(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp del registro")
    status: UptimeStatus = Field(..., description="Estado del servicio")
    response_time: Optional[float] = Field(None, description="Tiempo de respuesta (ms)")
    status_code: Optional[int] = Field(None, description="Código de estado HTTP")
    error_message: Optional[str] = Field(None, description="Mensaje de error")
    check_type: str = Field(..., description="Tipo de verificación")
    endpoint: str = Field(..., description="Endpoint verificado")

class UptimeStats(BaseModel):
    service_name: str = Field(..., description="Nombre del servicio")
    current_status: UptimeStatus = Field(..., description="Estado actual")
    uptime_percentage: float = Field(..., description="Porcentaje de tiempo activo")
    total_checks: int = Field(..., description="Total de verificaciones")
    successful_checks: int = Field(..., description="Verificaciones exitosas")
    failed_checks: int = Field(..., description="Verificaciones fallidas")
    avg_response_time: float = Field(..., description="Tiempo de respuesta promedio")
    last_check: datetime = Field(..., description="Última verificación")
    last_downtime: Optional[datetime] = Field(None, description="Último tiempo de inactividad")
    incidents_count: int = Field(..., description="Número de incidentes")
    mttr: Optional[float] = Field(None, description="Tiempo medio de recuperación (minutos)")
    mtbf: Optional[float] = Field(None, description="Tiempo medio entre fallos (horas)")

class MonitoringDashboard(BaseModel):
    system_health: Dict[str, Any] = Field(..., description="Salud del sistema")
    active_alerts: List[Alert] = Field(..., description="Alertas activas")
    key_metrics: Dict[str, Metric] = Field(..., description="Métricas clave")
    uptime_summary: Dict[str, UptimeStats] = Field(..., description="Resumen de uptime")
    performance_summary: Dict[str, float] = Field(..., description="Resumen de rendimiento")
    resource_utilization: Dict[str, float] = Field(..., description="Utilización de recursos")
    recent_incidents: List[Dict[str, Any]] = Field(..., description="Incidentes recientes")
    trends: Dict[str, List[float]] = Field(..., description="Tendencias")

class AlertRule(BaseModel):
    id: str = Field(..., description="ID de la regla")
    name: str = Field(..., description="Nombre de la regla")
    metric_name: str = Field(..., description="Métrica a monitorear")
    condition: str = Field(..., description="Condición (>, <, ==, etc.)")
    threshold: float = Field(..., description="Umbral")
    severity: AlertSeverity = Field(..., description="Severidad de la alerta")
    category: AlertCategory = Field(..., description="Categoría")
    enabled: bool = Field(default=True, description="Regla habilitada")
    evaluation_interval: int = Field(..., description="Intervalo de evaluación (segundos)")
    for_duration: int = Field(..., description="Duración antes de alertar (segundos)")
    labels: Dict[str, str] = Field(default_factory=dict, description="Etiquetas")
    annotations: Dict[str, str] = Field(default_factory=dict, description="Anotaciones")

class MonitoringResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheck(BaseModel):
    service: str = Field(..., description="Nombre del servicio")
    status: str = Field(..., description="Estado del servicio")
    timestamp: datetime = Field(..., description="Timestamp de la verificación")
    response_time: float = Field(..., description="Tiempo de respuesta")
    details: Dict[str, Any] = Field(..., description="Detalles adicionales")

class PerformanceMetrics(BaseModel):
    throughput: float = Field(..., description="Throughput (req/s)")
    latency_p50: float = Field(..., description="Latencia percentil 50")
    latency_p95: float = Field(..., description="Latencia percentil 95")
    latency_p99: float = Field(..., description="Latencia percentil 99")
    error_rate: float = Field(..., description="Tasa de error")
    cpu_usage: float = Field(..., description="Uso de CPU")
    memory_usage: float = Field(..., description="Uso de memoria")
    disk_usage: float = Field(..., description="Uso de disco")
    network_io: Dict[str, float] = Field(..., description="I/O de red")
    timestamp: datetime = Field(..., description="Timestamp")

class AlertSummary(BaseModel):
    total_alerts: int = Field(..., description="Total de alertas")
    active_alerts: int = Field(..., description="Alertas activas")
    critical_alerts: int = Field(..., description="Alertas críticas")
    high_alerts: int = Field(..., description="Alertas altas")
    medium_alerts: int = Field(..., description="Alertas medias")
    low_alerts: int = Field(..., description="Alertas bajas")
    alerts_by_category: Dict[str, int] = Field(..., description="Alertas por categoría")
    alerts_by_component: Dict[str, int] = Field(..., description="Alertas por componente")
    recent_alerts: List[Alert] = Field(..., description="Alertas recientes")
    resolved_today: int = Field(..., description="Alertas resueltas hoy")
    avg_resolution_time: float = Field(..., description="Tiempo promedio de resolución")

class ServiceStatus(BaseModel):
    name: str = Field(..., description="Nombre del servicio")
    status: UptimeStatus = Field(..., description="Estado actual")
    uptime: float = Field(..., description="Tiempo de actividad (%)")
    last_check: datetime = Field(..., description="Última verificación")
    response_time: float = Field(..., description="Tiempo de respuesta")
    incidents: int = Field(..., description="Número de incidentes")
    dependencies: List[str] = Field(..., description="Dependencias")
    health_checks: List[HealthCheck] = Field(..., description="Verificaciones de salud")
