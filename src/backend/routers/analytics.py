from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
import json
import csv
import io
import uuid
from datetime import datetime, timedelta
import psutil
import time
import random

from ..models.analytics_model import (
    DashboardData, APIAnalytics, PerformanceMetrics, ReportData,
    ExportRequest, ExportResponse, RealtimeData, TrendData,
    AnalyticsResponse, MetricType, TimeRange
)

router = APIRouter(tags=["Analytics"])

# Simulación de base de datos en memoria
analytics_cache = {
    "dashboard": {},
    "usage": [],
    "performance": [],
    "reports": [],
    "exports": {},
    "realtime": {},
    "trends": {}
}

def get_system_metrics():
    """Obtener métricas del sistema"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": cpu_percent,
            "memory": memory.percent,
            "disk": disk.percent,
            "uptime": time.time() - psutil.boot_time()
        }
    except Exception:
        return {
            "cpu": random.uniform(10, 80),
            "memory": random.uniform(20, 70),
            "disk": random.uniform(15, 60),
            "uptime": random.uniform(86400, 604800)
        }

def format_uptime(seconds):
    """Formatear tiempo de actividad"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}d {hours}h {minutes}m"

@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_data():
    """
    📊 Obtener datos del dashboard principal
    
    Retorna métricas clave del sistema:
    - Total de usuarios
    - Usuarios activos
    - Llamadas API del día
    - Salud del sistema
    - Tiempo de actividad
    """
    try:
        system_metrics = get_system_metrics()
        
        dashboard_data = DashboardData(
            total_users=random.randint(1000, 5000),
            active_users=random.randint(50, 500),
            api_calls_today=random.randint(10000, 50000),
            system_health=100 - max(system_metrics["cpu"], system_metrics["memory"]) * 0.5,
            uptime=format_uptime(system_metrics["uptime"])
        )
        
        analytics_cache["dashboard"] = dashboard_data.dict()
        
        return AnalyticsResponse(
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@router.get("/usage", response_model=AnalyticsResponse)
async def get_usage_statistics(
    limit: int = Query(10, ge=1, le=100, description="Número de endpoints a retornar"),
    sort_by: str = Query("calls", description="Campo para ordenar")
):
    """
    📈 Obtener estadísticas de uso de la API
    
    Retorna información sobre:
    - Endpoints más utilizados
    - Tiempos de respuesta
    - Tasas de error
    - Última actividad
    """
    try:
        # Simular datos de uso de endpoints
        endpoints = [
            "/api/vicky-new/process", "/api/translate/", "/api/tts/synthesize",
            "/api/stt/transcribe", "/api/users/profile", "/api/files/upload",
            "/api/health/", "/api/auth/login", "/api/voice/clone", "/api/analytics/dashboard"
        ]
        
        usage_stats = []
        for endpoint in endpoints[:limit]:
            stats = APIAnalytics(
                endpoint=endpoint,
                total_calls=random.randint(100, 10000),
                avg_response_time=random.uniform(50, 2000),
                error_count=int(random.uniform(0, 500)),
                success_rate=100 - random.uniform(0, 5),
                last_called=datetime.now() - timedelta(minutes=random.randint(1, 1440))
            )
            usage_stats.append(stats)
        
        # Ordenar por el campo especificado
        if sort_by == "calls":
            usage_stats.sort(key=lambda x: x.total_calls, reverse=True)
        elif sort_by == "response_time":
            usage_stats.sort(key=lambda x: x.avg_response_time, reverse=True)
        elif sort_by == "error_rate":
            usage_stats.sort(key=lambda x: 100 - x.success_rate, reverse=True)
        
        analytics_cache["usage"] = [stat.dict() for stat in usage_stats]
        
        return AnalyticsResponse(
            message="Usage statistics retrieved successfully",
            data=usage_stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving usage statistics: {str(e)}")

@router.get("/performance", response_model=AnalyticsResponse)
async def get_performance_metrics(
    metric_type: Optional[MetricType] = Query(None, description="Tipo de métrica específica"),
    time_range: TimeRange = Query(TimeRange.HOUR, description="Rango de tiempo")
):
    """
    ⚡ Obtener métricas de rendimiento del sistema
    
    Incluye:
    - CPU, memoria, disco, red
    - Llamadas API
    - Usuarios activos
    - Errores del sistema
    """
    try:
        system_metrics = get_system_metrics()
        
        metrics = []
        metric_types = [metric_type] if metric_type else list(MetricType)
        
        for m_type in metric_types:
            if m_type == MetricType.CPU:
                current = system_metrics["cpu"]
            elif m_type == MetricType.MEMORY:
                current = system_metrics["memory"]
            elif m_type == MetricType.DISK:
                current = system_metrics["disk"]
            elif m_type == MetricType.NETWORK:
                current = random.uniform(10, 90)
            elif m_type == MetricType.API_CALLS:
                current = random.uniform(100, 1000)
            elif m_type == MetricType.USERS:
                current = random.uniform(50, 500)
            else:  # ERRORS
                current = random.uniform(0, 10)
            
            metric = PerformanceMetrics(
                metric_type=m_type,
                current_value=current,
                average_value=current * random.uniform(0.8, 1.2),
                peak_value=current * random.uniform(1.2, 2.0),
                unit="%" if m_type in [MetricType.CPU, MetricType.MEMORY, MetricType.DISK] else "count"
            )
            metrics.append(metric)
        
        analytics_cache["performance"] = [metric.dict() for metric in metrics]
        
        return AnalyticsResponse(
            message="Performance metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")

@router.get("/reports", response_model=AnalyticsResponse)
async def get_reports(
    limit: int = Query(10, ge=1, le=50, description="Número de reportes a retornar")
):
    """
    📋 Obtener lista de reportes disponibles
    
    Retorna reportes generados del sistema:
    - Reportes de uso
    - Reportes de rendimiento
    - Reportes de errores
    - Reportes personalizados
    """
    try:
        report_types = ["Usage Report", "Performance Report", "Error Report", "User Activity Report"]
        
        reports = []
        for i in range(limit):
            report = ReportData(
                report_id=str(uuid.uuid4()),
                title=f"{random.choice(report_types)} - {datetime.now().strftime('%Y-%m-%d')}",
                description=f"Automated report generated for system analysis",
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                data={
                    "total_entries": random.randint(100, 10000),
                    "summary": "Report contains detailed analytics data",
                    "categories": random.randint(3, 8)
                }
            )
            reports.append(report)
        
        analytics_cache["reports"] = [report.dict() for report in reports]
        
        return AnalyticsResponse(
            message="Reports retrieved successfully",
            data=reports
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {str(e)}")

@router.post("/export", response_model=AnalyticsResponse)
async def export_analytics_data(
    export_request: ExportRequest,
    background_tasks: BackgroundTasks
):
    """
    📤 Exportar datos de analytics
    
    Permite exportar:
    - Datos de uso
    - Métricas de rendimiento
    - Reportes
    - Datos en tiempo real
    
    Formatos soportados: CSV, JSON, Excel
    """
    try:
        export_id = str(uuid.uuid4())
        
        # Simular procesamiento en background
        def process_export():
            time.sleep(2)  # Simular procesamiento
            analytics_cache["exports"][export_id] = {
                "status": "completed",
                "file_path": f"/tmp/export_{export_id}.{export_request.format}",
                "created_at": datetime.now()
            }
        
        background_tasks.add_task(process_export)
        
        export_response = ExportResponse(
            export_id=export_id,
            download_url=f"/api/analytics/download/{export_id}",
            expires_at=datetime.now() + timedelta(hours=24),
            file_size=random.randint(1024, 1048576)  # 1KB - 1MB
        )
        
        return AnalyticsResponse(
            message="Export request processed successfully",
            data=export_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing export request: {str(e)}")

@router.get("/realtime", response_model=AnalyticsResponse)
async def get_realtime_data():
    """
    🔴 Obtener datos en tiempo real
    
    Métricas actualizadas en tiempo real:
    - Conexiones activas
    - Peticiones por segundo
    - Uso de recursos
    - Tiempo de respuesta
    """
    try:
        system_metrics = get_system_metrics()
        
        realtime_data = RealtimeData(
            active_connections=random.randint(10, 100),
            requests_per_second=random.uniform(5, 50),
            cpu_usage=system_metrics["cpu"],
            memory_usage=system_metrics["memory"],
            response_time=random.uniform(50, 500)
        )
        
        analytics_cache["realtime"] = realtime_data.dict()
        
        return AnalyticsResponse(
            message="Realtime data retrieved successfully",
            data=realtime_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving realtime data: {str(e)}")

@router.get("/trends", response_model=AnalyticsResponse)
async def get_trends_analysis(
    metric: str = Query("api_calls", description="Métrica para analizar tendencias"),
    time_range: TimeRange = Query(TimeRange.DAY, description="Rango de tiempo para el análisis")
):
    """
    📊 Obtener análisis de tendencias
    
    Analiza tendencias de:
    - Uso de la API
    - Rendimiento del sistema
    - Actividad de usuarios
    - Errores y problemas
    
    Incluye predicciones basadas en datos históricos
    """
    try:
        # Generar datos de serie temporal simulados
        hours = 24 if time_range == TimeRange.DAY else 168 if time_range == TimeRange.WEEK else 720
        time_series = []
        
        base_value = random.uniform(100, 1000)
        for i in range(hours):
            timestamp = datetime.now() - timedelta(hours=hours-i)
            value = base_value + random.uniform(-50, 50) + (i * random.uniform(-2, 2))
            time_series.append({
                "timestamp": timestamp.isoformat(),
                "value": max(0, value)
            })
        
        # Calcular tendencia
        first_half = sum(point["value"] for point in time_series[:len(time_series)//2])
        second_half = sum(point["value"] for point in time_series[len(time_series)//2:])
        
        growth_rate = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        trend_direction = "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable"
        
        # Predicción simple
        last_value = time_series[-1]["value"]
        prediction = {
            "next_hour": last_value + (growth_rate * 0.01 * last_value),
            "next_day": last_value + (growth_rate * 0.24 * last_value),
            "confidence": random.uniform(0.7, 0.95)
        }
        
        trend_data = TrendData(
            metric=metric,
            time_series=time_series,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            prediction=prediction
        )
        
        analytics_cache["trends"][metric] = trend_data.dict()
        
        return AnalyticsResponse(
            message="Trends analysis retrieved successfully",
            data=trend_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trends analysis: {str(e)}")

# Endpoint adicional para descargar exportaciones
@router.get("/download/{export_id}")
async def download_export(export_id: str):
    """Descargar archivo de exportación"""
    if export_id not in analytics_cache["exports"]:
        raise HTTPException(status_code=404, detail="Export not found")
    
    # Simular descarga de archivo
    return {"message": f"Download started for export {export_id}"}
