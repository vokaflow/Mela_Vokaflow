#!/usr/bin/env python3
"""
Modelos para Analytics en VokaFlow
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class TimeRange(str, Enum):
    """Rangos de tiempo para análisis"""
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    YEAR = "1y"

class MetricType(str, Enum):
    """Tipos de métricas de rendimiento"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    API_CALLS = "api_calls"
    USERS = "users"
    ERRORS = "errors"

class AnalyticsResponse(BaseModel):
    """Respuesta base para analytics"""
    success: bool = True
    data: Any = {}
    timestamp: datetime = datetime.now()
    message: Optional[str] = None

class UsageStats(BaseModel):
    """Estadísticas de uso del sistema"""
    total_requests: int = 0
    total_users: int = 0 
    active_sessions: int = 0
    avg_response_time: float = 0.0
    peak_memory_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    last_updated: datetime = datetime.now()

class UsageMetrics(BaseModel):
    """Métricas de uso"""
    total_requests: int = 0
    active_users: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    requests_per_hour: Dict[str, int] = {}
    popular_endpoints: List[str] = []

class PerformanceMetrics(BaseModel):
    """Métricas de rendimiento"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = {}
    response_times: Dict[str, float] = {}
    throughput: float = 0.0

class DashboardData(BaseModel):
    """Datos del dashboard"""
    usage: UsageMetrics = UsageMetrics()
    performance: PerformanceMetrics = PerformanceMetrics()
    alerts: List[str] = []
    summary: Dict[str, Any] = {}
    last_updated: datetime = datetime.now()

class SystemMetrics(BaseModel):
    """Métricas del sistema"""
    uptime: str = "00:00:00"
    total_users: int = 0
    active_sessions: int = 0
    database_connections: int = 0
    cache_hit_rate: float = 0.0

class UserAnalytics(BaseModel):
    """Analytics de usuario"""
    user_id: int
    total_sessions: int = 0
    total_requests: int = 0
    avg_session_duration: float = 0.0
    last_activity: Optional[datetime] = None
    preferred_features: List[str] = []

class APIAnalytics(BaseModel):
    """Analytics de API"""
    endpoint: str
    total_calls: int = 0
    avg_response_time: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0
    last_called: Optional[datetime] = None

class ReportData(BaseModel):
    """Datos de reporte"""
    report_id: str
    title: str
    description: Optional[str] = None
    data: Dict[str, Any] = {}
    generated_at: datetime = datetime.now()
    format: str = "json"  # json, csv, pdf

class ExportRequest(BaseModel):
    """Solicitud de exportación"""
    report_type: str
    date_range: Dict[str, str] = {}
    filters: Dict[str, Any] = {}
    format: str = "json"
    email_notification: bool = False

class TrendData(BaseModel):
    """Datos de tendencias"""
    metric_name: str
    time_series: List[Dict[str, Any]] = []
    trend_direction: str = "stable"  # up, down, stable
    percentage_change: float = 0.0
    period: str = "24h"

class ExportResponse(BaseModel):
    """Respuesta de exportación"""
    export_id: str
    status: str = "processing"  # processing, completed, failed
    download_url: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    file_size: Optional[int] = None
    format: str = "json"

class RealtimeData(BaseModel):
    """Datos en tiempo real"""
    active_users: int = 0
    requests_per_second: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    server_status: str = "healthy"  # healthy, warning, critical
    last_events: List[Dict[str, Any]] = []
    timestamp: datetime = datetime.now()
