#!/usr/bin/env python3
"""
Router para High Scale Task Manager - VokaFlow
Gestión de tareas de alta escala con Redis distribuido
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Importar el High Scale Task Manager
from src.backend.core.high_scale_task_manager import (
    HighScaleTaskManager,
    TaskPriority,
    WorkerType,
    TaskStatus,
    submit_high_scale_task,
    get_scale_metrics,
    initialize_high_scale_system,
    shutdown_high_scale_system,
    high_scale_task_manager
)

logger = logging.getLogger("vokaflow.routers.high_scale_tasks")

# Crear router
router = APIRouter(
    prefix="/high-scale-tasks",
    tags=["High Scale Tasks"],
    responses={404: {"description": "Not found"}}
)

# Modelos Pydantic para el API

class TaskSubmissionRequest(BaseModel):
    """Solicitud para enviar una tarea de alta escala"""
    function_name: str = Field(..., description="Nombre de la función a ejecutar (e.g., 'math.sqrt')")
    args: List[Any] = Field(default=[], description="Argumentos posicionales para la función")
    kwargs: Dict[str, Any] = Field(default={}, description="Argumentos con nombre para la función")
    priority: str = Field(default="NORMAL", description="Prioridad de la tarea")
    worker_type: str = Field(default="GENERAL_PURPOSE", description="Tipo de worker especializado")
    name: Optional[str] = Field(None, description="Nombre personalizado para la tarea")
    category: str = Field(default="general", description="Categoría de la tarea")
    max_retries: int = Field(default=3, ge=0, le=10, description="Número máximo de reintentos")
    timeout: Optional[float] = Field(None, ge=1, le=300, description="Timeout en segundos")
    
    @validator('priority')
    def validate_priority(cls, v):
        try:
            TaskPriority[v.upper()]
            return v.upper()
        except KeyError:
            valid_priorities = [p.name for p in TaskPriority]
            raise ValueError(f"Prioridad inválida. Opciones válidas: {valid_priorities}")
    
    @validator('worker_type')
    def validate_worker_type(cls, v):
        try:
            WorkerType[v.upper()]
            return v.upper()
        except KeyError:
            valid_types = [wt.name for wt in WorkerType]
            raise ValueError(f"Tipo de worker inválido. Opciones válidas: {valid_types}")

class TaskSubmissionResponse(BaseModel):
    """Respuesta al enviar una tarea"""
    task_id: str
    status: str = "submitted"
    message: str
    estimated_completion: Optional[str] = None

class TaskMetricsResponse(BaseModel):
    """Respuesta con métricas del sistema"""
    status: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    active_workers: int
    throughput_per_second: float
    system_resources: Dict[str, Any]
    worker_pools: Dict[str, Any]
    redis_status: Dict[str, Any]
    recent_tasks: List[Dict[str, Any]]
    timestamp: float

class SystemControlRequest(BaseModel):
    """Solicitud de control del sistema"""
    action: str = Field(..., description="Acción a realizar: initialize, shutdown, restart")
    force: bool = Field(default=False, description="Forzar la operación")

class DLQTaskResponse(BaseModel):
    """Respuesta con tareas de Dead Letter Queue"""
    total_tasks: int
    tasks: List[Dict[str, Any]]
    worker_types: List[str]

# Funciones de utilidad

def resolve_function_from_name(func_name: str):
    """Resolver función desde nombre de string"""
    try:
        if '.' in func_name:
            module_name, function_name = func_name.rsplit('.', 1)
            import importlib
            module = importlib.import_module(module_name)
            return getattr(module, function_name)
        else:
            # Funciones built-in
            import builtins
            if hasattr(builtins, func_name):
                return getattr(builtins, func_name)
            else:
                # Funciones comunes para demostración
                demo_functions = {
                    'demo_cpu_task': lambda x: sum(i*i for i in range(x)),
                    'demo_io_task': lambda: "IO task completed",
                    'demo_network_task': lambda url: f"Network request to {url}",
                    'demo_memory_task': lambda size: [0] * size,
                    'demo_error_task': lambda: 1/0,  # Para probar manejo de errores
                }
                if func_name in demo_functions:
                    return demo_functions[func_name]
        
        raise ImportError(f"Función no encontrada: {func_name}")
    except Exception as e:
        logger.error(f"Error resolviendo función {func_name}: {e}")
        raise

# Endpoints del API

@router.post("/submit", response_model=TaskSubmissionResponse)
async def submit_task(request: TaskSubmissionRequest):
    """
    Enviar una tarea al sistema de alta escala
    
    Permite enviar tareas con diferentes prioridades, tipos de worker y configuraciones.
    """
    try:
        # Resolver función
        func = resolve_function_from_name(request.function_name)
        
        # Convertir enums
        priority = TaskPriority[request.priority]
        worker_type = WorkerType[request.worker_type]
        
        # Enviar tarea
        task_id = await submit_high_scale_task(
            func=func,
            args=tuple(request.args),
            kwargs=request.kwargs,
            priority=priority,
            worker_type=worker_type,
            name=request.name,
            category=request.category,
            max_retries=request.max_retries,
            timeout=request.timeout
        )
        
        # Estimar tiempo de completación (básico)
        estimated_completion = None
        if request.timeout:
            from datetime import datetime, timedelta
            estimated_completion = (datetime.now() + timedelta(seconds=request.timeout)).isoformat()
        
        logger.info(f"🚀 Tarea enviada: {request.function_name} -> {task_id}")
        
        return TaskSubmissionResponse(
            task_id=task_id,
            status="submitted",
            message=f"Tarea {request.function_name} enviada exitosamente",
            estimated_completion=estimated_completion
        )
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ImportError as e:
        logger.error(f"Error importando función: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Función no encontrada: {request.function_name}"
        )
    except Exception as e:
        logger.error(f"Error enviando tarea: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/metrics", response_model=TaskMetricsResponse)
async def get_system_metrics():
    """
    Obtener métricas completas del sistema de alta escala
    
    Incluye información sobre tareas, workers, recursos del sistema y estado de Redis.
    """
    try:
        metrics = await get_scale_metrics()
        
        # Estructurar respuesta
        response = TaskMetricsResponse(
            status=metrics.get("status", "unknown"),
            total_tasks=metrics.get("total_tasks", 0),
            completed_tasks=metrics.get("completed_tasks", 0),
            failed_tasks=metrics.get("failed_tasks", 0),
            pending_tasks=metrics.get("total_pending_tasks", 0),
            active_workers=metrics.get("active_workers", 0),
            throughput_per_second=metrics.get("throughput_per_second", 0.0),
            system_resources=metrics.get("system_resources", {}),
            worker_pools=metrics.get("worker_pools", {}),
            redis_status={
                "nodes": metrics.get("redis_nodes", 0),
                "partitions": metrics.get("partitions", 0),
                "memory_mode": metrics.get("memory_mode", {})
            },
            recent_tasks=metrics.get("recent_tasks", []),
            timestamp=metrics.get("timestamp", 0)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo métricas: {str(e)}"
        )

@router.get("/status")
async def get_system_status():
    """
    Obtener estado general del sistema de alta escala
    """
    try:
        global high_scale_task_manager
        
        if high_scale_task_manager is None:
            return {
                "status": "not_initialized",
                "message": "Sistema de alta escala no inicializado",
                "initialized": False,
                "recommendations": [
                    "Llama al endpoint POST /initialize para inicializar el sistema",
                    "Verifica que Redis esté funcionando",
                    "Revisa los logs para más detalles"
                ]
            }
        
        metrics = await get_scale_metrics()
        
        return {
            "status": "running",
            "message": "Sistema de alta escala operativo",
            "initialized": True,
            "uptime": metrics.get("timestamp", 0),
            "redis_nodes": metrics.get("redis_nodes", 0),
            "total_workers": sum(
                pool_info.get("max_workers", 0) 
                for pool_info in metrics.get("worker_pools", {}).values()
            ),
            "memory_mode": metrics.get("memory_mode", {}).get("enabled", False),
            "performance": {
                "completed_tasks": metrics.get("completed_tasks", 0),
                "failed_tasks": metrics.get("failed_tasks", 0),
                "pending_tasks": metrics.get("total_pending_tasks", 0),
                "throughput": metrics.get("throughput_per_second", 0.0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return {
            "status": "error",
            "message": f"Error obteniendo estado: {str(e)}",
            "initialized": False
        }

@router.post("/control")
async def control_system(request: SystemControlRequest):
    """
    Controlar el sistema de alta escala (inicializar, apagar, reiniciar)
    """
    try:
        action = request.action.lower()
        
        if action == "initialize":
            await initialize_high_scale_system()
            return {
                "status": "success",
                "message": "Sistema de alta escala inicializado correctamente",
                "action": action
            }
            
        elif action == "shutdown":
            await shutdown_high_scale_system()
            return {
                "status": "success",
                "message": "Sistema de alta escala apagado correctamente",
                "action": action
            }
            
        elif action == "restart":
            # Shutdown y luego initialize
            await shutdown_high_scale_system()
            await asyncio.sleep(2)  # Esperar un poco
            await initialize_high_scale_system()
            return {
                "status": "success",
                "message": "Sistema de alta escala reiniciado correctamente",
                "action": action
            }
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Acción no válida: {action}. Opciones: initialize, shutdown, restart"
            )
            
    except Exception as e:
        logger.error(f"Error controlando sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando acción {request.action}: {str(e)}"
        )

@router.get("/dlq", response_model=DLQTaskResponse)
async def get_dead_letter_queue_tasks(
    worker_type: Optional[str] = Query(None, description="Filtrar por tipo de worker"),
    limit: int = Query(50, ge=1, le=500, description="Número máximo de tareas a retornar")
):
    """
    Obtener tareas de Dead Letter Queue (tareas fallidas)
    """
    try:
        global high_scale_task_manager
        
        if high_scale_task_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sistema de alta escala no inicializado"
            )
        
        # Validar worker_type si se proporciona
        if worker_type:
            try:
                WorkerType[worker_type.upper()]
                worker_type = worker_type.upper()
            except KeyError:
                valid_types = [wt.name for wt in WorkerType]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de worker inválido. Opciones válidas: {valid_types}"
                )
        
        dlq_tasks = await high_scale_task_manager.get_dlq_tasks(worker_type, limit)
        
        return DLQTaskResponse(
            total_tasks=len(dlq_tasks),
            tasks=dlq_tasks,
            worker_types=list(set(task.get("worker_type", "unknown") for task in dlq_tasks))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo tareas DLQ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tareas DLQ: {str(e)}"
        )

@router.post("/dlq/{task_id}/retry")
async def retry_dlq_task(task_id: str = Path(..., description="ID de la tarea a reintentar")):
    """
    Reintentar una tarea desde Dead Letter Queue
    """
    try:
        global high_scale_task_manager
        
        if high_scale_task_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sistema de alta escala no inicializado"
            )
        
        success = await high_scale_task_manager.retry_dlq_task(task_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Tarea {task_id} reintentada desde DLQ",
                "task_id": task_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea {task_id} no encontrada en DLQ"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reintentando tarea DLQ {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reintentando tarea DLQ: {str(e)}"
        )

@router.get("/workers")
async def get_worker_info():
    """
    Obtener información detallada sobre los workers
    """
    try:
        metrics = await get_scale_metrics()
        worker_pools = metrics.get("worker_pools", {})
        
        worker_info = {}
        for worker_type, pool_info in worker_pools.items():
            worker_info[worker_type] = {
                "max_workers": pool_info.get("max_workers", 0),
                "pool_type": pool_info.get("pool_type", "unknown"),
                "description": get_worker_type_description(worker_type)
            }
        
        return {
            "worker_pools": worker_info,
            "total_workers": sum(info["max_workers"] for info in worker_info.values()),
            "system_resources": metrics.get("system_resources", {}),
            "recommendations": get_worker_recommendations(metrics)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo información de workers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información de workers: {str(e)}"
        )

def get_worker_type_description(worker_type: str) -> str:
    """Obtener descripción del tipo de worker"""
    descriptions = {
        "CPU_INTENSIVE": "Tareas que requieren mucho procesamiento de CPU (cálculos matemáticos, algoritmos)",
        "IO_INTENSIVE": "Tareas de entrada/salida (lectura/escritura de archivos, base de datos)",
        "MEMORY_INTENSIVE": "Tareas que requieren mucha memoria (procesamiento de grandes datasets)",
        "NETWORK_INTENSIVE": "Tareas de red (llamadas HTTP, APIs externas)",
        "GENERAL_PURPOSE": "Tareas generales que no requieren optimizaciones específicas"
    }
    return descriptions.get(worker_type, "Tipo de worker desconocido")

def get_worker_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generar recomendaciones basadas en métricas"""
    recommendations = []
    
    system_resources = metrics.get("system_resources", {})
    cpu_percent = system_resources.get("cpu_percent", 0)
    memory_percent = system_resources.get("memory_percent", 0)
    
    if cpu_percent > 80:
        recommendations.append("CPU usage alto - considera reducir workers CPU intensivos")
    elif cpu_percent < 20:
        recommendations.append("CPU usage bajo - puedes incrementar workers CPU intensivos")
    
    if memory_percent > 85:
        recommendations.append("Memoria alta - reduce workers memory intensivos")
    elif memory_percent < 30:
        recommendations.append("Memoria baja - puedes incrementar workers memory intensivos")
    
    pending_tasks = metrics.get("total_pending_tasks", 0)
    if pending_tasks > 1000:
        recommendations.append("Cola de tareas alta - considera incrementar workers")
    
    return recommendations

# Endpoints de demostración

@router.post("/demo/submit-demo-tasks")
async def submit_demo_tasks(count: int = Query(5, ge=1, le=50, description="Número de tareas demo a enviar")):
    """
    Enviar tareas de demostración para probar el sistema
    """
    try:
        demo_tasks = [
            {"func": "demo_cpu_task", "args": [1000], "priority": "HIGH", "worker_type": "CPU_INTENSIVE"},
            {"func": "demo_io_task", "args": [], "priority": "NORMAL", "worker_type": "IO_INTENSIVE"},
            {"func": "demo_network_task", "args": ["https://api.example.com"], "priority": "LOW", "worker_type": "NETWORK_INTENSIVE"},
            {"func": "demo_memory_task", "args": [100], "priority": "NORMAL", "worker_type": "MEMORY_INTENSIVE"},
            {"func": "math.sqrt", "args": [16], "priority": "NORMAL", "worker_type": "GENERAL_PURPOSE"},
        ]
        
        submitted_tasks = []
        
        for i in range(min(count, len(demo_tasks))):
            task = demo_tasks[i % len(demo_tasks)]
            
            try:
                func = resolve_function_from_name(task["func"])
                task_id = await submit_high_scale_task(
                    func=func,
                    args=tuple(task["args"]),
                    priority=TaskPriority[task["priority"]],
                    worker_type=WorkerType[task["worker_type"]],
                    name=f"demo_{task['func']}_{i}",
                    category="demo"
                )
                
                submitted_tasks.append({
                    "task_id": task_id,
                    "function": task["func"],
                    "priority": task["priority"],
                    "worker_type": task["worker_type"]
                })
                
            except Exception as e:
                logger.error(f"Error enviando tarea demo {task['func']}: {e}")
                continue
        
        return {
            "status": "success",
            "message": f"Se enviaron {len(submitted_tasks)} tareas de demostración",
            "submitted_tasks": submitted_tasks,
            "recommendation": "Usa GET /metrics para ver el progreso de las tareas"
        }
        
    except Exception as e:
        logger.error(f"Error enviando tareas demo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando tareas demo: {str(e)}"
        )

logger.info("🔥 Router High Scale Tasks cargado exitosamente") 