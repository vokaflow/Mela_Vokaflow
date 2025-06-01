# ACTIVADO: High Scale Task Manager configurado para Redis single-node
import time
_last_log_time = 0
_log_interval = 5  # segundos

def rate_limited_log(message, level="info"):
    global _last_log_time
    current_time = time.time()
    if current_time - _last_log_time > _log_interval:
        getattr(logger, level)(message)
        _last_log_time = current_time

#!/usr/bin/env python3
"""
VokaFlow - Sistema de Tareas de Alta Escala
TaskManager optimizado para millones de solicitudes por segundo
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import redis.asyncio as aioredis

# High Scale Task Manager - ACTIVADO
logger = logging.getLogger("vokaflow.high_scale_task_manager")
import json
import time
import uuid
import hashlib
import redis.asyncio as aioredis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union, Set
from enum import Enum, IntEnum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing
import queue
import os
import signal
from collections import defaultdict, deque
import psutil
import statistics

logger = logging.getLogger("vokaflow.high_scale_task_manager")

class TaskPriority(IntEnum):
    """Prioridades extendidas para alta escala (0 = más alta prioridad)"""
    EMERGENCY = 0      # Emergencias críticas del sistema
    CRITICAL = 1       # Tareas críticas del sistema
    HIGH = 2          # Alta prioridad
    NORMAL = 3        # Prioridad normal
    LOW = 4           # Baja prioridad
    BATCH = 5         # Procesamiento en lotes
    BACKGROUND = 6    # Tareas de fondo
    MAINTENANCE = 7   # Mantenimiento del sistema

class TaskStatus(Enum):
    """Estados extendidos de las tareas"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"

class WorkerType(Enum):
    """Tipos de workers especializados"""
    CPU_INTENSIVE = "cpu_intensive"
    IO_INTENSIVE = "io_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    NETWORK_INTENSIVE = "network_intensive"
    GENERAL_PURPOSE = "general_purpose"

@dataclass
class TaskMetrics:
    """Métricas avanzadas de tareas"""
    task_id: str
    priority: TaskPriority
    queue_time: float = 0.0
    execution_time: float = 0.0
    memory_usage: int = 0
    cpu_usage: float = 0.0
    network_io: int = 0
    disk_io: int = 0
    retries: int = 0
    worker_id: str = ""
    worker_type: WorkerType = WorkerType.GENERAL_PURPOSE
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class ScalableTask:
    """Tarea optimizada para alta escala"""
    id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: Dict[str, Any] = None
    priority: TaskPriority = TaskPriority.NORMAL
    worker_type: WorkerType = WorkerType.GENERAL_PURPOSE
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    rate_limit: Optional[int] = None  # requests per second
    category: str = "general"
    tags: List[str] = None
    dependencies: List[str] = None
    partition_key: str = ""  # Para distribución
    estimated_duration: float = 1.0
    memory_requirement: int = 64  # MB
    cpu_requirement: float = 0.1  # CPU cores
    created_at: datetime = None
    scheduled_for: Optional[datetime] = None

class CircuitBreaker:
    """Circuit breaker para prevenir cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e

class RateLimiter:
    """Rate limiter avanzado con sliding window"""
    
    def __init__(self, max_requests: int, window_size: int = 1):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        now = time.time()
        # Limpiar requests antiguos
        while self.requests and now - self.requests[0] > self.window_size:
            self.requests.popleft()
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

class HighScaleTaskManager:
    """
    Gestor de tareas de alta escala para millones de solicitudes por segundo
    
    Características:
        - Workers distribuidos y especializados
    - Colas de prioridad con Redis Cluster
    - Load balancing automático
    - Circuit breakers y rate limiting
    - Auto-scaling de workers
    - Monitoreo en tiempo real
    - Particionado de tareas
    """
    
    def __init__(self,
                 redis_cluster_nodes: List[str] = None,
                 max_workers_per_type: Dict[WorkerType, int] = None,
                 enable_auto_scaling: bool = True,
                 enable_monitoring: bool = True,
                 partition_count: int = 16):
        
        # Configuración de Redis (single-node por defecto)
        self.redis_cluster_nodes = redis_cluster_nodes or [
            "redis://localhost:6379"  # Single Redis instance
        ]
        
        # Configuración de workers por tipo
        self.max_workers_per_type = max_workers_per_type or {
            WorkerType.CPU_INTENSIVE: multiprocessing.cpu_count(),
            WorkerType.IO_INTENSIVE: multiprocessing.cpu_count() * 2,
            WorkerType.MEMORY_INTENSIVE: max(1, multiprocessing.cpu_count() // 2),
            WorkerType.NETWORK_INTENSIVE: multiprocessing.cpu_count() * 4,
            WorkerType.GENERAL_PURPOSE: multiprocessing.cpu_count()
        }
        
        self.enable_auto_scaling = enable_auto_scaling
        self.enable_monitoring = enable_monitoring
        self.partition_count = partition_count
        
        # Pools de workers especializados
        self.worker_pools = {}
        self.worker_metrics = defaultdict(dict)
        self.worker_health = defaultdict(bool)
        
        # Colas distribuidas por prioridad y tipo
        self.redis_pools = {}
        self.queue_keys = {}
        
        # Métricas y monitoreo
        self.global_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "avg_queue_time": 0.0,
            "avg_execution_time": 0.0,
            "throughput_per_second": 0.0,
            "active_workers": 0,
            "queue_lengths": defaultdict(int)
        }
        
        # Rate limiters por categoría
        self.rate_limiters = defaultdict(lambda: RateLimiter(10000))  # 10K per second default
        
        # Circuit breakers por función
        self.circuit_breakers = defaultdict(lambda: CircuitBreaker())
        
        # Cache de funciones compiladas
        self.function_cache = {}
        
        # Estado del sistema
        self.running = False
        self.monitoring_task = None
        self.auto_scaler_task = None
        self.memory_queues = defaultdict(list)  # Fallback en memoria
        self.processed_tasks = []  # Historial de tareas procesadas
        
        logger.info(f"🚀 HighScaleTaskManager inicializado para {sum(self.max_workers_per_type.values())} workers")

    async def initialize(self):
        """Inicializar el sistema distribuido"""
        try:
            # Conectar a Redis Cluster
            await self._setup_redis_cluster()
            
            # Inicializar worker pools
            await self._setup_worker_pools()
            
            # Configurar colas distribuidas
            await self._setup_distributed_queues()
            
            # Iniciar monitoreo
            if self.enable_monitoring:
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Iniciar auto-scaling
            if self.enable_auto_scaling:
                self.auto_scaler_task = asyncio.create_task(self._auto_scaling_loop())
            
            # Iniciar workers Redis distribuidos
            await self._start_redis_workers()
            
            self.running = True
            logger.info("✅ HighScaleTaskManager inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando HighScaleTaskManager: {e}")
            raise

    async def _setup_redis_cluster(self):
        """Configurar conexiones a Redis (single-node o cluster)"""
        for i, node_url in enumerate(self.redis_cluster_nodes):
            try:
                pool = aioredis.ConnectionPool.from_url(
                    node_url,
                    max_connections=20,  # Reducido para single-node
                    retry_on_timeout=True,
                    health_check_interval=60  # Menos frecuente
                )
                redis_client = aioredis.Redis(connection_pool=pool)
                await redis_client.ping()
                self.redis_pools[f"node_{i}"] = redis_client
                logger.info(f"✅ Conectado a Redis node: {node_url}")
            except Exception as e:
                logger.error(f"❌ Error conectando a Redis {node_url}: {e}")
                # En modo single-node, esto es crítico
                if len(self.redis_cluster_nodes) == 1:
                    logger.warning("⚠️ Redis single-node no disponible, usando modo memoria")

    async def _setup_worker_pools(self):
        """Configurar pools de workers especializados"""
        for worker_type, max_workers in self.max_workers_per_type.items():
            if worker_type == WorkerType.CPU_INTENSIVE:
                # ProcessPoolExecutor para tareas CPU-intensive
                self.worker_pools[worker_type] = ProcessPoolExecutor(
                    max_workers=max_workers,
                    mp_context=multiprocessing.get_context('spawn')
                )
            else:
                # ThreadPoolExecutor para I/O y tareas generales
                self.worker_pools[worker_type] = ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix=f"Worker-{worker_type.value}"
                )
            
            logger.info(f"✅ Pool de workers {worker_type.value}: {max_workers} workers")

    async def _setup_distributed_queues(self):
        """Configurar colas distribuidas por prioridad"""
        for priority in TaskPriority:
            for worker_type in WorkerType:
                for partition in range(self.partition_count):
                    queue_key = f"vokaflow:queue:{priority.name}:{worker_type.value}:{partition}"
                    self.queue_keys[(priority, worker_type, partition)] = queue_key

    async def _start_redis_workers(self):
        """Iniciar workers que consumen colas Redis distribuidas"""
        logger.info("🚀 Iniciando workers Redis distribuidos...")
        
        # Crear workers especializados para cada tipo
        self.worker_tasks = []
        
        for worker_type, max_workers in self.max_workers_per_type.items():
            # Crear múltiples workers por tipo
            for worker_id in range(max_workers):
                worker_task = asyncio.create_task(
                    self._redis_worker_loop(worker_type, worker_id)
                )
                self.worker_tasks.append(worker_task)
                logger.info(f"👷 Worker {worker_type.value}-{worker_id} iniciado")
        
        logger.info(f"✅ {len(self.worker_tasks)} workers Redis iniciados")

    async def _redis_worker_loop(self, worker_type: WorkerType, worker_id: int):
        """Worker loop que consume tareas de Redis distribuido"""
        worker_name = f"{worker_type.value}-{worker_id}"
        logger.info(f"🔄 Worker {worker_name} iniciado")
        
        # Configurar colas que este worker va a monitorear
        monitored_queues = []
        for priority in TaskPriority:
            for partition in range(self.partition_count):
                queue_key = self.queue_keys.get((priority, worker_type, partition))
                if queue_key:
                    monitored_queues.append((queue_key, priority))
        
        # Ordenar por prioridad (menor valor = mayor prioridad)
        monitored_queues.sort(key=lambda x: x[1].value)
        
        consecutive_empty_polls = 0
        max_empty_polls = 30  # 30 polls vacíos antes de aumentar el sleep
        
        while self.running:
            try:
                task_processed = False
                
                # Procesar colas en orden de prioridad
                for queue_key, priority in monitored_queues:
                    # Seleccionar nodo Redis para esta cola
                    redis_client = self._select_redis_node(
                        hash(queue_key) % len(self.redis_pools) if self.redis_pools else 0
                    )
                    
                    if not redis_client:
                        continue
                    
                    try:
                        # ZPOPMIN para obtener tarea con mayor prioridad (menor score)
                        result = await redis_client.zpopmin(queue_key, count=1)
                        
                        if result:
                            task_data, score = result[0]  # (task_json, score)
                            await self._process_redis_task(task_data, worker_name, priority)
                            task_processed = True
                            consecutive_empty_polls = 0
                            break  # Procesar una tarea a la vez
                    
                    except Exception as e:
                        logger.error(f"❌ Error en worker {worker_name} procesando cola {queue_key}: {e}")
                        continue
                
                # Gestión de sleep dinámico
                if not task_processed:
                    consecutive_empty_polls += 1
                    if consecutive_empty_polls < max_empty_polls:
                        await asyncio.sleep(0.1)  # Poll rápido si hay actividad reciente
                    else:
                        await asyncio.sleep(1.0)   # Sleep más largo si no hay tareas
                else:
                    await asyncio.sleep(0.01)  # Sleep mínimo entre tareas
                
            except Exception as e:
                logger.error(f"❌ Error crítico en worker {worker_name}: {e}")
                await asyncio.sleep(5)  # Sleep antes de reintentar
        
        logger.info(f"🛑 Worker {worker_name} detenido")

    async def _process_redis_task(self, task_data: str, worker_name: str, priority: TaskPriority):
        """Procesar una tarea obtenida de Redis"""
        start_time = time.time()
        task_dict = None
        
        try:
            # Deserializar tarea
            task_dict = json.loads(task_data)
            task_id = task_dict["id"]
            task_name = task_dict["name"]
            
            logger.debug(f"🔄 Worker {worker_name} procesando tarea {task_name} ({task_id})")
            
            # Obtener función desde el registro de funciones
            func = await self._resolve_function(task_dict["func_name"])
            if not func:
                raise Exception(f"Función no encontrada: {task_dict['func_name']}")
            
            # Aplicar circuit breaker
            circuit_breaker = self.circuit_breakers[task_dict["func_name"]]
            
            # Aplicar timeout si está especificado
            timeout = task_dict.get("timeout")
            
            # Ejecutar tarea
            if timeout:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        self.worker_pools.get(WorkerType(task_dict["worker_type"])),
                        circuit_breaker.call,
                        func,
                        *task_dict["args"],
                        **task_dict["kwargs"]
                    ),
                    timeout=timeout
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.worker_pools.get(WorkerType(task_dict["worker_type"])),
                    circuit_breaker.call,
                    func,
                    *task_dict["args"],
                    **task_dict["kwargs"]
                )
            
            processing_time = time.time() - start_time
            
            # Registrar tarea completada
            await self._record_task_completion(task_dict, result, processing_time, worker_name, "completed")
            
            logger.info(f"✅ Worker {worker_name} completó {task_name} ({task_id}) en {processing_time:.3f}s")
            
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            error_msg = f"Timeout después de {task_dict.get('timeout', 'N/A')}s"
            
            await self._record_task_completion(task_dict, None, processing_time, worker_name, "timeout", error_msg)
            await self._handle_failed_task(task_dict, error_msg)
            
            logger.warning(f"⏰ Worker {worker_name} timeout en tarea {task_dict.get('name', 'unknown')}")
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            await self._record_task_completion(task_dict, None, processing_time, worker_name, "failed", error_msg)
            await self._handle_failed_task(task_dict, error_msg)
            
            logger.error(f"❌ Worker {worker_name} error en tarea {task_dict.get('name', 'unknown')}: {e}")

    async def _resolve_function(self, func_name: str) -> Optional[Callable]:
        """Resolver nombre de función a función ejecutable"""
        # Cache de funciones resueltas
        if func_name in self.function_cache:
            return self.function_cache[func_name]
        
        try:
            # Parsear module.function
            if '.' in func_name:
                module_name, function_name = func_name.rsplit('.', 1)
                
                # Importar módulo dinámicamente
                import importlib
                module = importlib.import_module(module_name)
                func = getattr(module, function_name)
                
                # Cachear para próximas ejecuciones
                self.function_cache[func_name] = func
                return func
            else:
                # Función built-in o en scope global
                import builtins
                if hasattr(builtins, func_name):
                    func = getattr(builtins, func_name)
                    self.function_cache[func_name] = func
                    return func
        
        except Exception as e:
            logger.error(f"❌ No se pudo resolver función {func_name}: {e}")
            return None
        
        logger.warning(f"⚠️ Función no encontrada: {func_name}")
        return None

    async def _record_task_completion(self, task_dict: dict, result: Any, processing_time: float, 
                                    worker_name: str, status: str, error: str = None):
        """Registrar completación de tarea con métricas detalladas"""
        completion_record = {
            "task_id": task_dict["id"],
            "name": task_dict["name"],
            "worker_name": worker_name,
            "worker_type": task_dict["worker_type"],
            "priority": task_dict["priority"],
            "processing_time": processing_time,
            "status": status,
            "completed_at": datetime.now().isoformat(),
            "created_at": task_dict.get("created_at"),
        }
        
        if result is not None:
            completion_record["result"] = str(result)[:1000]  # Limitar tamaño del resultado
        
        if error:
            completion_record["error"] = error[:500]  # Limitar tamaño del error
        
        # Agregar a historial de tareas procesadas
        self.processed_tasks.append(completion_record)
        
        # Mantener solo las últimas 10000 tareas para evitar memory leak
        if len(self.processed_tasks) > 10000:
            self.processed_tasks = self.processed_tasks[-5000:]
        
        # Actualizar métricas globales
        if status == "completed":
            self.global_metrics["completed_tasks"] += 1
        elif status in ["failed", "timeout"]:
            self.global_metrics["failed_tasks"] += 1
        
        self.global_metrics["active_workers"] = len([t for t in self.worker_tasks if not t.done()])

    async def _handle_failed_task(self, task_dict: dict, error: str):
        """Manejar tarea fallida - reintento o dead letter queue"""
        current_retries = task_dict.get("current_retries", 0)
        max_retries = task_dict.get("max_retries", 3)
        
        if current_retries < max_retries:
            # Reintentar con backoff exponencial
            retry_delay = task_dict.get("retry_delay", 1.0) * (2 ** current_retries)
            task_dict["current_retries"] = current_retries + 1
            
            logger.info(f"🔄 Reintentando tarea {task_dict['name']} en {retry_delay}s (intento {current_retries + 1}/{max_retries})")
            
            # Programar reintento
            await asyncio.sleep(retry_delay)
            await self._requeue_task(task_dict)
        else:
            # Enviar a Dead Letter Queue
            await self._send_to_dlq(task_dict, error)

    async def _requeue_task(self, task_dict: dict):
        """Reencolar tarea para reintento"""
        try:
            # Seleccionar partición y cola
            task_id = task_dict["id"]
            partition = int(hashlib.md5(task_id.encode()).hexdigest(), 16) % self.partition_count
            priority = TaskPriority(task_dict["priority"])
            worker_type = WorkerType(task_dict["worker_type"])
            
            queue_key = self.queue_keys[(priority, worker_type, partition)]
            redis_client = self._select_redis_node(partition)
            
            if redis_client:
                # Re-serializar tarea actualizada
                task_data = json.dumps(task_dict)
                score = -time.time() + (priority.value * 1000000)  # Mantener orden de prioridad
                
                await redis_client.zadd(queue_key, {task_data: score})
                logger.debug(f"🔄 Tarea {task_dict['name']} reencolada para reintento")
            
        except Exception as e:
            logger.error(f"❌ Error reencolando tarea {task_dict.get('name', 'unknown')}: {e}")

    async def _send_to_dlq(self, task_dict: dict, error: str):
        """Enviar tarea fallida a Dead Letter Queue"""
        try:
            dlq_key = f"vokaflow:dlq:{task_dict['worker_type']}"
            redis_client = self._select_redis_node(0)  # Usar primer nodo para DLQ
            
            if redis_client:
                # Agregar información del error
                dlq_record = {
                    **task_dict,
                    "final_error": error,
                    "dlq_timestamp": datetime.now().isoformat(),
                    "total_retries": task_dict.get("current_retries", 0)
                }
                
                # Almacenar en DLQ con timestamp como score
                await redis_client.zadd(dlq_key, {
                    json.dumps(dlq_record): time.time()
                })
                
                logger.warning(f"💀 Tarea {task_dict['name']} enviada a DLQ después de {dlq_record['total_retries']} reintentos")
                
                # Mantener DLQ limpio (solo últimas 1000 tareas fallidas)
                await redis_client.zremrangebyrank(dlq_key, 0, -1001)
            
        except Exception as e:
            logger.error(f"❌ Error enviando tarea a DLQ: {e}")

    async def get_dlq_tasks(self, worker_type: str = None, limit: int = 100) -> List[dict]:
        """Obtener tareas de Dead Letter Queue"""
        try:
            if worker_type:
                dlq_keys = [f"vokaflow:dlq:{worker_type}"]
            else:
                dlq_keys = [f"vokaflow:dlq:{wt.value}" for wt in WorkerType]
            
            dlq_tasks = []
            redis_client = self._select_redis_node(0)
            
            if redis_client:
                for dlq_key in dlq_keys:
                    # Obtener tareas más recientes (mayor score = más reciente)
                    tasks = await redis_client.zrevrange(dlq_key, 0, limit-1, withscores=True)
                    
                    for task_data, timestamp in tasks:
                        try:
                            task_record = json.loads(task_data)
                            task_record["dlq_timestamp"] = timestamp
                            dlq_tasks.append(task_record)
                        except Exception as e:
                            logger.error(f"❌ Error deserializando tarea DLQ: {e}")
            
            return sorted(dlq_tasks, key=lambda x: x.get("dlq_timestamp", 0), reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo tareas DLQ: {e}")
            return []

    async def retry_dlq_task(self, task_id: str) -> bool:
        """Reintentar tarea desde Dead Letter Queue"""
        try:
            # Buscar tarea en todas las DLQs
            redis_client = self._select_redis_node(0)
            if not redis_client:
                return False
            
            for worker_type in WorkerType:
                dlq_key = f"vokaflow:dlq:{worker_type.value}"
                tasks = await redis_client.zrange(dlq_key, 0, -1, withscores=True)
                
                for task_data, score in tasks:
                    try:
                        task_record = json.loads(task_data)
                        if task_record["id"] == task_id:
                            # Remover de DLQ
                            await redis_client.zrem(dlq_key, task_data)
                            
                            # Resetear contadores y reencolar
                            task_record.pop("current_retries", None)
                            task_record.pop("final_error", None)
                            task_record.pop("dlq_timestamp", None)
                            
                            await self._requeue_task(task_record)
                            
                            logger.info(f"🔄 Tarea {task_id} reintentada desde DLQ")
                            return True
                    except Exception as e:
                        logger.error(f"❌ Error procesando tarea DLQ: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error reintentando tarea DLQ {task_id}: {e}")
            return False

    async def acquire_distributed_lock(self, lock_key: str, worker_id: str, timeout: int = 30) -> bool:
        """Adquirir lock distribuido usando Redis"""
        try:
            redis_client = self._select_redis_node(hash(lock_key) % len(self.redis_pools) if self.redis_pools else 0)
            if not redis_client:
                return False
            
            full_lock_key = f"vokaflow:lock:{lock_key}"
            expiration = time.time() + timeout
            
            # Intentar establecer lock atómicamente
            result = await redis_client.set(
                full_lock_key, 
                json.dumps({
                    "worker_id": worker_id,
                    "acquired_at": time.time(),
                    "expires_at": expiration
                }),
                ex=timeout,  # Expiración automática
                nx=True      # Solo si no existe
            )
            
            if result:
                logger.debug(f"🔒 Lock {lock_key} adquirido por worker {worker_id}")
                return True
            else:
                # Verificar si el lock expiró
                lock_data = await redis_client.get(full_lock_key)
                if lock_data:
                    try:
                        lock_info = json.loads(lock_data)
                        if time.time() > lock_info.get("expires_at", 0):
                            # Lock expirado, intentar tomarlo
                            await redis_client.delete(full_lock_key)
                            return await self.acquire_distributed_lock(lock_key, worker_id, timeout)
                    except Exception:
                        pass
                
                logger.debug(f"🔒 Lock {lock_key} no disponible para worker {worker_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error adquiriendo lock {lock_key}: {e}")
            return False

    async def release_distributed_lock(self, lock_key: str, worker_id: str) -> bool:
        """Liberar lock distribuido"""
        try:
            redis_client = self._select_redis_node(hash(lock_key) % len(self.redis_pools) if self.redis_pools else 0)
            if not redis_client:
                return False
            
            full_lock_key = f"vokaflow:lock:{lock_key}"
            
            # Script Lua para release atómico (solo si somos el owner)
            lua_script = """
            local lock_data = redis.call('GET', KEYS[1])
            if lock_data then
                local lock_info = cjson.decode(lock_data)
                if lock_info.worker_id == ARGV[1] then
                    return redis.call('DEL', KEYS[1])
                else
                    return 0
                end
            else
                return 0
            end
        """
            
            result = await redis_client.eval(lua_script, 1, full_lock_key, worker_id)
            
            if result:
                logger.debug(f"🔓 Lock {lock_key} liberado por worker {worker_id}")
                return True
            else:
                logger.warning(f"⚠️ Worker {worker_id} intentó liberar lock {lock_key} que no posee")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error liberando lock {lock_key}: {e}")
            return False

    async def execute_with_lock(self, lock_key: str, worker_id: str, func: Callable, 
                              *args, timeout: int = 30, **kwargs) -> Any:
        """Ejecutar función con lock distribuido"""
        lock_acquired = await self.acquire_distributed_lock(lock_key, worker_id, timeout)
        
        if not lock_acquired:
            raise Exception(f"No se pudo adquirir lock {lock_key} para worker {worker_id}")
        
        try:
            # Ejecutar función protegida
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            return result
            
        finally:
            # Siempre liberar el lock
            await self.release_distributed_lock(lock_key, worker_id)

    async def submit_task(self,
                         func: Callable,
                         args: tuple = (),
                         kwargs: Dict[str, Any] = None,
                         priority: TaskPriority = TaskPriority.NORMAL,
                         worker_type: WorkerType = WorkerType.GENERAL_PURPOSE,
                         name: str = None,
                         category: str = "general",
                         rate_limit: Optional[int] = None,
                         **task_options) -> str:
        """
        Enviar tarea optimizada para alta escala
        """
        # Rate limiting por categoría
        if not self.rate_limiters[category].is_allowed():
            raise Exception(f"Rate limit exceeded for category: {category}")
        
        # Generar ID único
        task_id = str(uuid.uuid4())
        
        if name is None:
            name = f"{func.__name__}_{task_id[:8]}"
        
        # Crear tarea escalable
        task = ScalableTask(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            worker_type=worker_type,
            category=category,
            rate_limit=rate_limit,
            created_at=datetime.now(),
            **task_options
        )
        
        # Determinar partición basada en el task_id para distribución uniforme
        partition = int(hashlib.md5(task_id.encode()).hexdigest(), 16) % self.partition_count
        
        # Seleccionar nodo Redis
        redis_client = self._select_redis_node(partition)
        
        # Serializar tarea
        task_data = self._serialize_task(task)
        
        # Encolar en Redis con prioridad (si está disponible)
        if redis_client:
            queue_key = self.queue_keys[(priority, worker_type, partition)]
            
            # Usar timestamp negativo para ordenación por prioridad (menor = mayor prioridad)
            score = -time.time() + (priority.value * 1000000)
            
            try:
                await redis_client.zadd(queue_key, {task_data: score})
                # Notificar a workers
                await redis_client.publish(f"vokaflow:notify:{worker_type.value}", task_id)
            except Exception as e:
                logger.warning(f"Redis no disponible, usando cola en memoria: {e}")
                # Fallback a cola en memoria
                if not hasattr(self, 'memory_queues'):
                    self.memory_queues = defaultdict(list)
                self.memory_queues[queue_key].append((score, task_data))
        else:
            # Fallback: usar cola en memoria
            if not hasattr(self, 'memory_queues'):
                self.memory_queues = defaultdict(list)
            queue_key = f"memory:{priority.name}:{worker_type.value}:{partition}"
            score = -time.time() + (priority.value * 1000000)
            self.memory_queues[queue_key].append((score, task_data))
        
        # Actualizar métricas
        self.global_metrics["total_tasks"] += 1
        queue_key = queue_key if 'queue_key' in locals() else f"memory:{priority.name}:{worker_type.value}:{partition}"
        self.global_metrics["queue_lengths"][queue_key] += 1
        
        logger.debug(f"📋 Tarea enviada: {name} ({task_id}) - Prioridad: {priority.name}, Partición: {partition}")
        
        # Si estamos usando memoria, procesar la tarea inmediatamente (modo demostración)
        if not redis_client:
            asyncio.create_task(self._process_memory_task(task_id, task))
        
        return task_id

    async def _process_memory_task(self, task_id: str, task: ScalableTask):
        """Procesar tarea en memoria (modo demostración sin Redis)"""
        try:
            start_time = time.time()
            
            # Simular procesamiento de la tarea
            result = await asyncio.get_event_loop().run_in_executor(
                self.worker_pools.get(task.worker_type, self.worker_pools[WorkerType.GENERAL_PURPOSE]),
                task.func,
                *task.args,
                **task.kwargs
            )
            
            processing_time = time.time() - start_time
            
            # Registrar tarea completada
            self.processed_tasks.append({
                "task_id": task_id,
                "name": task.name,
                "result": str(result),
                "processing_time": processing_time,
                "priority": task.priority.name,
                "worker_type": task.worker_type.value,
                "completed_at": datetime.now().isoformat(),
                "status": "completed"
            })
            
            # Actualizar métricas
            self.global_metrics["completed_tasks"] += 1
            self.global_metrics["active_workers"] += 1
            
            logger.info(f"✅ Tarea completada: {task.name} ({task_id}) en {processing_time:.3f}s")
            
        except Exception as e:
            # Registrar error
            self.processed_tasks.append({
                "task_id": task_id,
                "name": task.name,
                "error": str(e),
                "priority": task.priority.name,
                "worker_type": task.worker_type.value,
                "completed_at": datetime.now().isoformat(),
                "status": "failed"
            })
            
            self.global_metrics["failed_tasks"] += 1
            logger.error(f"❌ Error procesando tarea {task.name} ({task_id}): {e}")

    def _select_redis_node(self, partition: int) -> 'aioredis.Redis':
        """Seleccionar nodo Redis basado en partición"""
        if not self.redis_pools:
            # Si no hay pools Redis disponibles, usar el primer nodo por defecto
            return None
        node_index = partition % len(self.redis_pools)
        node_key = f"node_{node_index}"
        return self.redis_pools.get(node_key)

    def _serialize_task(self, task: ScalableTask) -> str:
        """Serializar tarea para Redis"""
        # Convertir función a string para serialización
        func_name = f"{task.func.__module__}.{task.func.__name__}"
        
        task_dict = {
            "id": task.id,
            "name": task.name,
            "func_name": func_name,
            "args": task.args,
            "kwargs": task.kwargs,
            "priority": task.priority.value,
            "worker_type": task.worker_type.value,
            "max_retries": task.max_retries,
            "timeout": task.timeout,
            "category": task.category,
            "created_at": task.created_at.isoformat()
        }
        
        return json.dumps(task_dict)

    async def _monitoring_loop(self):
        """Loop de monitoreo en tiempo real"""
        while self.running:
            try:
                # Calcular métricas de throughput
                current_time = time.time()
                
                # Obtener longitudes de colas
                total_queue_length = 0
                
                # Solo intentar obtener métricas de Redis si hay conexiones disponibles
                if self.redis_pools:
                    for queue_key in self.queue_keys.values():
                        redis_client = self._select_redis_node(0)  # Usar primer nodo para métricas
                        if redis_client:  # Verificar que redis_client no sea None
                            try:
                                length = await redis_client.zcard(queue_key)
                                total_queue_length += length
                            except Exception as redis_error:
                                rate_limited_log(f"⚠️ Error al obtener métricas de Redis para {queue_key}: {redis_error}", "warning")
                else:
                    # Modo memoria: contar tareas en memory_queues
                    total_queue_length = sum(len(queue) for queue in self.memory_queues.values())
                
                # Actualizar métricas globales
                self.global_metrics["total_queue_length"] = total_queue_length
                self.global_metrics["timestamp"] = current_time
                
                # Log métricas cada 10 segundos
                if int(current_time) % 10 == 0:
                    mode = "Redis" if self.redis_pools else "Memory"
                    logger.info(f"📊 Métricas ({mode}): {self.global_metrics['throughput_per_second']:.0f} tasks/s, "
                              f"Cola: {total_queue_length}, Workers: {self.global_metrics['active_workers']}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                rate_limited_log(f"❌ Error en monitoreo: {e}", "error")
                await asyncio.sleep(5)

    async def _auto_scaling_loop(self):
        """Loop de auto-scaling de workers"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Evaluar cada 30 segundos
                
                # Obtener métricas de sistema
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                # Auto-scaling basado en carga
                for worker_type, pool in self.worker_pools.items():
                    queue_length = sum(
                        self.global_metrics["queue_lengths"].get(
                            self.queue_keys.get((priority, worker_type, partition), ""), 0
                        )
                        for priority in TaskPriority
                        for partition in range(self.partition_count)
                    )
                    
                    # Decidir si escalar hacia arriba o hacia abajo
                    if queue_length > 1000 and cpu_percent < 80:
                        await self._scale_up_workers(worker_type)
                    elif queue_length < 100 and cpu_percent < 30:
                        await self._scale_down_workers(worker_type)
                
            except Exception as e:
                logger.error(f"❌ Error en auto-scaling: {e}")

    async def _scale_up_workers(self, worker_type: WorkerType):
        """Escalar hacia arriba el número de workers"""
        current_max = self.max_workers_per_type[worker_type]
        new_max = min(current_max * 2, multiprocessing.cpu_count() * 4)
        
        if new_max > current_max:
            logger.info(f"📈 Escalando {worker_type.value} de {current_max} a {new_max} workers")
            # Aquí implementaríamos la lógica real de escalamiento
            self.max_workers_per_type[worker_type] = new_max

    async def _scale_down_workers(self, worker_type: WorkerType):
        """Escalar hacia abajo el número de workers"""
        current_max = self.max_workers_per_type[worker_type]
        new_max = max(current_max // 2, 1)
        
        if new_max < current_max:
            logger.info(f"📉 Reduciendo {worker_type.value} de {current_max} a {new_max} workers")
            self.max_workers_per_type[worker_type] = new_max

    async def get_global_metrics(self) -> Dict[str, Any]:
        """Obtener métricas globales del sistema"""
        # Calcular throughput
        current_time = time.time()
        time_window = 60  # 1 minuto
        
        # Obtener estadísticas de todas las colas
        total_pending = 0
        if self.redis_pools and self.queue_keys:
            for queue_key in self.queue_keys.values():
                redis_client = self._select_redis_node(0)
                if redis_client:
                    try:
                        pending = await redis_client.zcard(queue_key)
                        total_pending += pending
                    except Exception as redis_error:
                        # Si Redis no está disponible, continuar sin error
                        rate_limited_log(f"⚠️ Error al obtener estadísticas de Redis para {queue_key}: {redis_error}", "warning")
                        pass
        
        # Agregar información sobre tareas en memoria
        memory_queue_lengths = {k: len(v) for k, v in self.memory_queues.items()}
        completed_tasks_count = len([t for t in self.processed_tasks if t["status"] == "completed"])
        failed_tasks_count = len([t for t in self.processed_tasks if t["status"] == "failed"])
        
        metrics = {
            **self.global_metrics,
            "total_pending_tasks": total_pending + sum(memory_queue_lengths.values()),
            "redis_nodes": len(self.redis_pools),
            "partitions": self.partition_count,
            "worker_pools": {
                worker_type.value: {
                    "max_workers": max_workers,
                    "pool_type": "ProcessPool" if worker_type == WorkerType.CPU_INTENSIVE else "ThreadPool"
                }
                for worker_type, max_workers in self.max_workers_per_type.items()
            },
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "memory_mode": {
                "enabled": len(self.redis_pools) == 0,
                "processed_tasks": len(self.processed_tasks),
                "completed_tasks": completed_tasks_count,
                "failed_tasks": failed_tasks_count,
                "memory_queue_lengths": memory_queue_lengths
            },
            "recent_tasks": self.processed_tasks[-5:] if self.processed_tasks else [],
            "timestamp": current_time
        }
        
        return metrics

    async def shutdown(self):
        """Shutdown graceful del sistema"""
        logger.info("🛑 Iniciando shutdown del HighScaleTaskManager...")
        
        self.running = False
        
        # Cancelar tareas de monitoreo
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.auto_scaler_task:
            self.auto_scaler_task.cancel()
        
        # Cancelar workers Redis
        if hasattr(self, 'worker_tasks'):
            for task in self.worker_tasks:
                task.cancel()
            
            # Esperar a que terminen gracefully
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Cerrar worker pools
        for worker_type, pool in self.worker_pools.items():
            logger.info(f"🔄 Cerrando pool {worker_type.value}")
            pool.shutdown(wait=True)
        
        # Cerrar conexiones Redis
        for node_name, redis_client in self.redis_pools.items():
            await redis_client.close()
        
        logger.info("✅ HighScaleTaskManager shutdown completado")

# Instancia global - REACTIVADA con configuración optimizada
high_scale_task_manager = None

def create_optimized_high_scale_manager():
    """Crear high scale manager con configuración optimizada para Redis single-node"""
    # Configuración optimizada para evitar sobrecarga
    cpu_count = multiprocessing.cpu_count()
    optimized_workers = {
        WorkerType.CPU_INTENSIVE: max(1, cpu_count // 4),  # Más conservador
        WorkerType.IO_INTENSIVE: max(2, cpu_count // 2),   # Reducido
        WorkerType.MEMORY_INTENSIVE: max(1, cpu_count // 8),
        WorkerType.NETWORK_INTENSIVE: max(2, cpu_count // 2),  # Reducido
        WorkerType.GENERAL_PURPOSE: max(2, cpu_count // 4)
    }
    
    logger.info(f"🚀 Configuración optimizada: {sum(optimized_workers.values())} workers totales")
    
    # Configuración para Redis single-node
    redis_nodes = ["redis://localhost:6379"]  # Single Redis instance
    
    return HighScaleTaskManager(
        redis_cluster_nodes=redis_nodes,
        max_workers_per_type=optimized_workers,
        enable_auto_scaling=False,  # Deshabilitado para evitar sobrecarga
        enable_monitoring=True,
        partition_count=4  # Reducido para single-node
    )

# Funciones de conveniencia para alta escala
async def submit_high_scale_task(*args, **kwargs) -> str:
    """Enviar tarea de alta escala"""
    global high_scale_task_manager
    if high_scale_task_manager is None:
        high_scale_task_manager = create_optimized_high_scale_manager()
        await high_scale_task_manager.initialize()
    return await high_scale_task_manager.submit_task(*args, **kwargs)

async def get_scale_metrics() -> Dict[str, Any]:
    """Obtener métricas de alta escala"""
    if high_scale_task_manager is None:
        return {"status": "not_initialized", "message": "High scale task manager is not initialized"}
    return await high_scale_task_manager.get_global_metrics()

async def initialize_high_scale_system():
    """Inicializar sistema de alta escala con configuración optimizada"""
    global high_scale_task_manager
    if high_scale_task_manager is None:
        high_scale_task_manager = create_optimized_high_scale_manager()
        await high_scale_task_manager.initialize()
        logger.info("🚀 Sistema de alta escala inicializado correctamente")

async def shutdown_high_scale_system():
    """Shutdown sistema de alta escala"""
    global high_scale_task_manager
    if high_scale_task_manager is not None:
        try:
            await high_scale_task_manager.shutdown() 
            high_scale_task_manager = None
            logger.info("🛑 Sistema de alta escala apagado correctamente")
        except Exception as e:
            logger.error(f"❌ Error durante shutdown de high scale system: {e}")
            high_scale_task_manager = None
    else:
        # Evitar log spam - solo logear una vez cuando ya está apagado
        pass 