"""
Utilidades para Métricas de Rendimiento
--------------------------------------

Este módulo proporciona decoradores y funciones para medir y registrar
el rendimiento de funciones y componentes del sistema.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import time
import logging
import functools
import traceback
import gc
import os
import psutil
from typing import Callable, Any, Dict, Optional

# Configurar logger
logger = logging.getLogger("vicky.performance")

def measure_execution_time(func: Callable) -> Callable:
    """
    Decorador que mide y registra el tiempo de ejecución de una función.
    
    Args:
        func: Función a medir
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Registrar tiempo de ejecución
            logger.debug(f"Función {func.__name__} ejecutada en {execution_time:.4f} segundos")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error en función {func.__name__} después de {execution_time:.4f} segundos: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    return wrapper

def log_memory_usage(func: Callable) -> Callable:
    """
    Decorador que registra el uso de memoria antes y después de una función.
    
    Args:
        func: Función a monitorear
        
    Returns:
        Función decorada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Forzar recolección de basura antes de medir
        gc.collect()
        
        # Medir memoria antes
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            
            # Forzar recolección de basura antes de medir nuevamente
            gc.collect()
            
            # Medir memoria después
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = memory_after - memory_before
            
            # Registrar uso de memoria
            logger.debug(f"Función {func.__name__}: Memoria antes={memory_before:.2f}MB, "
                        f"después={memory_after:.2f}MB, diferencia={memory_diff:.2f}MB")
            
            return result
        except Exception as e:
            logger.error(f"Error en función {func.__name__}: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    return wrapper

class PerformanceTracker:
    """
    Clase para realizar seguimiento del rendimiento de componentes del sistema.
    """
    
    def __init__(self, component_name: str):
        """
        Inicializa el tracker de rendimiento.
        
        Args:
            component_name: Nombre del componente a monitorear
        """
        self.component_name = component_name
        self.metrics = {
            "calls": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "errors": 0
        }
        self.logger = logging.getLogger(f"vicky.performance.{component_name}")
    
    def track(self, operation_name: Optional[str] = None) -> Callable:
        """
        Decorador para realizar seguimiento de una operación.
        
        Args:
            operation_name: Nombre de la operación (opcional)
            
        Returns:
            Decorador para la función
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Actualizar métricas
                    self._update_metrics(op_name, execution_time, success=True)
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    # Actualizar métricas con error
                    self._update_metrics(op_name, execution_time, success=False)
                    
                    self.logger.error(f"Error en {op_name}: {e}")
                    self.logger.debug(traceback.format_exc())
                    raise
            
            return wrapper
        
        return decorator
    
    def _update_metrics(self, operation: str, execution_time: float, success: bool) -> None:
        """
        Actualiza las métricas de rendimiento.
        
        Args:
            operation: Nombre de la operación
            execution_time: Tiempo de ejecución
            success: Si la operación fue exitosa
        """
        # Actualizar métricas generales
        self.metrics["calls"] += 1
        self.metrics["total_time"] += execution_time
        self.metrics["avg_time"] = self.metrics["total_time"] / self.metrics["calls"]
        self.metrics["min_time"] = min(self.metrics["min_time"], execution_time)
        self.metrics["max_time"] = max(self.metrics["max_time"], execution_time)
        
        if not success:
            self.metrics["errors"] += 1
        
        # Registrar métricas
        self.logger.debug(f"Operación {operation}: tiempo={execution_time:.4f}s, "
                         f"promedio={self.metrics['avg_time']:.4f}s, "
                         f"éxito={success}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene las métricas actuales.
        
        Returns:
            Diccionario con métricas
        """
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reinicia las métricas de rendimiento."""
        self.metrics = {
            "calls": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "errors": 0
        }
        self.logger.info(f"Métricas del componente {self.component_name} reiniciadas")

# Función de utilidad global
def track_performance(component_name: str, operation_name: Optional[str] = None) -> Callable:
    """
    Función de utilidad global para realizar seguimiento de rendimiento.
    
    Args:
        component_name: Nombre del componente
        operation_name: Nombre de la operación (opcional)
        
    Returns:
        Decorador para la función
    """
    tracker = PerformanceTracker(component_name)
    return tracker.track(operation_name)
