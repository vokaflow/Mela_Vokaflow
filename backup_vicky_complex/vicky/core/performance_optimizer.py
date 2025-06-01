"""
Optimizador de Rendimiento para VokaFlow
---------------------------------------

Este módulo implementa un sistema de optimización de rendimiento
que monitorea y ajusta automáticamente los parámetros del sistema
para maximizar la eficiencia y minimizar la latencia.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
import traceback
import json
import os
import psutil
import numpy as np
from dataclasses import dataclass, field

# Importaciones internas
from .dual_brain import DualBrain
from .cache_integration import DualBrainCacheManager
from .selective_cache import SelectiveCache, AdaptivePolicy
from .memory import Memory
from .state import State

# Configurar logger
logger = logging.getLogger("vicky.performance_optimizer")

@dataclass
class SystemResources:
    """Información sobre recursos del sistema."""
    cpu_count: int
    cpu_usage: float  # 0.0 a 1.0
    memory_total: int  # bytes
    memory_available: int  # bytes
    memory_usage: float  # 0.0 a 1.0
    disk_total: int  # bytes
    disk_available: int  # bytes
    disk_usage: float  # 0.0 a 1.0
    
    @classmethod
    def get_current(cls) -> 'SystemResources':
        """
        Obtiene información actual de recursos del sistema.
        
        Returns:
            Instancia con información de recursos
        """
        try:
            # CPU
            cpu_count = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=0.1) / 100.0
            
            # Memoria
            memory = psutil.virtual_memory()
            memory_total = memory.total
            memory_available = memory.available
            memory_usage = memory.percent / 100.0
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_total = disk.total
            disk_available = disk.free
            disk_usage = disk.percent / 100.0
            
            return cls(
                cpu_count=cpu_count,
                cpu_usage=cpu_usage,
                memory_total=memory_total,
                memory_available=memory_available,
                memory_usage=memory_usage,
                disk_total=disk_total,
                disk_available=disk_available,
                disk_usage=disk_usage
            )
        except Exception as e:
            logger.error(f"Error al obtener recursos del sistema: {e}")
            # Valores por defecto
            return cls(
                cpu_count=1,
                cpu_usage=0.5,
                memory_total=1,
                memory_available=1,
                memory_usage=0.5,
                disk_total=1,
                disk_available=1,
                disk_usage=0.5
            )


@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento del sistema."""
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    requests_per_second: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage: int = 0  # bytes
    error_rate: float = 0.0
    uptime: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    
    def update_percentiles(self) -> None:
        """Actualiza percentiles de tiempo de respuesta."""
        if self.response_times:
            self.p95_response_time = np.percentile(self.response_times, 95)
            self.p99_response_time = np.percentile(self.response_times, 99)
    
    def add_response_time(self, time: float) -> None:
        """
        Añade un tiempo de respuesta a las métricas.
        
        Args:
            time: Tiempo de respuesta en segundos
        """
        self.response_times.append(time)
        # Limitar tamaño del historial
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Actualizar promedio
        self.avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Actualizar percentiles
        self.update_percentiles()


class PerformanceOptimizer:
    """
    Optimizador de rendimiento para el sistema VokaFlow.
    
    Esta clase implementa:
    1. Monitoreo continuo de rendimiento
    2. Ajuste automático de parámetros
    3. Balanceo de recursos
    4. Optimización de caché
    5. Recomendaciones de configuración
    """
    
    def __init__(self, dual_brain: DualBrain, cache_manager: DualBrainCacheManager, 
                memory: Memory, state: State):
        """
        Inicializa el optimizador de rendimiento.
        
        Args:
            dual_brain: Instancia del Motor Dual-Hemisferio
            cache_manager: Gestor de caché
            memory: Sistema de memoria
            state: Sistema de estado
        """
        self.dual_brain = dual_brain
        self.cache_manager = cache_manager
        self.memory = memory
        self.state = state
        
        # Métricas de rendimiento
        self.metrics = PerformanceMetrics()
        self.metrics.uptime = time.time()
        
        # Configuración
        self.config = {
            "monitoring_interval": 60,  # segundos
            "optimization_interval": 300,  # segundos
            "auto_optimization": True,
            "memory_threshold": 0.8,  # 80% de uso de memoria
            "cpu_threshold": 0.9,  # 90% de uso de CPU
            "response_time_threshold": 2.0,  # segundos
            "cache_size_adjustment_factor": 0.2,  # 20% de ajuste
            "hemisphere_balance_adjustment_factor": 0.1  # 10% de ajuste
        }
        
        # Estado de optimización
        self.last_monitoring_time = 0.0
        self.last_optimization_time = 0.0
        self.optimization_history = []
        self.monitoring_active = False
        self.optimization_active = False
        
        # Iniciar monitoreo si está configurado
        if self.config["auto_optimization"]:
            self.start_monitoring()
        
        logger.info("Optimizador de rendimiento inicializado")
    
    def start_monitoring(self) -> bool:
        """
        Inicia el monitoreo continuo de rendimiento.
        
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        if self.monitoring_active:
            logger.warning("El monitoreo ya está activo")
            return False
        
        try:
            # Iniciar thread de monitoreo
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_active = True
            self.monitoring_thread.start()
            
            logger.info("Monitoreo de rendimiento iniciado")
            return True
        except Exception as e:
            logger.error(f"Error al iniciar monitoreo: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Detiene el monitoreo de rendimiento.
        
        Returns:
            True si se detuvo correctamente, False en caso contrario
        """
        if not self.monitoring_active:
            logger.warning("El monitoreo no está activo")
            return False
        
        try:
            self.monitoring_active = False
            logger.info("Monitoreo de rendimiento detenido")
            return True
        except Exception as e:
            logger.error(f"Error al detener monitoreo: {e}")
            return False
    
    def _monitoring_loop(self) -> None:
        """Loop principal de monitoreo."""
        while self.monitoring_active:
            try:
                # Ejecutar monitoreo
                self._monitor_performance()
                
                # Ejecutar optimización si corresponde
                current_time = time.time()
                if (current_time - self.last_optimization_time >= self.config["optimization_interval"] and
                    self.config["auto_optimization"]):
                    self._optimize_performance()
                    self.last_optimization_time = current_time
                
                # Esperar hasta el próximo ciclo
                time.sleep(self.config["monitoring_interval"])
            except Exception as e:
                logger.error(f"Error en ciclo de monitoreo: {e}")
                time.sleep(10)  # Esperar un poco más en caso de error
    
    def _monitor_performance(self) -> Dict[str, Any]:
        """
        Monitorea el rendimiento actual del sistema.
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        try:
            # Obtener recursos del sistema
            system_resources = SystemResources.get_current()
            
            # Obtener métricas de caché
            cache_metrics = self.cache_manager.get_metrics()
            
            # Actualizar métricas
            self.metrics.cache_hit_rate = cache_metrics["response_cache"]["hit_rate"]
            self.metrics.memory_usage = cache_metrics["total_memory_usage"]
            
            # Obtener estadísticas de DualBrain
            dual_brain_stats = self.dual_brain.get_processing_stats()
            
            # Actualizar métricas de solicitudes
            self.metrics.total_requests = self.state.get("total_messages_processed", 0)
            self.metrics.successful_requests = self.state.get("successful_messages", 0)
            self.metrics.failed_requests = self.state.get("failed_messages", 0)
            
            # Calcular tasa de error
            if self.metrics.total_requests > 0:
                self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests
            
            # Calcular solicitudes por segundo
            uptime_seconds = time.time() - self.metrics.uptime
            if uptime_seconds > 0:
                self.metrics.requests_per_second = self.metrics.total_requests / uptime_seconds
            
            # Guardar métricas en memoria
            self.memory.store("performance_metrics", {
                "avg_response_time": self.metrics.avg_response_time,
                "p95_response_time": self.metrics.p95_response_time,
                "p99_response_time": self.metrics.p99_response_time,
                "requests_per_second": self.metrics.requests_per_second,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "error_rate": self.metrics.error_rate,
                "total_requests": self.metrics.total_requests,
                "timestamp": time.time()
            })
            
            # Actualizar tiempo de último monitoreo
            self.last_monitoring_time = time.time()
            
            # Devolver métricas actuales
            return {
                "system_resources": {
                    "cpu_usage": system_resources.cpu_usage,
                    "memory_usage": system_resources.memory_usage,
                    "disk_usage": system_resources.disk_usage
                },
                "performance_metrics": {
                    "avg_response_time": self.metrics.avg_response_time,
                    "p95_response_time": self.metrics.p95_response_time,
                    "requests_per_second": self.metrics.requests_per_second,
                    "cache_hit_rate": self.metrics.cache_hit_rate,
                    "error_rate": self.metrics.error_rate,
                    "total_requests": self.metrics.total_requests
                },
                "cache_metrics": {
                    "response_cache_size": cache_metrics["response_cache"]["size"],
                    "response_cache_hit_rate": cache_metrics["response_cache"]["hit_rate"],
                    "hemisphere_cache_size": cache_metrics["hemisphere_cache"]["size"],
                    "hemisphere_cache_hit_rate": cache_metrics["hemisphere_cache"]["hit_rate"],
                    "intent_cache_size": cache_metrics["intent_cache"]["size"],
                    "intent_cache_hit_rate": cache_metrics["intent_cache"]["hit_rate"]
                },
                "dual_brain_metrics": {
                    "technical_avg_time": dual_brain_stats["average_times"]["technical"],
                    "emotional_avg_time": dual_brain_stats["average_times"]["emotional"],
                    "total_avg_time": dual_brain_stats["average_times"]["total"],
                    "processed_messages": dual_brain_stats["processed_messages"]
                }
            }
        except Exception as e:
            logger.error(f"Error al monitorear rendimiento: {e}")
            logger.debug(traceback.format_exc())
            return {}
    
    def _optimize_performance(self) -> Dict[str, Any]:
        """
        Optimiza automáticamente el rendimiento del sistema.
        
        Returns:
            Diccionario con cambios realizados
        """
        if self.optimization_active:
            logger.warning("Ya hay una optimización en curso")
            return {}
        
        self.optimization_active = True
        changes = {}
        
        try:
            # Obtener métricas actuales
            metrics = self._monitor_performance()
            
            # Optimizar caché
            cache_changes = self._optimize_cache(metrics)
            changes["cache"] = cache_changes
            
            # Optimizar balance de hemisferios
            hemisphere_changes = self._optimize_hemisphere_balance(metrics)
            changes["hemisphere_balance"] = hemisphere_changes
            
            # Optimizar estrategias de combinación
            strategy_changes = self._optimize_combination_strategy(metrics)
            changes["combination_strategy"] = strategy_changes
            
            # Guardar historial de optimización
            self.optimization_history.append({
                "timestamp": time.time(),
                "metrics_before": metrics,
                "changes": changes
            })
            
            # Limitar tamaño del historial
            if len(self.optimization_history) > 50:
                self.optimization_history = self.optimization_history[-50:]
            
            # Guardar en memoria
            self.memory.store("optimization_history", self.optimization_history, permanent=True)
            
            logger.info(f"Optimización completada: {len(changes)} cambios realizados")
            return changes
        except Exception as e:
            logger.error(f"Error en optimización de rendimiento: {e}")
            logger.debug(traceback.format_exc())
            return {"error": str(e)}
        finally:
            self.optimization_active = False
    
    def _optimize_cache(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza la configuración de caché.
        
        Args:
            metrics: Métricas actuales de rendimiento
            
        Returns:
            Diccionario con cambios realizados
        """
        changes = {}
        
        try:
            # Obtener recursos del sistema
            system_resources = SystemResources.get_current()
            
            # Ajustar tamaño de caché según uso de memoria
            if system_resources.memory_usage > self.config["memory_threshold"]:
                # Reducir tamaño de caché
                current_sizes = {
                    "response_cache_size": self.cache_manager.response_cache.max_size,
                    "hemisphere_cache_size": self.cache_manager.hemisphere_cache.max_size,
                    "intent_cache_size": self.cache_manager.intent_cache.max_size
                }
                
                # Reducir proporcionalmente
                reduction_factor = 1.0 - self.config["cache_size_adjustment_factor"]
                new_sizes = {
                    "response_cache_size": int(current_sizes["response_cache_size"] * reduction_factor),
                    "hemisphere_cache_size": int(current_sizes["hemisphere_cache_size"] * reduction_factor),
                    "intent_cache_size": int(current_sizes["intent_cache_size"] * reduction_factor)
                }
                
                # Aplicar cambios
                self.cache_manager.update_configuration(new_sizes)
                
                changes["cache_sizes"] = {
                    "before": current_sizes,
                    "after": new_sizes,
                    "action": "reduced",
                    "reason": "high_memory_usage"
                }
            elif system_resources.memory_usage < 0.5 and metrics["performance_metrics"]["cache_hit_rate"] < 0.7:
                # Aumentar tamaño de caché
                current_sizes = {
                    "response_cache_size": self.cache_manager.response_cache.max_size,
                    "hemisphere_cache_size": self.cache_manager.hemisphere_cache.max_size,
                    "intent_cache_size": self.cache_manager.intent_cache.max_size
                }
                
                # Aumentar proporcionalmente
                increase_factor = 1.0 + self.config["cache_size_adjustment_factor"]
                new_sizes = {
                    "response_cache_size": int(current_sizes["response_cache_size"] * increase_factor),
                    "hemisphere_cache_size": int(current_sizes["hemisphere_cache_size"] * increase_factor),
                    "intent_cache_size": int(current_sizes["intent_cache_size"] * increase_factor)
                }
                
                # Aplicar cambios
                self.cache_manager.update_configuration(new_sizes)
                
                changes["cache_sizes"] = {
                    "before": current_sizes,
                    "after": new_sizes,
                    "action": "increased",
                    "reason": "low_hit_rate"
                }
            
            # Ajustar estrategias de caché según patrones de uso
            cache_metrics = self.cache_manager.get_metrics()
            
            # Si hay muchos fallos de caché, ajustar configuración
            if cache_metrics["response_cache"]["hit_rate"] < 0.3:
                # Habilitar/deshabilitar cachés según rendimiento
                current_config = {
                    "enable_response_cache": self.cache_manager.enable_response_cache,
                    "enable_hemisphere_cache": self.cache_manager.enable_hemisphere_cache,
                    "enable_intent_cache": self.cache_manager.enable_intent_cache
                }
                
                # Analizar qué cachés están funcionando mejor
                new_config = current_config.copy()
                
                # Si el caché de respuestas tiene muy baja tasa de aciertos, ajustar
                if cache_metrics["response_cache"]["hit_rate"] < 0.2:
                    # Mantener habilitado pero ajustar TTL
                    self.cache_manager.response_cache.default_ttl = 1800  # 30 minutos
                    changes["response_cache_ttl"] = {
                        "before": 3600,
                        "after": 1800,
                        "action": "reduced",
                        "reason": "low_hit_rate"
                    }
                
                # Aplicar cambios si hay
                if new_config != current_config:
                    self.cache_manager.update_configuration(new_config)
                    changes["cache_config"] = {
                        "before": current_config,
                        "after": new_config,
                        "action": "adjusted",
                        "reason": "optimize_hit_rate"
                    }
            
            return changes
        except Exception as e:
            logger.error(f"Error al optimizar caché: {e}")
            return {"error": str(e)}
    
    def _optimize_hemisphere_balance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza el balance entre hemisferios.
        
        Args:
            metrics: Métricas actuales de rendimiento
            
        Returns:
            Diccionario con cambios realizados
        """
        changes = {}
        
        try:
            # Obtener balance actual
            current_weights = {
                "technical": self.dual_brain.default_weights.get("technical", 0.5),
                "emotional": self.dual_brain.default_weights.get("emotional", 0.5)
            }
            
            # Obtener tiempos de procesamiento por hemisferio
            technical_time = metrics["dual_brain_metrics"]["technical_avg_time"]
            emotional_time = metrics["dual_brain_metrics"]["emotional_avg_time"]
            
            # Si hay una diferencia significativa en tiempos, ajustar balance
            if technical_time > 0 and emotional_time > 0:
                time_ratio = technical_time / emotional_time
                
                # Si el hemisferio técnico es mucho más lento
                if time_ratio > 1.5:
                    # Reducir peso del hemisferio técnico
                    adjustment = self.config["hemisphere_balance_adjustment_factor"]
                    new_technical = max(0.2, current_weights["technical"] - adjustment)
                    new_emotional = 1.0 - new_technical
                    
                    # Aplicar cambios
                    self.dual_brain.set_hemisphere_weights({
                        "technical": new_technical,
                        "emotional": new_emotional
                    })
                    
                    changes["weights"] = {
                        "before": current_weights,
                        "after": {
                            "technical": new_technical,
                            "emotional": new_emotional
                        },
                        "action": "reduced_technical",
                        "reason": "technical_hemisphere_slower"
                    }
                
                # Si el hemisferio emocional es mucho más lento
                elif time_ratio < 0.67:
                    # Reducir peso del hemisferio emocional
                    adjustment = self.config["hemisphere_balance_adjustment_factor"]
                    new_emotional = max(0.2, current_weights["emotional"] - adjustment)
                    new_technical = 1.0 - new_emotional
                    
                    # Aplicar cambios
                    self.dual_brain.set_hemisphere_weights({
                        "technical": new_technical,
                        "emotional": new_emotional
                    })
                    
                    changes["weights"] = {
                        "before": current_weights,
                        "after": {
                            "technical": new_technical,
                            "emotional": new_emotional
                        },
                        "action": "reduced_emotional",
                        "reason": "emotional_hemisphere_slower"
                    }
            
            return changes
        except Exception as e:
            logger.error(f"Error al optimizar balance de hemisferios: {e}")
            return {"error": str(e)}
    
    def _optimize_combination_strategy(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza la estrategia de combinación de respuestas.
        
        Args:
            metrics: Métricas actuales de rendimiento
            
        Returns:
            Diccionario con cambios realizados
        """
        changes = {}
        
        try:
            # Obtener estrategia actual
            current_strategy = self.dual_brain.default_combination_strategy
            
            # Obtener tiempos de respuesta
            avg_response_time = metrics["performance_metrics"]["avg_response_time"]
            p95_response_time = metrics["performance_metrics"]["p95_response_time"]
            
            # Si los tiempos de respuesta son altos, usar estrategia más simple
            if p95_response_time > self.config["response_time_threshold"]:
                if current_strategy == "integrated":
                    # Cambiar a estrategia más simple
                    new_strategy = "selective"
                    self.dual_brain.set_combination_strategy(new_strategy)
                    
                    changes["strategy"] = {
                        "before": current_strategy,
                        "after": new_strategy,
                        "action": "simplified",
                        "reason": "high_response_time"
                    }
            # Si los tiempos son buenos, usar estrategia más completa
            elif avg_response_time < 0.5 and current_strategy == "selective":
                new_strategy = "integrated"
                self.dual_brain.set_combination_strategy(new_strategy)
                
                changes["strategy"] = {
                    "before": current_strategy,
                    "after": new_strategy,
                    "action": "enhanced",
                    "reason": "good_response_time"
                }
            
            return changes
        except Exception as e:
            logger.error(f"Error al optimizar estrategia de combinación: {e}")
            return {"error": str(e)}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Genera un informe completo de rendimiento.
        
        Returns:
            Diccionario con informe de rendimiento
        """
        try:
            # Obtener métricas actuales
            current_metrics = self._monitor_performance()
            
            # Obtener historial de optimización
            optimization_history = self.optimization_history[-10:] if self.optimization_history else []
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(current_metrics)
            
            # Construir informe
            report = {
                "timestamp": time.time(),
                "uptime": time.time() - self.metrics.uptime,
                "current_metrics": current_metrics,
                "optimization_history": optimization_history,
                "recommendations": recommendations,
                "configuration": {
                    "auto_optimization": self.config["auto_optimization"],
                    "monitoring_interval": self.config["monitoring_interval"],
                    "optimization_interval": self.config["optimization_interval"]
                }
            }
            
            # Guardar informe en memoria
            self.memory.store("last_performance_report", report, permanent=True)
            
            return report
        except Exception as e:
            logger.error(f"Error al generar informe de rendimiento: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones de optimización.
        
        Args:
            metrics: Métricas actuales de rendimiento
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        try:
            # Recomendaciones de caché
            cache_hit_rate = metrics["performance_metrics"]["cache_hit_rate"]
            if cache_hit_rate < 0.5:
                recommendations.append({
                    "type": "cache",
                    "priority": "medium",
                    "description": "Aumentar tamaño de caché para mejorar tasa de aciertos",
                    "current_value": f"{cache_hit_rate:.2f}",
                    "target_value": "> 0.7",
                    "action": "increase_cache_size"
                })
            
            # Recomendaciones de balance de hemisferios
            technical_time = metrics["dual_brain_metrics"]["technical_avg_time"]
            emotional_time = metrics["dual_brain_metrics"]["emotional_avg_time"]
            if technical_time > 0 and emotional_time > 0:
                time_ratio = technical_time / emotional_time
                if abs(time_ratio - 1.0) > 0.5:
                    slower = "técnico" if time_ratio > 1.0 else "emocional"
                    recommendations.append({
                        "type": "hemisphere_balance",
                        "priority": "high",
                        "description": f"Ajustar balance de hemisferios (hemisferio {slower} más lento)",
                        "current_value": f"{time_ratio:.2f}",
                        "target_value": "0.8 - 1.2",
                        "action": "adjust_hemisphere_weights"
                    })
            
            # Recomendaciones de tiempo de respuesta
            avg_response_time = metrics["performance_metrics"]["avg_response_time"]
            if avg_response_time > 1.0:
                recommendations.append({
                    "type": "response_time",
                    "priority": "high",
                    "description": "Tiempo de respuesta alto, considerar optimizaciones adicionales",
                    "current_value": f"{avg_response_time:.2f}s",
                    "target_value": "< 0.8s",
                    "action": "optimize_response_time"
                })
            
            # Recomendaciones de recursos del sistema
            system_resources = metrics["system_resources"]
            if system_resources["memory_usage"] > 0.85:
                recommendations.append({
                    "type": "system_resources",
                    "priority": "critical",
                    "description": "Uso de memoria muy alto, considerar reducir cachés",
                    "current_value": f"{system_resources['memory_usage']:.2f}",
                    "target_value": "< 0.8",
                    "action": "reduce_memory_usage"
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {e}")
            return []
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración del optimizador.
        
        Args:
            config: Diccionario con configuraciones a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Actualizar configuraciones
            for key, value in config.items():
                if key in self.config:
                    self.config[key] = value
            
            # Si se cambió auto_optimization, iniciar/detener monitoreo
            if "auto_optimization" in config:
                if config["auto_optimization"] and not self.monitoring_active:
                    self.start_monitoring()
                elif not config["auto_optimization"] and self.monitoring_active:
                    self.stop_monitoring()
            
            logger.info("Configuración de optimizador actualizada")
            return True
        except Exception as e:
            logger.error(f"Error al actualizar configuración de optimizador: {e}")
            return False
    
    def add_response_time(self, response_time: float) -> None:
        """
        Añade un tiempo de respuesta a las métricas.
        
        Args:
            response_time: Tiempo de respuesta en segundos
        """
        self.metrics.add_response_time(response_time)
