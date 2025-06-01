"""
Caché de Selección Inteligente para VokaFlow
--------------------------------------------

Este módulo implementa un sistema avanzado de caché con selección inteligente
para optimizar el rendimiento del sistema VokaFlow, reduciendo la carga
computacional y mejorando los tiempos de respuesta.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
import json
import hashlib
import threading
from typing import Dict, Any, List, Optional, Tuple, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
import traceback
from collections import OrderedDict
import numpy as np

# Configurar logger
logger = logging.getLogger("vicky.selective_cache")

# Definir tipo genérico para valores de caché
T = TypeVar('T')

@dataclass
class CacheMetrics:
    """Métricas de rendimiento del sistema de caché."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    insertions: int = 0
    hit_rate: float = 0.0
    avg_lookup_time: float = 0.0
    total_lookup_time: float = 0.0
    avg_insertion_time: float = 0.0
    total_insertion_time: float = 0.0
    memory_usage: int = 0  # bytes estimados
    last_cleanup_time: float = 0.0
    
    def update_hit_rate(self) -> None:
        """Actualiza la tasa de aciertos."""
        total = self.hits + self.misses
        self.hit_rate = self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a un diccionario."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "insertions": self.insertions,
            "hit_rate": self.hit_rate,
            "avg_lookup_time": self.avg_lookup_time,
            "avg_insertion_time": self.avg_insertion_time,
            "memory_usage": self.memory_usage,
            "last_cleanup_time": self.last_cleanup_time
        }


@dataclass
class CacheEntry(Generic[T]):
    """Entrada de caché con metadatos para políticas de selección."""
    key: str
    value: T
    creation_time: float
    last_access_time: float
    access_count: int = 0
    size_estimate: int = 0  # bytes estimados
    priority: float = 0.0  # 0.0 a 1.0, mayor = más prioritario
    ttl: Optional[float] = None  # tiempo de vida en segundos
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_access(self) -> None:
        """Actualiza estadísticas de acceso."""
        self.last_access_time = time.time()
        self.access_count += 1
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        if self.ttl is None:
            return False
        return (time.time() - self.creation_time) > self.ttl
    
    def calculate_priority(self, current_time: float) -> float:
        """
        Calcula la prioridad de la entrada para políticas de selección.
        
        Args:
            current_time: Tiempo actual para cálculos de recencia
            
        Returns:
            Valor de prioridad (0.0-1.0)
        """
        # Factores para prioridad
        recency = 1.0 - min(1.0, (current_time - self.last_access_time) / 3600.0)  # Decae en 1 hora
        frequency = min(1.0, self.access_count / 10.0)  # Normalizado a 10 accesos
        
        # Si hay prioridad explícita, usarla con mayor peso
        if self.priority > 0:
            return 0.6 * self.priority + 0.25 * recency + 0.15 * frequency
        
        # Si no, combinar recencia y frecuencia
        return 0.7 * recency + 0.3 * frequency


class CachePolicy:
    """Interfaz para políticas de selección de caché."""
    
    def select_for_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """
        Selecciona entradas para eliminación según la política.
        
        Args:
            entries: Lista de entradas de caché
            
        Returns:
            Lista de claves de entradas a eliminar
        """
        raise NotImplementedError("Debe implementarse en subclases")
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Determina si un valor debe ser cacheado.
        
        Args:
            key: Clave de caché
            value: Valor a cachear
            metadata: Metadatos asociados
            
        Returns:
            True si debe cachearse, False en caso contrario
        """
        raise NotImplementedError("Debe implementarse en subclases")


class LRUPolicy(CachePolicy):
    """Política Least Recently Used (LRU)."""
    
    def select_for_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """
        Selecciona entradas menos recientemente usadas para eliminación.
        
        Args:
            entries: Lista de entradas de caché
            
        Returns:
            Lista de claves de entradas a eliminar
        """
        # Ordenar por tiempo de último acceso (más antiguo primero)
        sorted_entries = sorted(entries, key=lambda e: e.last_access_time)
        
        # Seleccionar 25% más antiguas
        count_to_evict = max(1, len(entries) // 4)
        return [entry.key for entry in sorted_entries[:count_to_evict]]
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Determina si un valor debe ser cacheado (siempre true en LRU).
        
        Args:
            key: Clave de caché
            value: Valor a cachear
            metadata: Metadatos asociados
            
        Returns:
            True si debe cachearse, False en caso contrario
        """
        # En LRU simple, siempre cachear
        return True


class LFUPolicy(CachePolicy):
    """Política Least Frequently Used (LFU)."""
    
    def select_for_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """
        Selecciona entradas menos frecuentemente usadas para eliminación.
        
        Args:
            entries: Lista de entradas de caché
            
        Returns:
            Lista de claves de entradas a eliminar
        """
        # Ordenar por conteo de accesos (menor primero)
        sorted_entries = sorted(entries, key=lambda e: e.access_count)
        
        # Seleccionar 25% menos usadas
        count_to_evict = max(1, len(entries) // 4)
        return [entry.key for entry in sorted_entries[:count_to_evict]]
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Determina si un valor debe ser cacheado.
        
        Args:
            key: Clave de caché
            value: Valor a cachear
            metadata: Metadatos asociados
            
        Returns:
            True si debe cachearse, False en caso contrario
        """
        # En LFU, cachear si hay indicación de uso frecuente
        expected_frequency = metadata.get("expected_frequency", 0.0)
        return expected_frequency > 0.3  # Umbral de frecuencia esperada


class PriorityPolicy(CachePolicy):
    """Política basada en prioridad calculada."""
    
    def select_for_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """
        Selecciona entradas con menor prioridad para eliminación.
        
        Args:
            entries: Lista de entradas de caché
            
        Returns:
            Lista de claves de entradas a eliminar
        """
        current_time = time.time()
        
        # Calcular prioridad actual para cada entrada
        for entry in entries:
            entry.priority = entry.calculate_priority(current_time)
        
        # Ordenar por prioridad (menor primero)
        sorted_entries = sorted(entries, key=lambda e: e.priority)
        
        # Seleccionar 25% menos prioritarias
        count_to_evict = max(1, len(entries) // 4)
        return [entry.key for entry in sorted_entries[:count_to_evict]]
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Determina si un valor debe ser cacheado según su prioridad.
        
        Args:
            key: Clave de caché
            value: Valor a cachear
            metadata: Metadatos asociados
            
        Returns:
            True si debe cachearse, False en caso contrario
        """
        # Obtener prioridad explícita o calcularla
        priority = metadata.get("priority", 0.0)
        
        if priority > 0:
            return priority > 0.4  # Umbral de prioridad explícita
        
        # Calcular basado en otros factores
        expected_frequency = metadata.get("expected_frequency", 0.0)
        computation_cost = metadata.get("computation_cost", 0.0)
        value_size = metadata.get("value_size", 1.0)
        
        # Priorizar items costosos de computar pero no muy grandes
        calculated_priority = (0.4 * expected_frequency + 
                              0.5 * computation_cost - 
                              0.1 * value_size)
        
        return calculated_priority > 0.3


class SizeAwarePolicy(CachePolicy):
    """Política que considera el tamaño de las entradas."""
    
    def select_for_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """
        Selecciona entradas para eliminación considerando tamaño y valor.
        
        Args:
            entries: Lista de entradas de caché
            
        Returns:
            Lista de claves de entradas a eliminar
        """
        current_time = time.time()
        
        # Calcular ratio valor/tamaño para cada entrada
        for entry in entries:
            priority = entry.calculate_priority(current_time)
            size = max(1, entry.size_estimate)  # Evitar división por cero
            entry.metadata["value_size_ratio"] = priority / size
        
        # Ordenar por ratio valor/tamaño (menor primero)
        sorted_entries = sorted(entries, key=lambda e: e.metadata.get("value_size_ratio", 0))
        
        # Seleccionar 25% con peor ratio
        count_to_evict = max(1, len(entries) // 4)
        return [entry.key for entry in sorted_entries[:count_to_evict]]
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Determina si un valor debe ser cacheado según tamaño y valor.
        
        Args:
            key: Clave de caché
            value: Valor a cachear
            metadata: Metadatos asociados
            
        Returns:
            True si debe cachearse, False en caso contrario
        """
        # Obtener tamaño estimado
        size = metadata.get("value_size", 1.0)
        
        # Rechazar valores muy grandes
        if size > 10_000_000:  # 10 MB
            return False
        
        # Para valores grandes, requerir alta prioridad
        if size > 1_000_000:  # 1 MB
            return metadata.get("priority", 0.0) > 0.7
        
        # Para valores medianos, criterio moderado
        if size > 100_000:  # 100 KB
            return metadata.get("priority", 0.0) > 0.4
        
        # Valores pequeños, criterio laxo
        return True


class AdaptivePolicy(CachePolicy):
    """Política adaptativa que combina múltiples estrategias."""
    
    def __init__(self):
        """Inicializa la política adaptativa."""
        self.policies = {
            "lru": LRUPolicy(),
            "lfu": LFUPolicy(),
            "priority": PriorityPolicy(),
            "size_aware": SizeAwarePolicy()
        }
        
        # Pesos iniciales para cada política
        self.policy_weights = {
            "lru": 0.3,
            "lfu": 0.2,
            "priority": 0.3,
            "size_aware": 0.2
        }
        
        # Métricas de efectividad por política
        self.policy_effectiveness = {
            "lru": 0.5,
            "lfu": 0.5,
            "priority": 0.5,
            "size_aware": 0.5
        }
    
    def select_for_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """
        Selecciona entradas para eliminación combinando múltiples políticas.
        
        Args:
            entries: Lista de entradas de caché
            
        Returns:
            Lista de claves de entradas a eliminar
        """
        # Recopilar votos de cada política
        votes = {}
        for policy_name, policy in self.policies.items():
            policy_votes = policy.select_for_eviction(entries)
            weight = self.policy_weights[policy_name]
            
            for key in policy_votes:
                if key not in votes:
                    votes[key] = 0
                votes[key] += weight
        
        # Ordenar por votos (mayor primero)
        sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
        
        # Seleccionar 25% con más votos
        count_to_evict = max(1, len(entries) // 4)
        return [key for key, _ in sorted_votes[:count_to_evict]]
    
    def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Determina si un valor debe ser cacheado combinando múltiples políticas.
        
        Args:
            key: Clave de caché
            value: Valor a cachear
            metadata: Metadatos asociados
            
        Returns:
            True si debe cachearse, False en caso contrario
        """
        # Recopilar votos de cada política
        votes = 0.0
        total_weight = 0.0
        
        for policy_name, policy in self.policies.items():
            weight = self.policy_weights[policy_name]
            should_cache = policy.should_cache(key, value, metadata)
            
            votes += weight * (1.0 if should_cache else 0.0)
            total_weight += weight
        
        # Normalizar votos
        if total_weight > 0:
            normalized_votes = votes / total_weight
        else:
            normalized_votes = 0.5
        
        # Decidir basado en umbral
        return normalized_votes > 0.5
    
    def update_effectiveness(self, policy_name: str, effectiveness: float) -> None:
        """
        Actualiza la efectividad medida de una política.
        
        Args:
            policy_name: Nombre de la política
            effectiveness: Valor de efectividad (0.0-1.0)
        """
        if policy_name in self.policy_effectiveness:
            # Actualización suave (70% nuevo, 30% anterior)
            self.policy_effectiveness[policy_name] = (
                0.7 * effectiveness + 
                0.3 * self.policy_effectiveness[policy_name]
            )
            
            # Recalcular pesos
            self._recalculate_weights()
    
    def _recalculate_weights(self) -> None:
        """Recalcula los pesos de las políticas basado en efectividad."""
        total_effectiveness = sum(self.policy_effectiveness.values())
        
        if total_effectiveness > 0:
            for policy_name in self.policy_weights:
                self.policy_weights[policy_name] = (
                    self.policy_effectiveness[policy_name] / total_effectiveness
                )


class SelectiveCache(Generic[T]):
    """
    Caché inteligente con selección adaptativa para optimización de rendimiento.
    
    Esta clase implementa un sistema de caché avanzado que:
    1. Utiliza políticas adaptativas para decidir qué cachear
    2. Optimiza la gestión de memoria mediante selección inteligente
    3. Proporciona métricas detalladas de rendimiento
    4. Soporta invalidación selectiva y limpieza automática
    5. Permite personalización de estrategias según tipo de datos
    """
    
    def __init__(self, name: str, max_size: int = 1000, 
                policy: Optional[CachePolicy] = None,
                default_ttl: Optional[float] = None):
        """
        Inicializa el caché selectivo.
        
        Args:
            name: Nombre identificativo del caché
            max_size: Tamaño máximo (número de entradas)
            policy: Política de selección (opcional)
            default_ttl: Tiempo de vida por defecto en segundos (opcional)
        """
        self.name = name
        self.max_size = max_size
        self.policy = policy or AdaptivePolicy()
        self.default_ttl = default_ttl
        
        # Almacenamiento principal (thread-safe)
        self._cache: Dict[str, CacheEntry[T]] = {}
        self._lock = threading.RLock()
        
        # Métricas
        self.metrics = CacheMetrics()
        
        # Configuración
        self.auto_cleanup_threshold = 0.9  # 90% de capacidad
        self.size_estimation_samples = 10
        
        logger.info(f"Caché selectivo '{name}' inicializado (max_size={max_size})")
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Obtiene un valor del caché.
        
        Args:
            key: Clave de búsqueda
            default: Valor por defecto si no se encuentra
            
        Returns:
            Valor cacheado o valor por defecto
        """
        start_time = time.time()
        
        with self._lock:
            # Verificar si existe y no ha expirado
            if key in self._cache and not self._cache[key].is_expired():
                # Actualizar estadísticas de acceso
                self._cache[key].update_access()
                
                # Actualizar métricas
                self.metrics.hits += 1
                lookup_time = time.time() - start_time
                self.metrics.total_lookup_time += lookup_time
                self.metrics.avg_lookup_time = (
                    self.metrics.total_lookup_time / 
                    (self.metrics.hits + self.metrics.misses)
                )
                self.metrics.update_hit_rate()
                
                return self._cache[key].value
            else:
                # Eliminar si ha expirado
                if key in self._cache:
                    del self._cache[key]
                
                # Actualizar métricas
                self.metrics.misses += 1
                lookup_time = time.time() - start_time
                self.metrics.total_lookup_time += lookup_time
                self.metrics.avg_lookup_time = (
                    self.metrics.total_lookup_time / 
                    (self.metrics.hits + self.metrics.misses)
                )
                self.metrics.update_hit_rate()
                
                return default
    
    def set(self, key: str, value: T, ttl: Optional[float] = None, 
           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Almacena un valor en el caché si cumple criterios de selección.
        
        Args:
            key: Clave de almacenamiento
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos (opcional)
            metadata: Metadatos para decisiones de selección (opcional)
            
        Returns:
            True si se almacenó, False si fue rechazado
        """
        start_time = time.time()
        metadata = metadata or {}
        
        # Estimar tamaño si no se proporciona
        if "value_size" not in metadata:
            metadata["value_size"] = self._estimate_size(value)
        
        # Verificar si debe cachearse
        if not self.policy.should_cache(key, value, metadata):
            return False
        
        with self._lock:
            # Verificar si necesitamos limpiar
            current_size = len(self._cache)
            if current_size >= int(self.max_size * self.auto_cleanup_threshold):
                self._cleanup()
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                creation_time=time.time(),
                last_access_time=time.time(),
                size_estimate=metadata.get("value_size", 0),
                priority=metadata.get("priority", 0.0),
                ttl=ttl or self.default_ttl,
                metadata=metadata
            )
            
            # Almacenar
            self._cache[key] = entry
            
            # Actualizar métricas
            self.metrics.insertions += 1
            insertion_time = time.time() - start_time
            self.metrics.total_insertion_time += insertion_time
            self.metrics.avg_insertion_time = (
                self.metrics.total_insertion_time / 
                self.metrics.insertions
            )
            self.metrics.memory_usage += entry.size_estimate
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Elimina una entrada del caché.
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        with self._lock:
            if key in self._cache:
                # Actualizar métricas
                self.metrics.memory_usage -= self._cache[key].size_estimate
                
                # Eliminar
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Limpia completamente el caché."""
        with self._lock:
            self._cache.clear()
            
            # Reiniciar métricas de memoria
            self.metrics.memory_usage = 0
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalida entradas que coinciden con un patrón.
        
        Args:
            pattern: Patrón para coincidencia
            
        Returns:
            Número de entradas invalidadas
        """
        import re
        regex = re.compile(pattern)
        count = 0
        
        with self._lock:
            keys_to_delete = []
            
            # Identificar claves a eliminar
            for key in self._cache:
                if regex.search(key):
                    keys_to_delete.append(key)
            
            # Eliminar claves
            for key in keys_to_delete:
                self.metrics.memory_usage -= self._cache[key].size_estimate
                del self._cache[key]
                count += 1
        
        return count
    
    def invalidate_by_prefix(self, prefix: str) -> int:
        """
        Invalida entradas que comienzan con un prefijo.
        
        Args:
            prefix: Prefijo para coincidencia
            
        Returns:
            Número de entradas invalidadas
        """
        count = 0
        
        with self._lock:
            keys_to_delete = []
            
            # Identificar claves a eliminar
            for key in self._cache:
                if key.startswith(prefix):
                    keys_to_delete.append(key)
            
            # Eliminar claves
            for key in keys_to_delete:
                self.metrics.memory_usage -= self._cache[key].size_estimate
                del self._cache[key]
                count += 1
        
        return count
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas actuales del caché.
        
        Returns:
            Diccionario con métricas
        """
        with self._lock:
            metrics_dict = self.metrics.to_dict()
            metrics_dict["size"] = len(self._cache)
            metrics_dict["max_size"] = self.max_size
            metrics_dict["utilization"] = len(self._cache) / self.max_size
            
            # Añadir información de política
            if isinstance(self.policy, AdaptivePolicy):
                metrics_dict["policy"] = {
                    "type": "adaptive",
                    "weights": self.policy.policy_weights,
                    "effectiveness": self.policy.policy_effectiveness
                }
            else:
                metrics_dict["policy"] = {
                    "type": self.policy.__class__.__name__
                }
            
            return metrics_dict
    
    def _cleanup(self) -> None:
        """Limpia el caché según la política de selección."""
        # Primero, eliminar entradas expiradas
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self.metrics.memory_usage -= self._cache[key].size_estimate
            del self._cache[key]
        
        # Si aún necesitamos espacio, usar política de selección
        if len(self._cache) >= self.max_size:
            entries = list(self._cache.values())
            keys_to_evict = self.policy.select_for_eviction(entries)
            
            for key in keys_to_evict:
                if key in self._cache:  # Verificar que aún existe
                    self.metrics.memory_usage -= self._cache[key].size_estimate
                    del self._cache[key]
                    self.metrics.evictions += 1
        
        # Actualizar métricas
        self.metrics.last_cleanup_time = time.time()
    
    def _estimate_size(self, value: T) -> int:
        """
        Estima el tamaño en bytes de un valor.
        
        Args:
            value: Valor a estimar
            
        Returns:
            Tamaño estimado en bytes
        """
        try:
            # Método directo para tipos básicos
            if isinstance(value, (int, float, bool, type(None))):
                return 8  # Aproximación para tipos simples
            
            if isinstance(value, str):
                return len(value) * 2  # Aproximación para strings (2 bytes por char)
            
            if isinstance(value, (list, tuple, set)):
                # Muestrear para colecciones grandes
                if len(value) > self.size_estimation_samples:
                    sample = list(value)[:self.size_estimation_samples]
                    avg_size = sum(self._estimate_size(item) for item in sample) / len(sample)
                    return int(avg_size * len(value))
                else:
                    return sum(self._estimate_size(item) for item in value)
            
            if isinstance(value, dict):
                # Muestrear para diccionarios grandes
                if len(value) > self.size_estimation_samples:
                    sample_keys = list(value.keys())[:self.size_estimation_samples]
                    avg_size = sum(
                        self._estimate_size(k) + self._estimate_size(value[k]) 
                        for k in sample_keys
                    ) / len(sample_keys)
                    return int(avg_size * len(value))
                else:
                    return sum(
                        self._estimate_size(k) + self._estimate_size(v) 
                        for k, v in value.items()
                    )
            
            # Para objetos complejos, usar serialización
            import pickle
            return len(pickle.dumps(value))
            
        except Exception as e:
            logger.warning(f"Error al estimar tamaño: {e}")
            return 100  # Valor por defecto
    
    def get_keys(self) -> List[str]:
        """
        Obtiene todas las claves actualmente en el caché.
        
        Returns:
            Lista de claves
        """
        with self._lock:
            return list(self._cache.keys())
    
    def get_size(self) -> int:
        """
        Obtiene el número actual de entradas en el caché.
        
        Returns:
            Número de entradas
        """
        with self._lock:
            return len(self._cache)
    
    def get_memory_usage(self) -> int:
        """
        Obtiene el uso estimado de memoria en bytes.
        
        Returns:
            Uso de memoria estimado
        """
        with self._lock:
            return self.metrics.memory_usage
    
    def set_max_size(self, new_max_size: int) -> None:
        """
        Actualiza el tamaño máximo del caché.
        
        Args:
            new_max_size: Nuevo tamaño máximo
        """
        with self._lock:
            self.max_size = new_max_size
            
            # Si el nuevo tamaño es menor que el actual, limpiar
            if len(self._cache) > new_max_size:
                self._cleanup()
    
    def update_policy(self, policy: CachePolicy) -> None:
        """
        Actualiza la política de selección.
        
        Args:
            policy: Nueva política
        """
        with self._lock:
            self.policy = policy
