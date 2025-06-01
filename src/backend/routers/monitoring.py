from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import List, Dict, Any, Optional
import uuid
import random
import psutil
import time
from datetime import datetime, timedelta

from ..models.monitoring_model import (
    Alert, AlertCreate, Metric, MetricSeries, SystemMetrics, ApplicationMetrics,
    UptimeRecord, UptimeStats, MonitoringDashboard, AlertRule, MonitoringResponse,
    HealthCheck, PerformanceMetrics, AlertSummary, ServiceStatus,
    AlertSeverity, AlertStatus, AlertCategory, MetricType, UptimeStatus
)

router = APIRouter(tags=["Monitoring"])

# Simulación de base de datos en memoria
monitoring_db = {
    "alerts": {},
    "metrics": [],
    "uptime_records": [],
    "alert_rules": {},
    "health_checks": []
}

# Variables para simular métricas en tiempo real
start_time = datetime.now()
request_count = 0
error_count = 0

def generate_system_metrics() -> SystemMetrics:
    """Genera métricas del sistema usando psutil"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memoria
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Red
        network_io = psutil.net_io_counters()
        
        # Procesos
        process_count = len(psutil.pids())
        
        # Load average (solo en sistemas Unix)
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            load_avg = [0.0, 0.0, 0.0]  # Windows no tiene load average
        
        return SystemMetrics(
            cpu={
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else 0
            },
            memory={
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_percent": swap.percent
            },
            disk={
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2),
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0
            },
            network={
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "errors_in": network_io.errin,
                "errors_out": network_io.errout
            },
            processes={
                "total": process_count,
                "running": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running']),
                "sleeping": len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'sleeping'])
            },
            load_average=load_avg,
            timestamp=datetime.now()
        )
    except Exception as e:
        # Fallback con datos simulados si psutil falla
        return SystemMetrics(
            cpu={"usage_percent": random.uniform(10, 80), "count": 4, "frequency_mhz": 2400},
            memory={"total_gb": 16, "used_gb": random.uniform(4, 12), "available_gb": random.uniform(4, 12), "usage_percent": random.uniform(25, 75), "swap_total_gb": 8, "swap_used_gb": random.uniform(0, 2), "swap_percent": random.uniform(0, 25)},
            disk={"total_gb": 500, "used_gb": random.uniform(100, 400), "free_gb": random.uniform(100, 400), "usage_percent": random.uniform(20, 80), "read_bytes": random.randint(1000000, 10000000), "write_bytes": random.randint(1000000, 10000000)},
            network={"bytes_sent": random.randint(1000000, 100000000), "bytes_recv": random.randint(1000000, 100000000), "packets_sent": random.randint(1000, 100000), "packets_recv": random.randint(1000, 100000), "errors_in": random.randint(0, 10), "errors_out": random.randint(0, 10)},
            processes={"total": random.randint(100, 300), "running": random.randint(10, 50), "sleeping": random.randint(50, 200)},
            load_average=[random.uniform(0.1, 2.0), random.uniform(0.1, 2.0), random.uniform(0.1, 2.0)],
            timestamp=datetime.now()
        )

def generate_application_metrics() -> ApplicationMetrics:
    """Genera métricas de la aplicación"""
    global request_count, error_count
    
    # Simular incremento de peticiones
    request_count += random.randint(10, 100)
    error_count += random.randint(0, 5)
    
    uptime_seconds = (datetime.now() - start_time).total_seconds()
    requests_per_second = request_count / max(uptime_seconds, 1)
    
    return ApplicationMetrics(
        api_requests_total=request_count,
        api_requests_per_second=round(requests_per_second, 2),
        api_response_time_avg=random.uniform(100, 500),
        api_response_time_p95=random.uniform(500, 2000),
        api_error_rate=round((error_count / max(request_count, 1)) * 100, 2),
        active_connections=random.randint(10, 100),
        database_connections=random.randint(5, 50),
        cache_hit_rate=random.uniform(80, 95),
        queue_size=random.randint(0, 50),
        timestamp=datetime.now()
    )

def initialize_sample_alerts():
    """Inicializa alertas de ejemplo si la base de datos está vacía"""
    if not monitoring_db["alerts"]:
        # Crear algunas alertas de ejemplo
        severities = list(AlertSeverity)
        statuses = list(AlertStatus)
        categories = list(AlertCategory)
        
        sample_alerts = [
            {
                "title": "High CPU Usage",
                "description": "CPU usage has exceeded 90% for more than 5 minutes",
                "severity": AlertSeverity.HIGH,
                "category": AlertCategory.PERFORMANCE,
                "source": "system_monitor",
                "component": "api_server",
                "metric_name": "cpu_usage_percent",
                "metric_value": 92.5,
                "threshold": 90.0
            },
            {
                "title": "Memory Usage Critical",
                "description": "Memory usage has reached 95% capacity",
                "severity": AlertSeverity.CRITICAL,
                "category": AlertCategory.SYSTEM,
                "source": "system_monitor",
                "component": "database_server",
                "metric_name": "memory_usage_percent",
                "metric_value": 95.2,
                "threshold": 95.0
            },
            {
                "title": "API Response Time High",
                "description": "API response time has exceeded 2 seconds",
                "severity": AlertSeverity.MEDIUM,
                "category": AlertCategory.APPLICATION,
                "source": "api_monitor",
                "component": "api_gateway",
                "metric_name": "response_time_ms",
                "metric_value": 2150.0,
                "threshold": 2000.0
            },
            {
                "title": "Failed Login Attempts",
                "description": "Multiple failed login attempts detected from same IP",
                "severity": AlertSeverity.HIGH,
                "category": AlertCategory.SECURITY,
                "source": "security_monitor",
                "component": "auth_service",
                "metric_name": "failed_logins",
                "metric_value": 15.0,
                "threshold": 10.0
            },
            {
                "title": "Disk Space Low",
                "description": "Disk space usage has exceeded 85%",
                "severity": AlertSeverity.MEDIUM,
                "category": AlertCategory.STORAGE,
                "source": "system_monitor",
                "component": "file_server",
                "metric_name": "disk_usage_percent",
                "metric_value": 87.3,
                "threshold": 85.0
            }
        ]
        
        for i, alert_data in enumerate(sample_alerts):
            alert_id = f"alert_{uuid.uuid4().hex[:8]}"
            
            alert = Alert(
                id=alert_id,
                title=alert_data["title"],
                description=alert_data["description"],
                severity=alert_data["severity"],
                status=random.choice([AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]),
                category=alert_data["category"],
                source=alert_data["source"],
                component=alert_data["component"],
                metric_name=alert_data["metric_name"],
                metric_value=alert_data["metric_value"],
                threshold=alert_data["threshold"],
                created_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
                updated_at=datetime.now() - timedelta(minutes=random.randint(1, 60)) if random.random() > 0.5 else None,
                acknowledged_at=datetime.now() - timedelta(minutes=random.randint(1, 30)) if random.random() > 0.7 else None,
                resolved_at=None,
                acknowledged_by=f"admin_{random.randint(1, 3)}" if random.random() > 0.7 else None,
                resolved_by=None,
                tags=[alert_data["category"].value, alert_data["component"], "automated"],
                metadata={
                    "hostname": f"server-{random.randint(1, 5)}",
                    "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                    "environment": random.choice(["production", "staging"])
                }
            )
            
            monitoring_db["alerts"][alert_id] = alert.dict()

def generate_uptime_records():
    """Genera registros de uptime de ejemplo"""
    if len(monitoring_db["uptime_records"]) < 100:
        services = ["api", "database", "cache", "auth", "files"]
        endpoints = [
            "/health",
            "/api/health",
            "/api/status",
            "/ping",
            "/ready"
        ]
        
        for _ in range(100):
            service = random.choice(services)
            endpoint = random.choice(endpoints)
            status = random.choice(list(UptimeStatus))
            
            record = UptimeRecord(
                timestamp=datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                status=status,
                response_time=random.uniform(50, 500) if status == UptimeStatus.UP else None,
                status_code=200 if status == UptimeStatus.UP else random.choice([500, 502, 503, 504]),
                error_message=None if status == UptimeStatus.UP else "Service unavailable",
                check_type=f"{service}_health_check",
                endpoint=f"https://{service}.vokaflow.com{endpoint}"
            )
            
            monitoring_db["uptime_records"].append(record.dict())

@router.get("/alerts", response_model=MonitoringResponse)
async def get_system_alerts(
    severity: Optional[AlertSeverity] = Query(None, description="Filtrar por severidad"),
    status: Optional[AlertStatus] = Query(None, description="Filtrar por estado"),
    category: Optional[AlertCategory] = Query(None, description="Filtrar por categoría"),
    component: Optional[str] = Query(None, description="Filtrar por componente"),
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    🚨 Obtener alertas del sistema
    
    Devuelve una lista de alertas del sistema con opciones de filtrado.
    Incluye alertas activas, reconocidas y resueltas.
    """
    try:
        initialize_sample_alerts()
        
        # Filtrar alertas
        filtered_alerts = []
        for alert_data in monitoring_db["alerts"].values():
            alert = Alert(**alert_data)
            
            # Aplicar filtros
            if severity and alert.severity != severity:
                continue
            if status and alert.status != status:
                continue
            if category and alert.category != category:
                continue
            if component and component.lower() not in alert.component.lower():
                continue
            
            filtered_alerts.append(alert)
        
        # Ordenar por fecha de creación (más recientes primero)
        filtered_alerts.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginación
        total_filtered = len(filtered_alerts)
        paginated_alerts = filtered_alerts[offset:offset + limit]
        
        # Generar resumen de alertas
        alert_summary = AlertSummary(
            total_alerts=len(monitoring_db["alerts"]),
            active_alerts=len([a for a in monitoring_db["alerts"].values() if a["status"] == "active"]),
            critical_alerts=len([a for a in monitoring_db["alerts"].values() if a["severity"] == "critical"]),
            high_alerts=len([a for a in monitoring_db["alerts"].values() if a["severity"] == "high"]),
            medium_alerts=len([a for a in monitoring_db["alerts"].values() if a["severity"] == "medium"]),
            low_alerts=len([a for a in monitoring_db["alerts"].values() if a["severity"] == "low"]),
            alerts_by_category={},
            alerts_by_component={},
            recent_alerts=paginated_alerts[:5],
            resolved_today=len([a for a in monitoring_db["alerts"].values() 
                              if a.get("resolved_at") and 
                              datetime.fromisoformat(a["resolved_at"].replace("Z", "+00:00")).date() == datetime.now().date()]),
            avg_resolution_time=random.uniform(15, 120)  # minutos
        )
        
        # Contar por categoría y componente
        for alert_data in monitoring_db["alerts"].values():
            cat = alert_data["category"]
            comp = alert_data["component"]
            alert_summary.alerts_by_category[cat] = alert_summary.alerts_by_category.get(cat, 0) + 1
            alert_summary.alerts_by_component[comp] = alert_summary.alerts_by_component.get(comp, 0) + 1
        
        return MonitoringResponse(
            message=f"Retrieved {len(paginated_alerts)} alerts",
            data={
                "alerts": paginated_alerts,
                "summary": alert_summary,
                "total": total_filtered,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_filtered
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@router.get("/metrics", response_model=MonitoringResponse)
async def get_monitoring_metrics(
    metric_type: Optional[str] = Query(None, description="Tipo de métrica: system, application, performance"),
    time_range: str = Query("1h", description="Rango de tiempo: 1h, 6h, 24h, 7d"),
    include_historical: bool = Query(False, description="Incluir datos históricos")
):
    """
    📊 Obtener métricas de monitoreo
    
    Devuelve métricas del sistema, aplicación y rendimiento.
    Incluye datos en tiempo real y históricos opcionales.
    """
    try:
        # Generar métricas actuales
        system_metrics = generate_system_metrics()
        app_metrics = generate_application_metrics()
        
        # Métricas de rendimiento
        performance_metrics = PerformanceMetrics(
            throughput=app_metrics.api_requests_per_second,
            latency_p50=random.uniform(100, 300),
            latency_p95=app_metrics.api_response_time_p95,
            latency_p99=random.uniform(1000, 3000),
            error_rate=app_metrics.api_error_rate,
            cpu_usage=system_metrics.cpu["usage_percent"],
            memory_usage=system_metrics.memory["usage_percent"],
            disk_usage=system_metrics.disk["usage_percent"],
            network_io={
                "bytes_sent_per_sec": random.uniform(1000, 10000),
                "bytes_recv_per_sec": random.uniform(1000, 10000)
            },
            timestamp=datetime.now()
        )
        
        # Métricas clave como objetos Metric
        key_metrics = {
            "cpu_usage": Metric(
                name="cpu_usage_percent",
                type=MetricType.GAUGE,
                value=system_metrics.cpu["usage_percent"],
                unit="percent",
                description="CPU usage percentage",
                timestamp=datetime.now(),
                labels={"component": "system"},
                source="system_monitor"
            ),
            "memory_usage": Metric(
                name="memory_usage_percent",
                type=MetricType.GAUGE,
                value=system_metrics.memory["usage_percent"],
                unit="percent",
                description="Memory usage percentage",
                timestamp=datetime.now(),
                labels={"component": "system"},
                source="system_monitor"
            ),
            "api_requests": Metric(
                name="api_requests_per_second",
                type=MetricType.GAUGE,
                value=app_metrics.api_requests_per_second,
                unit="requests/sec",
                description="API requests per second",
                timestamp=datetime.now(),
                labels={"component": "api"},
                source="api_monitor"
            ),
            "response_time": Metric(
                name="api_response_time_avg",
                type=MetricType.GAUGE,
                value=app_metrics.api_response_time_avg,
                unit="milliseconds",
                description="Average API response time",
                timestamp=datetime.now(),
                labels={"component": "api"},
                source="api_monitor"
            )
        }
        
        # Datos históricos si se solicitan
        historical_data = {}
        if include_historical:
            # Generar datos históricos simulados
            time_points = []
            now = datetime.now()
            
            if time_range == "1h":
                points = 60
                interval = timedelta(minutes=1)
            elif time_range == "6h":
                points = 72
                interval = timedelta(minutes=5)
            elif time_range == "24h":
                points = 96
                interval = timedelta(minutes=15)
            else:  # 7d
                points = 168
                interval = timedelta(hours=1)
            
            for i in range(points):
                time_points.append(now - (interval * (points - i)))
            
            # Generar series temporales para métricas clave
            historical_data = {
                "cpu_usage": {
                    "timestamps": [t.isoformat() for t in time_points],
                    "values": [random.uniform(10, 80) for _ in time_points]
                },
                "memory_usage": {
                    "timestamps": [t.isoformat() for t in time_points],
                    "values": [random.uniform(20, 70) for _ in time_points]
                },
                "api_requests": {
                    "timestamps": [t.isoformat() for t in time_points],
                    "values": [random.uniform(10, 100) for _ in time_points]
                },
                "response_time": {
                    "timestamps": [t.isoformat() for t in time_points],
                    "values": [random.uniform(100, 500) for _ in time_points]
                }
            }
        
        # Filtrar por tipo de métrica si se especifica
        response_data = {
            "current_metrics": {
                "system": system_metrics if not metric_type or metric_type == "system" else None,
                "application": app_metrics if not metric_type or metric_type == "application" else None,
                "performance": performance_metrics if not metric_type or metric_type == "performance" else None
            },
            "key_metrics": key_metrics,
            "time_range": time_range,
            "last_updated": datetime.now()
        }
        
        if include_historical:
            response_data["historical_data"] = historical_data
        
        return MonitoringResponse(
            message="Monitoring metrics retrieved successfully",
            data=response_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")

@router.post("/alert", response_model=MonitoringResponse, status_code=201)
async def create_alert(alert_create: AlertCreate):
    """
    🚨 Crear nueva alerta
    
    Crea una nueva alerta en el sistema de monitoreo.
    La alerta se activará inmediatamente y se notificará según la configuración.
    """
    try:
        # Generar ID único
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        
        # Crear objeto alerta
        alert = Alert(
            id=alert_id,
            title=alert_create.title,
            description=alert_create.description,
            severity=alert_create.severity,
            status=AlertStatus.ACTIVE,
            category=alert_create.category,
            source=alert_create.source,
            component=alert_create.component,
            metric_name=alert_create.metric_name,
            metric_value=alert_create.metric_value,
            threshold=alert_create.threshold,
            created_at=datetime.now(),
            updated_at=None,
            acknowledged_at=None,
            resolved_at=None,
            acknowledged_by=None,
            resolved_by=None,
            tags=alert_create.tags,
            metadata=alert_create.msg_metadata or {
                "created_by": "api",
                "created_at": datetime.now().isoformat(),
                "auto_generated": False
            }
        )
        
        # Guardar en la base de datos
        monitoring_db["alerts"][alert_id] = alert.dict()
        
        # Determinar acciones automáticas basadas en severidad
        auto_actions = []
        if alert.severity == AlertSeverity.CRITICAL:
            auto_actions = ["notify_oncall", "create_incident", "escalate"]
        elif alert.severity == AlertSeverity.HIGH:
            auto_actions = ["notify_team", "create_ticket"]
        elif alert.severity == AlertSeverity.MEDIUM:
            auto_actions = ["notify_team"]
        else:
            auto_actions = ["log_only"]
        
        return MonitoringResponse(
            message="Alert created successfully",
            data={
                "alert": alert,
                "auto_actions": auto_actions,
                "notification_sent": alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH],
                "escalation_required": alert.severity == AlertSeverity.CRITICAL
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

@router.get("/uptime", response_model=MonitoringResponse)
async def get_uptime_status(
    service: Optional[str] = Query(None, description="Servicio específico"),
    time_range: str = Query("24h", description="Rango de tiempo: 1h, 24h, 7d, 30d")
):
    """
    ⏱️ Obtener tiempo de actividad
    
    Devuelve estadísticas de tiempo de actividad para todos los servicios
    o un servicio específico. Incluye métricas de disponibilidad y rendimiento.
    """
    try:
        generate_uptime_records()
        
        # Definir servicios monitoreados
        services = ["api", "database", "cache", "auth", "files", "storage", "analytics"]
        
        # Calcular rango de tiempo
        now = datetime.now()
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "24h":
            start_time = now - timedelta(hours=24)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        else:  # 30d
            start_time = now - timedelta(days=30)
        
        # Filtrar registros por rango de tiempo
        filtered_records = [
            r for r in monitoring_db["uptime_records"]
            if datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")) >= start_time
        ]
        
        # Calcular estadísticas por servicio
        service_stats = {}
        
        for svc in services:
            if service and svc != service:
                continue
            
            # Filtrar registros del servicio
            service_records = [r for r in filtered_records if svc in r["check_type"]]
            
            if not service_records:
                # Generar datos simulados si no hay registros
                service_records = []
                for i in range(random.randint(50, 200)):
                    record = {
                        "timestamp": (start_time + timedelta(minutes=random.randint(0, int((now - start_time).total_seconds() / 60)))).isoformat(),
                        "status": random.choice(["up", "up", "up", "up", "down"]),  # 80% uptime
                        "response_time": random.uniform(50, 300),
                        "status_code": 200 if random.random() > 0.1 else random.choice([500, 502, 503]),
                        "check_type": f"{svc}_health_check",
                        "endpoint": f"https://{svc}.vokaflow.com/health"
                    }
                    service_records.append(record)
            
            # Calcular estadísticas
            total_checks = len(service_records)
            successful_checks = len([r for r in service_records if r["status"] == "up"])
            failed_checks = total_checks - successful_checks
            
            uptime_percentage = (successful_checks / total_checks * 100) if total_checks > 0 else 0
            
            # Tiempo de respuesta promedio
            response_times = [r["response_time"] for r in service_records if r.get("response_time")]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Estado actual (último registro)
            current_status = UptimeStatus.UP
            if service_records:
                last_record = max(service_records, key=lambda x: x["timestamp"])
                current_status = UptimeStatus(last_record["status"])
            
            # Último tiempo de inactividad
            last_downtime = None
            down_records = [r for r in service_records if r["status"] == "down"]
            if down_records:
                last_downtime = max(down_records, key=lambda x: x["timestamp"])["timestamp"]
            
            # Contar incidentes (períodos continuos de inactividad)
            incidents_count = 0
            was_down = False
            for record in sorted(service_records, key=lambda x: x["timestamp"]):
                if record["status"] == "down" and not was_down:
                    incidents_count += 1
                    was_down = True
                elif record["status"] == "up":
                    was_down = False
            
            # MTTR y MTBF simulados
            mttr = random.uniform(5, 30) if incidents_count > 0 else None  # minutos
            mtbf = random.uniform(24, 168) if incidents_count > 1 else None  # horas
            
            service_stats[svc] = UptimeStats(
                service_name=svc,
                current_status=current_status,
                uptime_percentage=round(uptime_percentage, 2),
                total_checks=total_checks,
                successful_checks=successful_checks,
                failed_checks=failed_checks,
                avg_response_time=round(avg_response_time, 2),
                last_check=datetime.now() - timedelta(minutes=random.randint(1, 10)),
                last_downtime=datetime.fromisoformat(last_downtime.replace("Z", "+00:00")) if last_downtime else None,
                incidents_count=incidents_count,
                mttr=mttr,
                mtbf=mtbf
            )
        
        # Estadísticas globales
        if not service:
            all_checks = sum(stats.total_checks for stats in service_stats.values())
            all_successful = sum(stats.successful_checks for stats in service_stats.values())
            global_uptime = (all_successful / all_checks * 100) if all_checks > 0 else 0
            
            global_stats = {
                "overall_uptime": round(global_uptime, 2),
                "services_up": len([s for s in service_stats.values() if s.current_status == UptimeStatus.UP]),
                "services_down": len([s for s in service_stats.values() if s.current_status == UptimeStatus.DOWN]),
                "total_incidents": sum(s.incidents_count for s in service_stats.values()),
                "avg_response_time": round(sum(s.avg_response_time for s in service_stats.values()) / len(service_stats), 2) if service_stats else 0
            }
        else:
            global_stats = None
        
        # Crear registros de uptime recientes
        recent_records = sorted(filtered_records, key=lambda x: x["timestamp"], reverse=True)[:20]
        recent_uptime_records = [UptimeRecord(**r) for r in recent_records]
        
        return MonitoringResponse(
            message=f"Uptime statistics for {time_range} retrieved successfully",
            data={
                "service_statistics": service_stats,
                "global_statistics": global_stats,
                "recent_records": recent_uptime_records,
                "time_range": {
                    "period": time_range,
                    "start_time": start_time,
                    "end_time": now,
                    "total_duration_hours": round((now - start_time).total_seconds() / 3600, 2)
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving uptime status: {str(e)}")

# Endpoints adicionales útiles

@router.get("/dashboard", response_model=MonitoringResponse)
async def get_monitoring_dashboard():
    """Dashboard completo de monitoreo"""
    try:
        initialize_sample_alerts()
        generate_uptime_records()
        
        # Obtener métricas actuales
        system_metrics = generate_system_metrics()
        app_metrics = generate_application_metrics()
        
        # Alertas activas
        active_alerts = [Alert(**a) for a in monitoring_db["alerts"].values() if a["status"] == "active"]
        
        # Métricas clave
        key_metrics = {
            "cpu_usage": Metric(
                name="cpu_usage_percent",
                type=MetricType.GAUGE,
                value=system_metrics.cpu["usage_percent"],
                unit="percent",
                description="CPU usage",
                timestamp=datetime.now(),
                source="system"
            ),
            "memory_usage": Metric(
                name="memory_usage_percent",
                type=MetricType.GAUGE,
                value=system_metrics.memory["usage_percent"],
                unit="percent",
                description="Memory usage",
                timestamp=datetime.now(),
                source="system"
            ),
            "api_requests": Metric(
                name="api_requests_per_second",
                type=MetricType.GAUGE,
                value=app_metrics.api_requests_per_second,
                unit="req/s",
                description="API requests per second",
                timestamp=datetime.now(),
                source="application"
            )
        }
        
        # Resumen de uptime
        services = ["api", "database", "cache", "auth"]
        uptime_summary = {}
        for svc in services:
            uptime_summary[svc] = UptimeStats(
                service_name=svc,
                current_status=UptimeStatus.UP if random.random() > 0.1 else UptimeStatus.DOWN,
                uptime_percentage=random.uniform(95, 99.9),
                total_checks=random.randint(100, 1000),
                successful_checks=random.randint(95, 999),
                failed_checks=random.randint(1, 50),
                avg_response_time=random.uniform(50, 200),
                last_check=datetime.now() - timedelta(minutes=random.randint(1, 5)),
                last_downtime=datetime.now() - timedelta(hours=random.randint(1, 48)) if random.random() > 0.7 else None,
                incidents_count=random.randint(0, 5),
                mttr=random.uniform(5, 30),
                mtbf=random.uniform(24, 168)
            )
        
        # Estado de salud del sistema
        system_health = {
            "overall_status": "healthy" if len(active_alerts) < 3 else "degraded",
            "cpu_status": "normal" if system_metrics.cpu["usage_percent"] < 80 else "high",
            "memory_status": "normal" if system_metrics.memory["usage_percent"] < 80 else "high",
            "disk_status": "normal" if system_metrics.disk["usage_percent"] < 85 else "high",
            "network_status": "normal",
            "services_status": "operational"
        }
        
        # Resumen de rendimiento
        performance_summary = {
            "avg_response_time": app_metrics.api_response_time_avg,
            "requests_per_second": app_metrics.api_requests_per_second,
            "error_rate": app_metrics.api_error_rate,
            "uptime_percentage": random.uniform(99.5, 99.99)
        }
        
        # Utilización de recursos
        resource_utilization = {
            "cpu": system_metrics.cpu["usage_percent"],
            "memory": system_metrics.memory["usage_percent"],
            "disk": system_metrics.disk["usage_percent"],
            "network": random.uniform(10, 50)
        }
        
        # Incidentes recientes
        recent_incidents = [
            {
                "id": f"inc_{uuid.uuid4().hex[:8]}",
                "title": "API Response Time Spike",
                "severity": "medium",
                "status": "resolved",
                "created_at": datetime.now() - timedelta(hours=2),
                "resolved_at": datetime.now() - timedelta(hours=1)
            },
            {
                "id": f"inc_{uuid.uuid4().hex[:8]}",
                "title": "Database Connection Pool Exhausted",
                "severity": "high",
                "status": "resolved",
                "created_at": datetime.now() - timedelta(hours=6),
                "resolved_at": datetime.now() - timedelta(hours=5)
            }
        ]
        
        # Tendencias (últimas 24 horas)
        trends = {
            "cpu_trend": [random.uniform(20, 80) for _ in range(24)],
            "memory_trend": [random.uniform(30, 70) for _ in range(24)],
            "requests_trend": [random.uniform(50, 200) for _ in range(24)],
            "response_time_trend": [random.uniform(100, 500) for _ in range(24)]
        }
        
        dashboard = MonitoringDashboard(
            system_health=system_health,
            active_alerts=active_alerts[:10],  # Últimas 10 alertas
            key_metrics=key_metrics,
            uptime_summary=uptime_summary,
            performance_summary=performance_summary,
            resource_utilization=resource_utilization,
            recent_incidents=recent_incidents,
            trends=trends
        )
        
        return MonitoringResponse(
            message="Monitoring dashboard retrieved successfully",
            data=dashboard
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving monitoring dashboard: {str(e)}")

@router.put("/alerts/{alert_id}/acknowledge", response_model=MonitoringResponse)
async def acknowledge_alert(alert_id: str = Path(..., description="ID de la alerta")):
    """Reconocer una alerta"""
    try:
        if alert_id not in monitoring_db["alerts"]:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert_data = monitoring_db["alerts"][alert_id]
        alert_data["status"] = AlertStatus.ACKNOWLEDGED
        alert_data["acknowledged_at"] = datetime.now().isoformat()
        alert_data["acknowledged_by"] = "current_user"  # En producción sería el usuario actual
        alert_data["updated_at"] = datetime.now().isoformat()
        
        updated_alert = Alert(**alert_data)
        
        return MonitoringResponse(
            message="Alert acknowledged successfully",
            data={
                "alert": updated_alert,
                "acknowledged_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")

@router.put("/alerts/{alert_id}/resolve", response_model=MonitoringResponse)
async def resolve_alert(alert_id: str = Path(..., description="ID de la alerta")):
    """Resolver una alerta"""
    try:
        if alert_id not in monitoring_db["alerts"]:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert_data = monitoring_db["alerts"][alert_id]
        alert_data["status"] = AlertStatus.RESOLVED
        alert_data["resolved_at"] = datetime.now().isoformat()
        alert_data["resolved_by"] = "current_user"  # En producción sería el usuario actual
        alert_data["updated_at"] = datetime.now().isoformat()
        
        updated_alert = Alert(**alert_data)
        
        return MonitoringResponse(
            message="Alert resolved successfully",
            data={
                "alert": updated_alert,
                "resolved_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving alert: {str(e)}")
