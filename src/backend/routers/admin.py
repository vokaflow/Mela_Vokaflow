from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Dict, Any, Optional
import uuid
import random
from datetime import datetime, timedelta

from ..models.admin_model import (
    AdminDashboard, AdminUser, UserUpdate, GlobalSettings, AdminLog,
    MaintenanceConfig, GlobalStats, SystemAlert, AdminAction, AdminResponse,
    UserManagement, SecurityReport, PerformanceReport, AuditTrail,
    UserRole, UserStatus, MaintenanceMode, LogCategory
)

router = APIRouter(tags=["Admin"])

# Simulación de base de datos en memoria
admin_db = {
    "users": {},
    "settings": {},
    "logs": [],
    "alerts": [],
    "actions": [],
    "maintenance": {},
    "stats": {},
    "audit_trail": []
}

def initialize_admin_data():
    """Inicializar datos de administración"""
    if not admin_db["users"]:
        # Usuarios de ejemplo
        sample_users = []
        for i in range(50):
            user = AdminUser(
                id=f"user_{i+1}",
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                full_name=f"User {i+1}",
                role=random.choice(list(UserRole)),
                status=random.choice(list(UserStatus)),
                created_at=datetime.now() - timedelta(days=random.randint(0, 365)),
                last_login=datetime.now() - timedelta(hours=random.randint(0, 168)) if random.random() > 0.2 else None,
                login_count=random.randint(0, 1000),
                api_calls=random.randint(0, 10000),
                storage_used=random.randint(0, 1024),
                permissions=[f"perm_{j}" for j in range(random.randint(1, 5))]
            )
            admin_db["users"][user.id] = user.dict()
            sample_users.append(user)
    
    # Configuración global por defecto
    if not admin_db["settings"]:
        admin_db["settings"] = GlobalSettings(
            security_features={
                "two_factor_auth": True,
                "password_complexity": True,
                "session_timeout": True,
                "ip_whitelist": False
            },
            api_features={
                "rate_limiting": True,
                "api_versioning": True,
                "request_logging": True,
                "response_caching": True
            },
            notification_settings={
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "admin_alerts": True
            }
        ).dict()

def generate_admin_logs():
    """Generar logs administrativos de ejemplo"""
    if len(admin_db["logs"]) < 100:
        categories = list(LogCategory)
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        actions = ["login", "logout", "create_user", "delete_user", "update_settings", "api_call", "file_upload"]
        
        for i in range(100):
            log = AdminLog(
                id=f"log_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now() - timedelta(hours=random.randint(0, 168)),
                category=random.choice(categories),
                level=random.choice(levels),
                user_id=f"user_{random.randint(1, 50)}" if random.random() > 0.3 else None,
                action=random.choice(actions),
                resource=f"resource_{random.randint(1, 10)}",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (compatible; AdminBot/1.0)",
                details={
                    "request_id": f"req_{uuid.uuid4().hex[:8]}",
                    "duration_ms": random.randint(10, 5000),
                    "status_code": random.choice([200, 201, 400, 401, 403, 404, 500])
                },
                severity=random.choice(["low", "medium", "high", "critical"])
            )
            admin_db["logs"].append(log.dict())

@router.get("/dashboard", response_model=AdminResponse)
async def get_admin_dashboard():
    """
    📊 Dashboard administrativo
    
    Panel principal de administración con:
    - Estado de salud del sistema
    - Estadísticas de usuarios y API
    - Uso de recursos
    - Actividades recientes
    - Alertas del sistema
    """
    try:
        initialize_admin_data()
        
        # Estado de salud del sistema
        system_health = {
            "status": "healthy",
            "uptime": "15d 8h 42m",
            "cpu_usage": random.uniform(10, 80),
            "memory_usage": random.uniform(20, 70),
            "disk_usage": random.uniform(15, 60),
            "network_status": "stable",
            "database_status": "connected",
            "services_running": 12,
            "services_total": 15
        }
        
        # Estadísticas de usuarios
        total_users = len(admin_db["users"])
        active_users = len([u for u in admin_db["users"].values() if u["status"] == "active"])
        
        user_stats = {
            "total_users": total_users,
            "active_users": active_users,
            "new_today": random.randint(5, 25),
            "online_now": random.randint(50, 200),
            "banned_users": len([u for u in admin_db["users"].values() if u["status"] == "banned"])
        }
        
        # Estadísticas de API
        api_stats = {
            "total_requests_today": random.randint(10000, 50000),
            "successful_requests": random.randint(9000, 48000),
            "failed_requests": random.randint(100, 2000),
            "avg_response_time": random.uniform(150, 800),
            "rate_limited_requests": random.randint(10, 100),
            "top_endpoints": [
                {"endpoint": "/api/vicky/process", "calls": random.randint(1000, 5000)},
                {"endpoint": "/api/translate", "calls": random.randint(800, 4000)},
                {"endpoint": "/api/tts/synthesize", "calls": random.randint(600, 3000)}
            ]
        }
        
        # Uso de recursos
        resource_usage = {
            "cpu_cores": 8,
            "cpu_usage_percent": random.uniform(15, 75),
            "memory_total_gb": 32,
            "memory_used_gb": random.uniform(8, 24),
            "disk_total_gb": 1000,
            "disk_used_gb": random.uniform(200, 600),
            "network_in_mbps": random.uniform(10, 100),
            "network_out_mbps": random.uniform(5, 80)
        }
        
        # Actividades recientes
        recent_activities = [
            {
                "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 60)),
                "type": "user_registration",
                "description": f"New user registered: user{random.randint(1, 1000)}",
                "severity": "info"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 120)),
                "type": "system_update",
                "description": "System configuration updated",
                "severity": "info"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 180)),
                "type": "security_alert",
                "description": "Multiple failed login attempts detected",
                "severity": "warning"
            }
        ]
        
        # Alertas del sistema
        alerts = [
            {
                "id": f"alert_{uuid.uuid4().hex[:8]}",
                "type": "performance",
                "severity": "warning",
                "message": "High CPU usage detected",
                "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 60))
            },
            {
                "id": f"alert_{uuid.uuid4().hex[:8]}",
                "type": "security",
                "severity": "medium",
                "message": "Unusual login pattern detected",
                "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 120))
            }
        ]
        
        # Métricas de rendimiento
        performance_metrics = {
            "requests_per_second": random.uniform(50, 200),
            "avg_response_time_ms": random.uniform(100, 500),
            "error_rate_percent": random.uniform(0.1, 2.0),
            "cache_hit_rate_percent": random.uniform(80, 95),
            "database_query_time_ms": random.uniform(10, 100)
        }
        
        # Estado de seguridad
        security_status = {
            "threat_level": "low",
            "failed_logins_24h": random.randint(10, 100),
            "blocked_ips": random.randint(5, 50),
            "security_events": random.randint(0, 10),
            "ssl_certificate_expires": "45 days",
            "last_security_scan": datetime.now() - timedelta(days=1)
        }
        
        dashboard = AdminDashboard(
            system_health=system_health,
            user_stats=user_stats,
            api_stats=api_stats,
            resource_usage=resource_usage,
            recent_activities=recent_activities,
            alerts=alerts,
            performance_metrics=performance_metrics,
            security_status=security_status
        )
        
        return AdminResponse(
            message="Admin dashboard data retrieved successfully",
            data=dashboard
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving admin dashboard: {str(e)}")

@router.get("/users", response_model=AdminResponse)
async def get_users_management(
    role: Optional[UserRole] = Query(None, description="Filtrar por rol"),
    status: Optional[UserStatus] = Query(None, description="Filtrar por estado"),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    sort_by: str = Query("created_at", description="Campo para ordenar"),
    sort_order: str = Query("desc", description="Orden: asc o desc")
):
    """
    👥 Gestión de usuarios
    
    Panel de gestión de usuarios con:
    - Lista filtrable de usuarios
    - Estadísticas de usuarios
    - Acciones administrativas
    - Búsqueda y paginación
    """
    try:
        initialize_admin_data()
        
        # Filtrar usuarios
        filtered_users = []
        for user_data in admin_db["users"].values():
            user = AdminUser(**user_data)
            
            # Aplicar filtros
            if role and user.role != role:
                continue
            if status and user.status != status:
                continue
            if search and search.lower() not in user.username.lower() and search.lower() not in user.email.lower():
                continue
            
            filtered_users.append(user)
        
        # Ordenar usuarios
        reverse_order = sort_order.lower() == "desc"
        if sort_by == "created_at":
            filtered_users.sort(key=lambda x: x.created_at, reverse=reverse_order)
        elif sort_by == "last_login":
            filtered_users.sort(key=lambda x: x.last_login or datetime.min, reverse=reverse_order)
        elif sort_by == "username":
            filtered_users.sort(key=lambda x: x.username.lower(), reverse=reverse_order)
        elif sort_by == "api_calls":
            filtered_users.sort(key=lambda x: x.api_calls, reverse=reverse_order)
        
        # Aplicar paginación
        total_filtered = len(filtered_users)
        paginated_users = filtered_users[offset:offset + limit]
        
        # Estadísticas de gestión de usuarios
        total_users = len(admin_db["users"])
        users_by_role = {}
        users_by_status = {}
        
        for user_data in admin_db["users"].values():
            user = AdminUser(**user_data)
            users_by_role[user.role.value] = users_by_role.get(user.role.value, 0) + 1
            users_by_status[user.status.value] = users_by_status.get(user.status.value, 0) + 1
        
        # Usuarios más activos
        all_users = [AdminUser(**u) for u in admin_db["users"].values()]
        top_users = sorted(all_users, key=lambda x: x.api_calls, reverse=True)[:5]
        
        # Registros recientes
        recent_users = sorted(all_users, key=lambda x: x.created_at, reverse=True)[:5]
        
        user_management = UserManagement(
            total_users=total_users,
            active_users=users_by_status.get("active", 0),
            new_users_today=random.randint(5, 25),
            users_by_role=users_by_role,
            users_by_status=users_by_status,
            recent_registrations=recent_users,
            top_users_by_activity=top_users
        )
        
        return AdminResponse(
            message=f"Retrieved {len(paginated_users)} users",
            data={
                "users": paginated_users,
                "total_filtered": total_filtered,
                "total_users": total_users,
                "management_stats": user_management,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_filtered
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users management: {str(e)}")

@router.put("/settings", response_model=AdminResponse)
async def update_global_settings(settings: GlobalSettings):
    """
    ⚙️ Configuración global del sistema
    
    Actualiza configuración global:
    - Configuraciones del sitio
    - Límites y restricciones
    - Características de seguridad
    - Configuración de API
    - Notificaciones
    """
    try:
        # Validar configuración
        if settings.max_users < 1:
            raise HTTPException(status_code=400, detail="max_users must be at least 1")
        
        if settings.max_api_calls_per_day < 100:
            raise HTTPException(status_code=400, detail="max_api_calls_per_day must be at least 100")
        
        if settings.max_storage_per_user < 10:
            raise HTTPException(status_code=400, detail="max_storage_per_user must be at least 10 MB")
        
        # Guardar configuración anterior para auditoría
        old_settings = admin_db.get("settings", {})
        
        # Actualizar configuración
        settings_dict = settings.dict()
        settings_dict["updated_at"] = datetime.now().isoformat()
        settings_dict["updated_by"] = "admin_user"  # En producción sería el usuario actual
        
        admin_db["settings"] = settings_dict
        
        # Registrar cambios en auditoría
        changes = []
        for key, new_value in settings_dict.items():
            if key in ["updated_at", "updated_by"]:
                continue
            old_value = old_settings.get(key)
            if old_value != new_value:
                changes.append({
                    "field": key,
                    "old_value": old_value,
                    "new_value": new_value
                })
        
        # Crear entrada de auditoría
        audit_entry = AuditTrail(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id="admin_user",
            action="update_global_settings",
            resource="global_settings",
            old_value=old_settings,
            new_value=settings_dict,
            ip_address="127.0.0.1",
            success=True,
            details={"changes": changes}
        )
        
        admin_db["audit_trail"].append(audit_entry.dict())
        
        # Determinar si se requiere reinicio
        restart_required_fields = ["logging_level", "rate_limiting_enabled", "backup_enabled"]
        restart_required = any(change["field"] in restart_required_fields for change in changes)
        
        return AdminResponse(
            message="Global settings updated successfully",
            data={
                "settings": settings,
                "changes_applied": len(changes),
                "restart_required": restart_required,
                "changes_summary": changes,
                "updated_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating global settings: {str(e)}")

@router.get("/logs", response_model=AdminResponse)
async def get_admin_logs(
    category: Optional[LogCategory] = Query(None, description="Filtrar por categoría"),
    level: Optional[str] = Query(None, description="Filtrar por nivel"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    start_time: Optional[datetime] = Query(None, description="Tiempo de inicio"),
    end_time: Optional[datetime] = Query(None, description="Tiempo de fin"),
    search: Optional[str] = Query(None, description="Buscar en acción o detalles"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    📋 Logs administrativos
    
    Acceso a logs del sistema con:
    - Filtros avanzados
    - Búsqueda en contenido
    - Categorización por tipo
    - Análisis de patrones
    """
    try:
        generate_admin_logs()
        
        # Filtrar logs
        filtered_logs = []
        for log_data in admin_db["logs"]:
            log = AdminLog(**log_data)
            
            # Aplicar filtros
            if category and log.category != category:
                continue
            if level and log.level != level:
                continue
            if user_id and log.user_id != user_id:
                continue
            if start_time and log.timestamp < start_time:
                continue
            if end_time and log.timestamp > end_time:
                continue
            if search and search.lower() not in log.action.lower() and search.lower() not in str(log.details).lower():
                continue
            
            filtered_logs.append(log)
        
        # Ordenar por timestamp (más recientes primero)
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Aplicar paginación
        total_filtered = len(filtered_logs)
        paginated_logs = filtered_logs[offset:offset + limit]
        
        # Estadísticas de logs
        log_stats = {
            "total_logs": len(admin_db["logs"]),
            "logs_by_category": {},
            "logs_by_level": {},
            "logs_by_severity": {},
            "recent_errors": 0
        }
        
        for log_data in admin_db["logs"]:
            log = AdminLog(**log_data)
            
            # Contar por categoría
            cat = log.category.value
            log_stats["logs_by_category"][cat] = log_stats["logs_by_category"].get(cat, 0) + 1
            
            # Contar por nivel
            log_stats["logs_by_level"][log.level] = log_stats["logs_by_level"].get(log.level, 0) + 1
            
            # Contar por severidad
            log_stats["logs_by_severity"][log.severity] = log_stats["logs_by_severity"].get(log.severity, 0) + 1
            
            # Errores recientes (últimas 24 horas)
            if log.level in ["ERROR", "CRITICAL"] and log.timestamp > datetime.now() - timedelta(days=1):
                log_stats["recent_errors"] += 1
        
        return AdminResponse(
            message=f"Retrieved {len(paginated_logs)} log entries",
            data={
                "logs": paginated_logs,
                "total_filtered": total_filtered,
                "log_statistics": log_stats,
                "filters_applied": {
                    "category": category,
                    "level": level,
                    "user_id": user_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "search": search
                },
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_filtered
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving admin logs: {str(e)}")

@router.post("/maintenance", response_model=AdminResponse)
async def set_maintenance_mode(maintenance_config: MaintenanceConfig):
    """
    🔧 Configurar modo mantenimiento
    
    Gestiona el modo mantenimiento:
    - Activación/desactivación
    - Programación de mantenimiento
    - Configuración de accesos
    - Mensajes personalizados
    """
    try:
        # Validar configuración
        if maintenance_config.mode == MaintenanceMode.SCHEDULED:
            if not maintenance_config.start_time or not maintenance_config.end_time:
                raise HTTPException(
                    status_code=400, 
                    detail="start_time and end_time are required for scheduled maintenance"
                )
            
            if maintenance_config.start_time >= maintenance_config.end_time:
                raise HTTPException(
                    status_code=400, 
                    detail="start_time must be before end_time"
                )
        
        # Guardar configuración de mantenimiento
        maintenance_dict = maintenance_config.dict()
        maintenance_dict["configured_at"] = datetime.now().isoformat()
        maintenance_dict["configured_by"] = "admin_user"
        
        admin_db["maintenance"] = maintenance_dict
        
        # Crear acción administrativa
        admin_action = AdminAction(
            action_id=str(uuid.uuid4()),
            admin_user_id="admin_user",
            action_type="maintenance_config",
            target_type="system",
            target_id="global",
            description=f"Maintenance mode set to {maintenance_config.mode.value}",
            success=True
        )
        
        admin_db["actions"].append(admin_action.dict())
        
        # Determinar estado actual
        current_time = datetime.now()
        if maintenance_config.mode == MaintenanceMode.ACTIVE:
            status = "Maintenance mode is now ACTIVE"
        elif maintenance_config.mode == MaintenanceMode.SCHEDULED:
            if current_time < maintenance_config.start_time:
                status = f"Maintenance scheduled for {maintenance_config.start_time}"
            elif current_time <= maintenance_config.end_time:
                status = "Scheduled maintenance is now ACTIVE"
            else:
                status = "Scheduled maintenance has ended"
        elif maintenance_config.mode == MaintenanceMode.EMERGENCY:
            status = "EMERGENCY maintenance mode activated"
        else:
            status = "Maintenance mode is OFF"
        
        # Calcular usuarios afectados
        affected_users = 0
        if maintenance_config.mode in [MaintenanceMode.ACTIVE, MaintenanceMode.EMERGENCY]:
            total_users = len([u for u in admin_db["users"].values() if u["status"] == "active"])
            allowed_users_count = len(maintenance_config.allowed_users)
            affected_users = max(0, total_users - allowed_users_count)
        
        return AdminResponse(
            message="Maintenance mode configuration updated",
            data={
                "maintenance_config": maintenance_config,
                "current_status": status,
                "affected_users": affected_users,
                "allowed_ips_count": len(maintenance_config.allowed_ips),
                "allowed_users_count": len(maintenance_config.allowed_users),
                "configured_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring maintenance mode: {str(e)}")

@router.get("/stats", response_model=AdminResponse)
async def get_global_statistics(
    period: str = Query("24h", description="Período: 1h, 24h, 7d, 30d"),
    include_details: bool = Query(False, description="Incluir detalles adicionales")
):
    """
    📈 Estadísticas globales del sistema
    
    Estadísticas completas del sistema:
    - Métricas de usuarios y actividad
    - Rendimiento de API
    - Uso de recursos
    - Distribución geográfica
    - Tendencias temporales
    """
    try:
        initialize_admin_data()
        
        # Estadísticas de usuarios
        total_users = len(admin_db["users"])
        active_users = len([u for u in admin_db["users"].values() if u["status"] == "active"])
        
        users_stats = {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_period": random.randint(10, 100),
            "user_retention_rate": random.uniform(70, 90),
            "avg_session_duration": random.uniform(15, 60),
            "users_by_role": {},
            "users_by_status": {}
        }
        
        # Contar usuarios por rol y estado
        for user_data in admin_db["users"].values():
            user = AdminUser(**user_data)
            users_stats["users_by_role"][user.role.value] = users_stats["users_by_role"].get(user.role.value, 0) + 1
            users_stats["users_by_status"][user.status.value] = users_stats["users_by_status"].get(user.status.value, 0) + 1
        
        # Estadísticas de API
        api_stats = {
            "total_requests": random.randint(50000, 200000),
            "successful_requests": random.randint(45000, 190000),
            "failed_requests": random.randint(1000, 10000),
            "avg_response_time": random.uniform(150, 500),
            "requests_per_second": random.uniform(50, 200),
            "top_endpoints": [
                {"endpoint": "/api/vicky/process", "requests": random.randint(10000, 50000), "avg_time": random.uniform(200, 800)},
                {"endpoint": "/api/translate", "requests": random.randint(8000, 40000), "avg_time": random.uniform(100, 400)},
                {"endpoint": "/api/tts/synthesize", "requests": random.randint(6000, 30000), "avg_time": random.uniform(500, 2000)},
                {"endpoint": "/api/stt/transcribe", "requests": random.randint(4000, 20000), "avg_time": random.uniform(800, 3000)}
            ],
            "error_breakdown": {
                "4xx_errors": random.randint(500, 5000),
                "5xx_errors": random.randint(100, 1000),
                "timeout_errors": random.randint(50, 500)
            }
        }
        
        # Estadísticas del sistema
        system_stats = {
            "uptime_hours": random.randint(100, 8760),
            "cpu_avg_usage": random.uniform(20, 60),
            "memory_avg_usage": random.uniform(30, 70),
            "disk_usage": random.uniform(40, 80),
            "network_throughput_mbps": random.uniform(50, 500),
            "active_connections": random.randint(100, 1000),
            "database_connections": random.randint(10, 100),
            "cache_hit_rate": random.uniform(80, 95)
        }
        
        # Estadísticas de contenido
        content_stats = {
            "total_conversations": random.randint(1000, 10000),
            "total_messages": random.randint(50000, 500000),
            "total_translations": random.randint(10000, 100000),
            "total_voice_samples": random.randint(500, 5000),
            "total_files_uploaded": random.randint(2000, 20000),
            "storage_used_gb": random.randint(100, 1000)
        }
        
        # Métricas de rendimiento
        performance_stats = {
            "avg_response_time_ms": random.uniform(150, 500),
            "p95_response_time_ms": random.uniform(500, 2000),
            "p99_response_time_ms": random.uniform(1000, 5000),
            "throughput_rps": random.uniform(50, 200),
            "error_rate_percent": random.uniform(0.1, 2.0),
            "availability_percent": random.uniform(99.5, 99.99)
        }
        
        # Estadísticas de seguridad
        security_stats = {
            "failed_login_attempts": random.randint(100, 1000),
            "blocked_ips": random.randint(10, 100),
            "security_events": random.randint(5, 50),
            "suspicious_activities": random.randint(2, 20),
            "malware_detections": random.randint(0, 5),
            "ddos_attempts": random.randint(0, 10)
        }
        
        # Estadísticas de almacenamiento
        storage_stats = {
            "total_storage_gb": 1000,
            "used_storage_gb": random.randint(200, 800),
            "user_files_gb": random.randint(100, 400),
            "system_files_gb": random.randint(50, 200),
            "backups_gb": random.randint(50, 200),
            "avg_file_size_mb": random.uniform(1, 50)
        }
        
        # Distribución geográfica
        geographic_stats = {
            "United States": random.randint(1000, 5000),
            "Spain": random.randint(500, 2000),
            "Mexico": random.randint(300, 1500),
            "Argentina": random.randint(200, 1000),
            "Colombia": random.randint(150, 800),
            "France": random.randint(100, 600),
            "Germany": random.randint(100, 600),
            "Brazil": random.randint(200, 1000),
            "Other": random.randint(500, 2000)
        }
        
        global_stats = GlobalStats(
            users=users_stats,
            api=api_stats,
            system=system_stats,
            content=content_stats,
            performance=performance_stats,
            security=security_stats,
            storage=storage_stats,
            geographic=geographic_stats
        )
        
        response_data = {"statistics": global_stats, "period": period, "generated_at": datetime.now()}
        
        # Incluir detalles adicionales si se solicita
        if include_details:
            response_data["additional_details"] = {
                "trending_features": ["voice_cloning", "real_time_translation", "ai_chat"],
                "peak_usage_hours": [9, 10, 11, 14, 15, 16, 20, 21],
                "growth_metrics": {
                    "user_growth_rate": random.uniform(5, 15),
                    "api_usage_growth": random.uniform(10, 25),
                    "storage_growth_rate": random.uniform(8, 20)
                },
                "recommendations": [
                    "Consider scaling API infrastructure during peak hours",
                    "Monitor storage growth and plan capacity expansion",
                    "Implement additional security measures for high-risk regions"
                ]
            }
        
        return AdminResponse(
            message="Global statistics retrieved successfully",
            data=response_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving global statistics: {str(e)}")

# Endpoints adicionales útiles

@router.put("/users/{user_id}", response_model=AdminResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """Actualizar usuario específico"""
    try:
        if user_id not in admin_db["users"]:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = admin_db["users"][user_id]
        old_user = AdminUser(**user_data)
        
        # Aplicar actualizaciones
        update_dict = user_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field != "reason" and value is not None:
                user_data[field] = value
        
        user_data["updated_at"] = datetime.now().isoformat()
        
        # Crear acción administrativa
        admin_action = AdminAction(
            action_id=str(uuid.uuid4()),
            admin_user_id="admin_user",
            action_type="update_user",
            target_type="user",
            target_id=user_id,
            description=f"User updated: {user_update.reason or 'No reason provided'}",
            success=True
        )
        
        admin_db["actions"].append(admin_action.dict())
        
        updated_user = AdminUser(**user_data)
        
        return AdminResponse(
            message="User updated successfully",
            data={
                "user": updated_user,
                "changes": update_dict,
                "reason": user_update.reason
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.get("/security-report", response_model=AdminResponse)
async def get_security_report():
    """Obtener reporte de seguridad"""
    try:
        security_report = SecurityReport(
            failed_logins=random.randint(50, 500),
            suspicious_activities=random.randint(5, 50),
            blocked_ips=[f"192.168.1.{i}" for i in range(1, random.randint(5, 20))],
            security_events=[
                {
                    "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24)),
                    "type": "brute_force_attempt",
                    "severity": "high",
                    "source_ip": f"192.168.1.{random.randint(1, 255)}",
                    "details": "Multiple failed login attempts"
                }
                for _ in range(random.randint(3, 10))
            ],
            vulnerability_scan={
                "last_scan": datetime.now() - timedelta(days=1),
                "vulnerabilities_found": random.randint(0, 5),
                "critical_issues": random.randint(0, 2),
                "status": "clean" if random.random() > 0.3 else "issues_found"
            },
            compliance_status={
                "gdpr_compliant": True,
                "ccpa_compliant": True,
                "iso27001_compliant": random.random() > 0.2,
                "soc2_compliant": random.random() > 0.3
            }
        )
        
        return AdminResponse(
            message="Security report generated successfully",
            data=security_report
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating security report: {str(e)}")
