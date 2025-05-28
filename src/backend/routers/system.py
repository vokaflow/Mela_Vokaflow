from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
import psutil
import platform
import sys
import os
import uuid
import hashlib
import subprocess
import signal
from datetime import datetime, timedelta
import random
import json

from ..models.system_model import (
    SystemInfo, SystemMetrics, SystemProcess, SystemLog, BackupInfo,
    SystemConfig, SystemOperation, SystemHealth, SystemResponse,
    RestartRequest, ShutdownRequest, BackupRequest, LogQuery,
    SystemStatus, LogLevel, ProcessStatus, BackupType
)

router = APIRouter(tags=["System"])

# Simulación de base de datos en memoria
system_db = {
    "config": {},
    "operations": {},
    "backups": {},
    "logs": [],
    "health_checks": []
}

def get_system_uptime():
    """Obtener tiempo de actividad del sistema"""
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = psutil.time.time() - boot_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m"
    except:
        return "Unknown"

def get_network_interfaces():
    """Obtener interfaces de red"""
    try:
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = {"name": interface, "addresses": []}
            for addr in addrs:
                interface_info["addresses"].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            interfaces.append(interface_info)
        return interfaces
    except:
        return []

@router.get("/info", response_model=SystemResponse)
async def get_system_info():
    """
    ℹ️ Obtener información del sistema
    
    Retorna información detallada del sistema:
    - Información del host y plataforma
    - Versiones de software
    - Recursos de hardware
    - Configuración de red
    """
    try:
        # Obtener información del sistema
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = SystemInfo(
            hostname=platform.node(),
            platform=f"{platform.system()} {platform.release()}",
            architecture=platform.machine(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            app_version="1.0.0",
            uptime=get_system_uptime(),
            boot_time=datetime.fromtimestamp(psutil.boot_time()),
            timezone=str(datetime.now().astimezone().tzinfo),
            cpu_count=psutil.cpu_count(),
            memory_total=memory.total,
            disk_total=disk.total,
            network_interfaces=get_network_interfaces()
        )
        
        return SystemResponse(
            message="System information retrieved successfully",
            data=system_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system info: {str(e)}")

@router.get("/metrics", response_model=SystemResponse)
async def get_system_metrics():
    """
    📊 Obtener métricas del sistema
    
    Retorna métricas en tiempo real:
    - Uso de CPU, memoria y disco
    - I/O de red y disco
    - Carga del sistema
    - Procesos y conexiones activas
    """
    try:
        # Obtener métricas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # I/O de red
        try:
            net_io = psutil.net_io_counters()
            network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            network_io = {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
        
        # I/O de disco
        try:
            disk_io = psutil.disk_io_counters()
            disk_io_data = {
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count
            }
        except:
            disk_io_data = {"read_bytes": 0, "write_bytes": 0, "read_count": 0, "write_count": 0}
        
        # Promedio de carga
        try:
            load_avg = os.getloadavg()
        except:
            load_avg = [0.0, 0.0, 0.0]
        
        metrics = SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=(disk.used / disk.total) * 100,
            network_io=network_io,
            disk_io=disk_io_data,
            load_average=list(load_avg),
            active_connections=random.randint(10, 100),  # Simulado
            processes_count=len(psutil.pids()),
            threads_count=sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads']),
            file_descriptors=random.randint(100, 1000)  # Simulado
        )
        
        return SystemResponse(
            message="System metrics retrieved successfully",
            data=metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system metrics: {str(e)}")

@router.post("/restart", response_model=SystemResponse)
async def restart_system(
    restart_request: RestartRequest,
    background_tasks: BackgroundTasks
):
    """
    🔄 Reiniciar el sistema
    
    Reinicia el sistema de forma controlada:
    - Opción de forzar reinicio
    - Retraso configurable
    - Registro de la operación
    - Notificación a usuarios activos
    """
    try:
        operation_id = str(uuid.uuid4())
        
        # Crear operación
        operation = SystemOperation(
            operation="restart",
            status="initiated",
            started_at=datetime.now(),
            message=f"System restart initiated with {restart_request.delay_seconds}s delay"
        )
        
        system_db["operations"][operation_id] = operation.dict()
        
        # Función para ejecutar el reinicio
        async def execute_restart():
            try:
                # Actualizar progreso
                operation["status"] = "preparing"
                operation["progress"] = 25
                operation["message"] = "Preparing for restart..."
                system_db["operations"][operation_id] = operation.dict()
                
                await asyncio.sleep(restart_request.delay_seconds / 2)
                
                # Guardar estado
                operation["progress"] = 50
                operation["message"] = "Saving system state..."
                system_db["operations"][operation_id] = operation.dict()
                
                await asyncio.sleep(restart_request.delay_seconds / 2)
                
                # Simular reinicio (en producción sería un reinicio real)
                operation["status"] = "restarting"
                operation["progress"] = 100
                operation["message"] = "Restarting system..."
                operation["completed_at"] = datetime.now()
                system_db["operations"][operation_id] = operation.dict()
                
                # En un sistema real, aquí se ejecutaría el reinicio
                if restart_request.force:
                    # Reinicio forzado
                    os.system("sudo reboot")
                else:
                    # Reinicio graceful
                    os.system("sudo shutdown -r now")
                
            except Exception as e:
                operation["status"] = "failed"
                operation["message"] = f"Restart failed: {str(e)}"
                operation["completed_at"] = datetime.now()
                system_db["operations"][operation_id] = operation.dict()
        
        # Ejecutar en background
        background_tasks.add_task(execute_restart)
        
        return SystemResponse(
            message="System restart initiated",
            data={
                "operation_id": operation_id,
                "delay_seconds": restart_request.delay_seconds,
                "force": restart_request.force,
                "reason": restart_request.reason
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating system restart: {str(e)}")

@router.post("/shutdown", response_model=SystemResponse)
async def shutdown_system(
    shutdown_request: ShutdownRequest,
    background_tasks: BackgroundTasks
):
    """
    🔌 Apagar el sistema
    
    Apaga el sistema de forma controlada:
    - Cierre graceful de servicios
    - Guardado de estado
    - Notificación a usuarios
    - Registro de la operación
    """
    try:
        operation_id = str(uuid.uuid4())
        
        # Crear operación
        operation = SystemOperation(
            operation="shutdown",
            status="initiated",
            started_at=datetime.now(),
            message=f"System shutdown initiated with {shutdown_request.delay_seconds}s delay"
        )
        
        system_db["operations"][operation_id] = operation.dict()
        
        # Función para ejecutar el apagado
        async def execute_shutdown():
            try:
                # Actualizar progreso
                operation["status"] = "preparing"
                operation["progress"] = 20
                operation["message"] = "Preparing for shutdown..."
                system_db["operations"][operation_id] = operation.dict()
                
                await asyncio.sleep(shutdown_request.delay_seconds / 3)
                
                # Cerrar servicios
                operation["progress"] = 50
                operation["message"] = "Stopping services..."
                system_db["operations"][operation_id] = operation.dict()
                
                await asyncio.sleep(shutdown_request.delay_seconds / 3)
                
                # Guardar estado
                operation["progress"] = 80
                operation["message"] = "Saving system state..."
                system_db["operations"][operation_id] = operation.dict()
                
                await asyncio.sleep(shutdown_request.delay_seconds / 3)
                
                # Apagar sistema
                operation["status"] = "shutting_down"
                operation["progress"] = 100
                operation["message"] = "Shutting down system..."
                operation["completed_at"] = datetime.now()
                system_db["operations"][operation_id] = operation.dict()
                
                # En un sistema real, aquí se ejecutaría el apagado
                if shutdown_request.force:
                    os.system("sudo poweroff")
                else:
                    os.system("sudo shutdown -h now")
                
            except Exception as e:
                operation["status"] = "failed"
                operation["message"] = f"Shutdown failed: {str(e)}"
                operation["completed_at"] = datetime.now()
                system_db["operations"][operation_id] = operation.dict()
        
        # Ejecutar en background
        background_tasks.add_task(execute_shutdown)
        
        return SystemResponse(
            message="System shutdown initiated",
            data={
                "operation_id": operation_id,
                "delay_seconds": shutdown_request.delay_seconds,
                "force": shutdown_request.force,
                "reason": shutdown_request.reason
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating system shutdown: {str(e)}")

@router.get("/logs", response_model=SystemResponse)
async def get_system_logs(
    level: Optional[LogLevel] = Query(None, description="Filtrar por nivel"),
    component: Optional[str] = Query(None, description="Filtrar por componente"),
    start_time: Optional[datetime] = Query(None, description="Tiempo de inicio"),
    end_time: Optional[datetime] = Query(None, description="Tiempo de fin"),
    search: Optional[str] = Query(None, description="Buscar en mensaje"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados")
):
    """
    📋 Obtener logs del sistema
    
    Retorna logs del sistema con filtros:
    - Filtro por nivel de log
    - Filtro por componente
    - Rango de fechas
    - Búsqueda en contenido
    - Paginación
    """
    try:
        # Generar logs de ejemplo si no existen
        if not system_db["logs"]:
            components = ["system", "api", "database", "auth", "vicky", "translator"]
            levels = list(LogLevel)
            
            for i in range(500):
                log = SystemLog(
                    timestamp=datetime.now() - timedelta(hours=random.randint(0, 168)),
                    level=random.choice(levels),
                    component=random.choice(components),
                    message=f"Log message {i+1} from {random.choice(components)}",
                    details={"request_id": f"req_{uuid.uuid4().hex[:8]}", "user_id": f"user_{random.randint(1,100)}"},
                    source_file=f"{random.choice(components)}.py",
                    line_number=random.randint(1, 500)
                )
                system_db["logs"].append(log.dict())
        
        # Filtrar logs
        filtered_logs = []
        for log_data in system_db["logs"]:
            log = SystemLog(**log_data)
            
            # Aplicar filtros
            if level and log.level != level:
                continue
            if component and log.component != component:
                continue
            if start_time and log.timestamp < start_time:
                continue
            if end_time and log.timestamp > end_time:
                continue
            if search and search.lower() not in log.message.lower():
                continue
            
            filtered_logs.append(log)
        
        # Ordenar por timestamp (más recientes primero)
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Aplicar límite
        limited_logs = filtered_logs[:limit]
        
        return SystemResponse(
            message=f"Retrieved {len(limited_logs)} log entries",
            data={
                "logs": limited_logs,
                "total_found": len(filtered_logs),
                "total_available": len(system_db["logs"]),
                "filters_applied": {
                    "level": level,
                    "component": component,
                    "start_time": start_time,
                    "end_time": end_time,
                    "search": search
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system logs: {str(e)}")

@router.post("/backup", response_model=SystemResponse)
async def create_backup(
    backup_request: BackupRequest,
    background_tasks: BackgroundTasks
):
    """
    💾 Crear backup del sistema
    
    Crea backup del sistema:
    - Diferentes tipos de backup
    - Compresión y encriptación
    - Verificación de integridad
    - Almacenamiento seguro
    """
    try:
        backup_id = str(uuid.uuid4())
        
        # Crear información del backup
        backup_info = BackupInfo(
            id=backup_id,
            type=backup_request.type,
            status="initiated",
            created_at=datetime.now(),
            size=0,
            file_path=f"/backups/backup_{backup_id}.tar.gz",
            checksum="",
            metadata={
                "include_data": backup_request.include_data,
                "include_config": backup_request.include_config,
                "include_logs": backup_request.include_logs,
                "compression": backup_request.compression,
                "encryption": backup_request.encryption
            }
        )
        
        system_db["backups"][backup_id] = backup_info.dict()
        
        # Función para crear el backup
        async def create_backup_task():
            try:
                # Simular creación del backup
                backup_data = system_db["backups"][backup_id]
                
                # Fase 1: Preparación
                backup_data["status"] = "preparing"
                await asyncio.sleep(1)
                
                # Fase 2: Recopilación de datos
                backup_data["status"] = "collecting"
                estimated_size = 0
                
                if backup_request.include_data:
                    estimated_size += random.randint(100000000, 500000000)  # 100-500MB
                if backup_request.include_config:
                    estimated_size += random.randint(1000000, 10000000)     # 1-10MB
                if backup_request.include_logs:
                    estimated_size += random.randint(50000000, 200000000)   # 50-200MB
                
                backup_data["size"] = estimated_size
                await asyncio.sleep(2)
                
                # Fase 3: Compresión
                if backup_request.compression:
                    backup_data["status"] = "compressing"
                    backup_data["size"] = int(estimated_size * 0.3)  # 30% del tamaño original
                    await asyncio.sleep(1)
                
                # Fase 4: Encriptación
                if backup_request.encryption:
                    backup_data["status"] = "encrypting"
                    await asyncio.sleep(1)
                
                # Fase 5: Verificación
                backup_data["status"] = "verifying"
                backup_data["checksum"] = hashlib.md5(f"backup_{backup_id}".encode()).hexdigest()
                await asyncio.sleep(1)
                
                # Completado
                backup_data["status"] = "completed"
                system_db["backups"][backup_id] = backup_data
                
            except Exception as e:
                backup_data["status"] = "failed"
                backup_data["metadata"]["error"] = str(e)
                system_db["backups"][backup_id] = backup_data
        
        # Ejecutar en background
        background_tasks.add_task(create_backup_task)
        
        return SystemResponse(
            message="Backup creation initiated",
            data=backup_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")

@router.get("/processes", response_model=SystemResponse)
async def get_active_processes(
    limit: int = Query(50, ge=1, le=200, description="Número máximo de procesos"),
    sort_by: str = Query("cpu", description="Ordenar por: cpu, memory, pid, name"),
    filter_name: Optional[str] = Query(None, description="Filtrar por nombre")
):
    """
    🔄 Obtener procesos activos
    
    Lista procesos del sistema:
    - Información detallada de cada proceso
    - Uso de CPU y memoria
    - Filtros y ordenamiento
    - Estado de los procesos
    """
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 
                                       'memory_info', 'create_time', 'cmdline', 'username', 'num_threads']):
            try:
                pinfo = proc.info
                
                # Filtrar por nombre si se especifica
                if filter_name and filter_name.lower() not in pinfo['name'].lower():
                    continue
                
                # Mapear estado
                status_map = {
                    'running': ProcessStatus.RUNNING,
                    'sleeping': ProcessStatus.SLEEPING,
                    'disk-sleep': ProcessStatus.DISK_SLEEP,
                    'stopped': ProcessStatus.STOPPED,
                    'zombie': ProcessStatus.ZOMBIE
                }
                
                process = SystemProcess(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    status=status_map.get(pinfo['status'], ProcessStatus.RUNNING),
                    cpu_percent=pinfo['cpu_percent'] or 0.0,
                    memory_percent=pinfo['memory_percent'] or 0.0,
                    memory_rss=pinfo['memory_info'].rss if pinfo['memory_info'] else 0,
                    create_time=datetime.fromtimestamp(pinfo['create_time']),
                    cmdline=pinfo['cmdline'] or [],
                    username=pinfo['username'] or 'unknown',
                    num_threads=pinfo['num_threads'] or 1
                )
                
                processes.append(process)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Ordenar procesos
        if sort_by == "cpu":
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x.memory_percent, reverse=True)
        elif sort_by == "pid":
            processes.sort(key=lambda x: x.pid)
        elif sort_by == "name":
            processes.sort(key=lambda x: x.name.lower())
        
        # Aplicar límite
        limited_processes = processes[:limit]
        
        return SystemResponse(
            message=f"Retrieved {len(limited_processes)} processes",
            data={
                "processes": limited_processes,
                "total_processes": len(processes),
                "system_summary": {
                    "total_cpu": sum(p.cpu_percent for p in processes),
                    "total_memory": sum(p.memory_percent for p in processes),
                    "running_processes": len([p for p in processes if p.status == ProcessStatus.RUNNING])
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving processes: {str(e)}")

@router.put("/config", response_model=SystemResponse)
async def update_system_config(config: SystemConfig):
    """
    ⚙️ Configurar sistema
    
    Actualiza configuración del sistema:
    - Parámetros de rendimiento
    - Configuración de logging
    - Opciones de backup
    - Modo mantenimiento
    """
    try:
        # Validar configuración
        if config.max_connections < 1 or config.max_connections > 10000:
            raise HTTPException(status_code=400, detail="max_connections must be between 1 and 10000")
        
        if config.timeout_seconds < 1 or config.timeout_seconds > 3600:
            raise HTTPException(status_code=400, detail="timeout_seconds must be between 1 and 3600")
        
        if config.cache_ttl < 60 or config.cache_ttl > 86400:
            raise HTTPException(status_code=400, detail="cache_ttl must be between 60 and 86400 seconds")
        
        # Guardar configuración
        config_dict = config.dict()
        config_dict["updated_at"] = datetime.now().isoformat()
        config_dict["updated_by"] = "system_admin"  # En producción sería el usuario actual
        
        system_db["config"] = config_dict
        
        # Aplicar configuración (simulado)
        applied_changes = []
        
        if config.debug_mode:
            applied_changes.append("Debug mode enabled")
        
        if config.maintenance_mode:
            applied_changes.append("Maintenance mode activated")
        
        if not config.cache_enabled:
            applied_changes.append("Cache disabled")
        
        return SystemResponse(
            message="System configuration updated successfully",
            data={
                "config": config,
                "applied_changes": applied_changes,
                "restart_required": config.debug_mode or config.maintenance_mode,
                "updated_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating system configuration: {str(e)}")

# Endpoints adicionales útiles

@router.get("/health", response_model=SystemResponse)
async def get_system_health():
    """Verificación de salud del sistema"""
    try:
        checks = []
        warnings = []
        errors = []
        recommendations = []
        
        # Verificar CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 90:
            errors.append("High CPU usage detected")
        elif cpu_usage > 70:
            warnings.append("Elevated CPU usage")
        checks.append({"name": "CPU Usage", "status": "ok" if cpu_usage < 70 else "warning", "value": f"{cpu_usage}%"})
        
        # Verificar memoria
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            errors.append("High memory usage detected")
        elif memory.percent > 80:
            warnings.append("Elevated memory usage")
        checks.append({"name": "Memory Usage", "status": "ok" if memory.percent < 80 else "warning", "value": f"{memory.percent}%"})
        
        # Verificar disco
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 95:
            errors.append("Disk space critically low")
        elif disk_percent > 85:
            warnings.append("Disk space running low")
            recommendations.append("Consider cleaning up old files or expanding storage")
        checks.append({"name": "Disk Usage", "status": "ok" if disk_percent < 85 else "warning", "value": f"{disk_percent:.1f}%"})
        
        # Determinar estado general
        if errors:
            status = SystemStatus.CRITICAL
            score = 25
        elif warnings:
            status = SystemStatus.WARNING
            score = 65
        else:
            status = SystemStatus.HEALTHY
            score = 95
        
        health = SystemHealth(
            status=status,
            score=score,
            checks=checks,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations,
            last_check=datetime.now()
        )
        
        return SystemResponse(
            message="System health check completed",
            data=health
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing health check: {str(e)}")

@router.get("/operations/{operation_id}", response_model=SystemResponse)
async def get_operation_status(operation_id: str):
    """Obtener estado de una operación del sistema"""
    try:
        if operation_id not in system_db["operations"]:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        operation = SystemOperation(**system_db["operations"][operation_id])
        
        return SystemResponse(
            message="Operation status retrieved successfully",
            data=operation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving operation status: {str(e)}")
