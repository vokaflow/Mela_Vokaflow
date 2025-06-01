#!/usr/bin/env python3
"""
VokaFlow - Sistema de Gestión de Tareas en Segundo Plano
Sistema robusto para manejar tareas asíncronas, cola de trabajos y monitoreo
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import os

logger = logging.getLogger("vokaflow.task_manager")

class TaskStatus(Enum):
    """Estados de las tareas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """Prioridades de las tareas"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TaskResult:
    """Resultado de una tarea"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    retries: int = 0
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario serializable"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data

@dataclass
class Task:
    """Definición de una tarea"""
    id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: Dict[str, Any] = None
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    category: str = "general"
    created_at: datetime = None
    scheduled_for: Optional[datetime] = None
    depends_on: List[str] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.depends_on is None:
            self.depends_on = []

class VokaFlowTaskManager:
    """
    Gestor de tareas en segundo plano optimizado para VokaFlow
    
    Características:
    - Cola de prioridades
    - Retry automático con backoff
    - Monitoreo y métricas
    - Scheduling de tareas
    - Dependencias entre tareas
    - Workers paralelos
    - Persistencia opcional
    """
    
    def __init__(self, 
                 max_workers: int = 4,
                 enable_redis: bool = True,
                 redis_url: str = "redis://localhost:6379/1"):
        
        self.max_workers = max_workers
        self.enable_redis = enable_redis
        self.redis_url = redis_url
        
        # Colas por prioridad
        self.task_queues = {
            TaskPriority.CRITICAL: queue.PriorityQueue(),
            TaskPriority.HIGH: queue.PriorityQueue(),
            TaskPriority.NORMAL: queue.PriorityQueue(),
            TaskPriority.LOW: queue.PriorityQueue()
        }
        
        # Almacenamiento de tareas y resultados
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self.scheduled_tasks: Dict[str, Task] = {}
        
        # Workers y control
        self.workers: List[threading.Thread] = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "active_workers": 0,
            "queue_sizes": {}
        }
        
        # Redis para persistencia (opcional)
        self.redis_client = None
        if enable_redis:
            self._setup_redis()
        
        # Scheduler para tareas programadas
        self.scheduler_thread = None
        
        logger.info(f"🔧 TaskManager inicializado con {max_workers} workers")

    def _setup_redis(self):
        """Configura conexión a Redis para persistencia"""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis conectado para persistencia de tareas")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible, usando memoria: {e}")
            self.enable_redis = False

    def start(self):
        """Inicia el sistema de tareas"""
        if self.running:
            logger.warning("TaskManager ya está ejecutándose")
            return
        
        self.running = True
        
        # Iniciar workers
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # Iniciar scheduler
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="TaskScheduler",
            daemon=True
        )
        self.scheduler_thread.start()
        
        logger.info(f"🚀 TaskManager iniciado con {len(self.workers)} workers")

    def stop(self, timeout: float = 30.0):
        """Detiene el sistema de tareas"""
        logger.info("🛑 Deteniendo TaskManager...")
        self.running = False
        
        # Esperar a que terminen los workers
        for worker in self.workers:
            worker.join(timeout=timeout/len(self.workers))
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        
        self.executor.shutdown(wait=True)
        logger.info("✅ TaskManager detenido")

    def submit_task(self,
                   func: Callable,
                   args: tuple = (),
                   kwargs: Dict[str, Any] = None,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   name: str = None,
                   category: str = "general",
                   max_retries: int = 3,
                   timeout: Optional[float] = None,
                   delay: Optional[float] = None,
                   depends_on: List[str] = None) -> str:
        """
        Envía una tarea para ejecución
        
        Args:
            func: Función a ejecutar
            args: Argumentos posicionales
            kwargs: Argumentos nominales
            priority: Prioridad de la tarea
            name: Nombre descriptivo
            category: Categoría para organización
            max_retries: Número máximo de reintentos
            timeout: Timeout en segundos
            delay: Retraso antes de ejecutar (en segundos)
            depends_on: Lista de IDs de tareas de las que depende
        
        Returns:
            ID único de la tarea
        """
        task_id = str(uuid.uuid4())
        
        if name is None:
            name = f"{func.__name__}_{task_id[:8]}"
        
        # Crear tarea
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            max_retries=max_retries,
            timeout=timeout,
            category=category,
            depends_on=depends_on or []
        )
        
        # Programar si hay delay
        if delay:
            task.scheduled_for = datetime.now() + timedelta(seconds=delay)
            self.scheduled_tasks[task_id] = task
        else:
            self._queue_task(task)
        
        self.tasks[task_id] = task
        self.stats["total_tasks"] += 1
        
        # Persistir en Redis si está disponible
        if self.redis_client:
            self._persist_task(task)
        
        logger.debug(f"📋 Tarea enviada: {name} ({task_id}) - Prioridad: {priority.name}")
        return task_id

    def _queue_task(self, task: Task):
        """Agrega una tarea a la cola apropiada"""
        if self._check_dependencies(task):
            priority_value = task.priority.value
            timestamp = time.time()  # Para orden FIFO en misma prioridad
            self.task_queues[task.priority].put((priority_value, timestamp, task))
            self._update_queue_stats()
        else:
            # Re-programar si las dependencias no están listas
            task.scheduled_for = datetime.now() + timedelta(seconds=5)
            self.scheduled_tasks[task.id] = task

    def _check_dependencies(self, task: Task) -> bool:
        """Verifica si las dependencias de una tarea están completadas"""
        for dep_id in task.depends_on:
            if dep_id not in self.results:
                return False
            if self.results[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True

    def _worker_loop(self):
        """Loop principal de un worker"""
        worker_name = threading.current_thread().name
        logger.debug(f"👷 Worker {worker_name} iniciado")
        
        while self.running:
            try:
                task = self._get_next_task()
                if task is None:
                    time.sleep(0.1)  # No hay tareas, esperar
                    continue
                
                self.stats["active_workers"] += 1
                self._execute_task(task)
                self.stats["active_workers"] -= 1
                
            except Exception as e:
                logger.error(f"❌ Error en worker {worker_name}: {e}")
                self.stats["active_workers"] = max(0, self.stats["active_workers"] - 1)
        
        logger.debug(f"👷 Worker {worker_name} terminado")

    def _get_next_task(self) -> Optional[Task]:
        """Obtiene la siguiente tarea de mayor prioridad"""
        # Revisar en orden de prioridad
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, 
                        TaskPriority.NORMAL, TaskPriority.LOW]:
            try:
                if not self.task_queues[priority].empty():
                    _, _, task = self.task_queues[priority].get_nowait()
                    self._update_queue_stats()
                    return task
            except queue.Empty:
                continue
        return None

    def _execute_task(self, task: Task):
        """Ejecuta una tarea individual"""
        result = TaskResult(
            task_id=task.id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now(),
            metadata={"category": task.category, "worker": threading.current_thread().name}
        )
        
        logger.info(f"🔄 Ejecutando: {task.name} ({task.id})")
        
        try:
            # Ejecutar con timeout si está especificado
            if task.timeout:
                future = self.executor.submit(task.func, *task.args, **task.kwargs)
                task_result = future.result(timeout=task.timeout)
            else:
                task_result = task.func(*task.args, **task.kwargs)
            
            # Tarea completada exitosamente
            result.status = TaskStatus.COMPLETED
            result.result = task_result
            result.end_time = datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            self.stats["completed_tasks"] += 1
            logger.info(f"✅ Completada: {task.name} ({task.id}) en {result.execution_time:.2f}s")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error en tarea {task.name} ({task.id}): {error_msg}")
            
            result.error = error_msg
            result.end_time = datetime.now()
            result.execution_time = (result.end_time - result.start_time).total_seconds()
            
            # Intentar retry si está configurado
            if result.retries < task.max_retries:
                result.status = TaskStatus.RETRYING
                result.retries += 1
                
                # Re-programar con delay exponencial
                delay = task.retry_delay * (2 ** (result.retries - 1))
                task.scheduled_for = datetime.now() + timedelta(seconds=delay)
                self.scheduled_tasks[task.id] = task
                
                logger.info(f"🔄 Reintentando tarea {task.name} en {delay}s (intento {result.retries}/{task.max_retries})")
            else:
                result.status = TaskStatus.FAILED
                self.stats["failed_tasks"] += 1
        
        self.results[task.id] = result
        
        # Persistir resultado si Redis está disponible
        if self.redis_client:
            self._persist_result(result)

    def _scheduler_loop(self):
        """Loop del programador de tareas"""
        logger.debug("📅 Scheduler iniciado")
        
        while self.running:
            try:
                now = datetime.now()
                tasks_to_schedule = []
                
                # Buscar tareas programadas listas para ejecutar
                for task_id, task in list(self.scheduled_tasks.items()):
                    if task.scheduled_for and task.scheduled_for <= now:
                        tasks_to_schedule.append(task_id)
                
                # Mover tareas a las colas
                for task_id in tasks_to_schedule:
                    task = self.scheduled_tasks.pop(task_id)
                    self._queue_task(task)
                
                time.sleep(1)  # Revisar cada segundo
                
            except Exception as e:
                logger.error(f"❌ Error en scheduler: {e}")
        
        logger.debug("📅 Scheduler terminado")

    def _update_queue_stats(self):
        """Actualiza estadísticas de las colas"""
        self.stats["queue_sizes"] = {
            priority.name: self.task_queues[priority].qsize()
            for priority in TaskPriority
        }

    def _persist_task(self, task: Task):
        """Persiste una tarea en Redis"""
        try:
            key = f"vokaflow:task:{task.id}"
            data = {
                "id": task.id,
                "name": task.name,
                "category": task.category,
                "priority": task.priority.name,
                "created_at": task.created_at.isoformat(),
                "max_retries": task.max_retries
            }
            self.redis_client.hset(key, mapping=data)
            self.redis_client.expire(key, 86400)  # 24 horas
        except Exception as e:
            logger.error(f"Error persistiendo tarea {task.id}: {e}")

    def _persist_result(self, result: TaskResult):
        """Persiste un resultado en Redis"""
        try:
            key = f"vokaflow:result:{result.task_id}"
            self.redis_client.hset(key, mapping=result.to_dict())
            self.redis_client.expire(key, 86400)  # 24 horas
        except Exception as e:
            logger.error(f"Error persistiendo resultado {result.task_id}: {e}")

    # API Pública
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Obtiene el estado de una tarea"""
        return self.results.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea (solo si no ha empezado)"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            
            result = TaskResult(
                task_id=task_id,
                status=TaskStatus.CANCELLED,
                end_time=datetime.now()
            )
            self.results[task_id] = result
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        self._update_queue_stats()
        return {
            **self.stats,
            "scheduled_tasks": len(self.scheduled_tasks),
            "running": self.running,
            "workers_count": len(self.workers)
        }

    def list_tasks(self, 
                  category: Optional[str] = None,
                  status: Optional[TaskStatus] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """Lista tareas con filtros opcionales"""
        tasks = []
        
        for task_id, result in self.results.items():
            if category and self.tasks[task_id].category != category:
                continue
            if status and result.status != status:
                continue
            
            task_info = {
                "id": task_id,
                "name": self.tasks[task_id].name,
                "category": self.tasks[task_id].category,
                "status": result.status.value,
                "created_at": self.tasks[task_id].created_at.isoformat(),
                "execution_time": result.execution_time,
                "retries": result.retries
            }
            
            if result.error:
                task_info["error"] = result.error
            
            tasks.append(task_info)
        
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)[:limit]

# Instancia global del gestor de tareas
task_manager = VokaFlowTaskManager()

# Funciones de conveniencia
def submit_task(*args, **kwargs) -> str:
    """Función de conveniencia para enviar tareas"""
    return task_manager.submit_task(*args, **kwargs)

def get_task_status(task_id: str) -> Optional[TaskResult]:
    """Función de conveniencia para obtener estado de tarea"""
    return task_manager.get_task_status(task_id)

def start_task_manager():
    """Inicia el gestor de tareas"""
    task_manager.start()

def stop_task_manager():
    """Detiene el gestor de tareas"""
    task_manager.stop() 