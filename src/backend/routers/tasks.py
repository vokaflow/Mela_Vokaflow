#!/usr/bin/env python3
"""
VokaFlow - Router de Gestión de Tareas
API para manejar y monitorear tareas en segundo plano
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from datetime import datetime

from ..core.task_manager import (
    task_manager, TaskStatus, TaskPriority, 
    submit_task, get_task_status
)

logger = logging.getLogger("vokaflow.tasks")

# Router
router = APIRouter(tags=["Tasks Management"])

# Modelos Pydantic
class TaskSubmissionRequest(BaseModel):
    name: str
    function_name: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    category: str = "general"
    max_retries: int = 3
    timeout: Optional[float] = None
    delay: Optional[float] = None

class TaskResponse(BaseModel):
    task_id: str
    name: str
    status: str
    message: str
    created_at: str
    execution_time: Optional[float] = None
    retries: int = 0
    error: Optional[str] = None

class TaskStatsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    active_workers: int
    scheduled_tasks: int
    queue_sizes: Dict[str, int]
    running: bool
    workers_count: int

class TaskListResponse(BaseModel):
    tasks: List[Dict[str, Any]]
    total: int
    page: int
    per_page: int

# Funciones auxiliares registradas para ejecutar via API
REGISTERED_FUNCTIONS = {
    "example_task": lambda x, y: f"Resultado: {x + y}",
    "vicky_process": lambda message: f"Vicky procesó: {message}",
    "cleanup_temp": lambda: "Archivos temporales limpiados",
    "backup_data": lambda path: f"Backup creado en {path}",
    "send_notification": lambda user, msg: f"Notificación enviada a {user}: {msg}",
    "analyze_audio": lambda file_path: f"Audio analizado: {file_path}",
    "generate_report": lambda report_type: f"Reporte {report_type} generado",
    "optimize_models": lambda: "Modelos de IA optimizados"
}

@router.get("/stats", response_model=TaskStatsResponse)
async def get_task_stats():
    """
    📊 Obtener estadísticas del sistema de tareas
    
    Retorna:
    - Número total de tareas
    - Tareas completadas y falladas
    - Workers activos
    - Tareas programadas
    - Tamaños de colas por prioridad
    """
    try:
        stats = task_manager.get_stats()
        return TaskStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de tareas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.get("/list", response_model=TaskListResponse)
async def list_tasks(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por estado"),
    page: int = Query(1, ge=1, description="Página"),
    per_page: int = Query(50, ge=1, le=200, description="Tareas por página")
):
    """
    📋 Listar tareas con filtros opcionales
    
    Permite filtrar por:
    - Categoría
    - Estado (pending, running, completed, failed, etc.)
    - Paginación
    """
    try:
        status_enum = None
        if status_filter:
            try:
                status_enum = TaskStatus(status_filter.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {status_filter}"
                )
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Obtener tareas (el task manager no tiene paginación nativa, así que filtramos después)
        all_tasks = task_manager.list_tasks(
            category=category,
            status=status_enum,
            limit=1000  # Obtener muchas para paginar
        )
        
        # Paginar
        total = len(all_tasks)
        tasks = all_tasks[offset:offset + per_page]
        
        return TaskListResponse(
            tasks=tasks,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando tareas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando tareas: {str(e)}"
        )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_details(task_id: str):
    """
    🔍 Obtener detalles de una tarea específica
    
    Retorna información detallada incluyendo:
    - Estado actual
    - Tiempo de ejecución
    - Errores si los hay
    - Metadatos
    """
    try:
        result = get_task_status(task_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea {task_id} no encontrada"
            )
        
        task = task_manager.tasks.get(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Información de tarea {task_id} no disponible"
            )
        
        return TaskResponse(
            task_id=task_id,
            name=task.name,
            status=result.status.value,
            message=f"Tarea en estado: {result.status.value}",
            created_at=task.created_at.isoformat(),
            execution_time=result.execution_time,
            retries=result.retries,
            error=result.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles de tarea {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalles: {str(e)}"
        )

@router.post("/submit", response_model=TaskResponse)
async def submit_new_task(task_request: TaskSubmissionRequest):
    """
    📤 Enviar una nueva tarea para ejecución
    
    Permite enviar tareas de las funciones registradas:
    - example_task
    - vicky_process
    - cleanup_temp
    - backup_data
    - send_notification
    - analyze_audio
    - generate_report
    - optimize_models
    """
    try:
        # Validar función
        if task_request.function_name not in REGISTERED_FUNCTIONS:
            available_functions = list(REGISTERED_FUNCTIONS.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Función '{task_request.function_name}' no registrada. "
                       f"Disponibles: {available_functions}"
            )
        
        # Validar prioridad
        try:
            priority = TaskPriority[task_request.priority.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prioridad inválida: {task_request.priority}. "
                       f"Válidas: {[p.name for p in TaskPriority]}"
            )
        
        # Obtener función
        func = REGISTERED_FUNCTIONS[task_request.function_name]
        
        # Enviar tarea
        task_id = submit_task(
            func=func,
            args=tuple(task_request.args),
            kwargs=task_request.kwargs,
            priority=priority,
            name=task_request.name,
            category=task_request.category,
            max_retries=task_request.max_retries,
            timeout=task_request.timeout,
            delay=task_request.delay
        )
        
        return TaskResponse(
            task_id=task_id,
            name=task_request.name,
            status="pending",
            message=f"Tarea '{task_request.name}' enviada exitosamente",
            created_at=datetime.now().isoformat(),
            retries=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando tarea: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando tarea: {str(e)}"
        )

@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    ❌ Cancelar una tarea pendiente
    
    Solo puede cancelar tareas que aún no han empezado a ejecutarse
    """
    try:
        success = task_manager.cancel_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudo cancelar la tarea {task_id}. "
                       "Puede que ya esté ejecutándose o no exista."
            )
        
        return {
            "message": f"Tarea {task_id} cancelada exitosamente",
            "task_id": task_id,
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelando tarea {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelando tarea: {str(e)}"
        )

@router.get("/categories/list")
async def list_task_categories():
    """
    📂 Listar categorías de tareas disponibles
    """
    try:
        # Obtener categorías únicas de las tareas existentes
        categories = set()
        for task in task_manager.tasks.values():
            categories.add(task.category)
        
        # Agregar categorías predefinidas
        predefined_categories = [
            "general", "vicky", "audio", "backup", 
            "notification", "cleanup", "analysis", "report"
        ]
        
        categories.update(predefined_categories)
        
        return {
            "categories": sorted(list(categories)),
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error listando categorías: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando categorías: {str(e)}"
        )

@router.get("/functions/list")
async def list_available_functions():
    """
    🔧 Listar funciones disponibles para ejecutar como tareas
    """
    try:
        functions_info = []
        
        for func_name, func in REGISTERED_FUNCTIONS.items():
            # Intentar obtener información de la función
            doc = func.__doc__ or "Sin descripción disponible"
            
            functions_info.append({
                "name": func_name,
                "description": doc.strip(),
                "category": _get_function_category(func_name)
            })
        
        return {
            "functions": functions_info,
            "total": len(functions_info)
        }
        
    except Exception as e:
        logger.error(f"Error listando funciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando funciones: {str(e)}"
        )

@router.post("/batch")
async def submit_batch_tasks(tasks: List[TaskSubmissionRequest]):
    """
    📦 Enviar múltiples tareas en lote
    
    Permite enviar varias tareas de una vez
    """
    try:
        if len(tasks) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden enviar más de 100 tareas en un lote"
            )
        
        submitted_tasks = []
        errors = []
        
        for i, task_request in enumerate(tasks):
            try:
                # Validar función
                if task_request.function_name not in REGISTERED_FUNCTIONS:
                    errors.append({
                        "index": i,
                        "error": f"Función '{task_request.function_name}' no registrada"
                    })
                    continue
                
                # Validar prioridad
                try:
                    priority = TaskPriority[task_request.priority.upper()]
                except KeyError:
                    errors.append({
                        "index": i,
                        "error": f"Prioridad inválida: {task_request.priority}"
                    })
                    continue
                
                # Obtener función y enviar tarea
                func = REGISTERED_FUNCTIONS[task_request.function_name]
                
                task_id = submit_task(
                    func=func,
                    args=tuple(task_request.args),
                    kwargs=task_request.kwargs,
                    priority=priority,
                    name=task_request.name,
                    category=task_request.category,
                    max_retries=task_request.max_retries,
                    timeout=task_request.timeout,
                    delay=task_request.delay
                )
                
                submitted_tasks.append({
                    "index": i,
                    "task_id": task_id,
                    "name": task_request.name,
                    "status": "submitted"
                })
                
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e)
                })
        
        return {
            "submitted_tasks": submitted_tasks,
            "total_submitted": len(submitted_tasks),
            "errors": errors,
            "total_errors": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando tareas en lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando tareas en lote: {str(e)}"
        )

def _get_function_category(func_name: str) -> str:
    """Determina la categoría de una función basada en su nombre"""
    if "vicky" in func_name.lower():
        return "vicky"
    elif "audio" in func_name.lower() or "voice" in func_name.lower():
        return "audio"
    elif "backup" in func_name.lower():
        return "backup"
    elif "notification" in func_name.lower() or "notify" in func_name.lower():
        return "notification"
    elif "cleanup" in func_name.lower() or "clean" in func_name.lower():
        return "cleanup"
    elif "analyze" in func_name.lower() or "analysis" in func_name.lower():
        return "analysis"
    elif "report" in func_name.lower():
        return "report"
    else:
        return "general" 