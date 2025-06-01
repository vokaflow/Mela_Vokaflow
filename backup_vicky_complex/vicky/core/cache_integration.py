"""
Integración de Caché Selectivo con DualBrain
-------------------------------------------

Este módulo implementa la integración del sistema de caché selectivo
con el Motor Dual-Hemisferio (DualBrain) para optimizar el rendimiento
y reducir la carga computacional.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple, Union
import threading
import traceback

# Importaciones internas
from .dual_brain import DualBrain, IntentParser, ResponseGenerator
from .selective_cache import SelectiveCache, AdaptivePolicy, PriorityPolicy
from .context import Context
from .memory import Memory

# Configurar logger
logger = logging.getLogger("vicky.cache_integration")

class DualBrainCacheManager:
    """
    Gestor de caché para el Motor Dual-Hemisferio (DualBrain).
    
    Esta clase implementa:
    1. Caché para respuestas completas
    2. Caché para resultados de procesamiento de hemisferios
    3. Caché para análisis de intenciones
    4. Estrategias de invalidación inteligente
    5. Optimización de rendimiento adaptativa
    """
    
    def __init__(self, dual_brain: DualBrain, memory: Memory):
        """
        Inicializa el gestor de caché para DualBrain.
        
        Args:
            dual_brain: Instancia del Motor Dual-Hemisferio
            memory: Sistema de memoria para persistencia
        """
        self.dual_brain = dual_brain
        self.memory = memory
        
        # Inicializar cachés
        self.response_cache = SelectiveCache[str](
            name="response_cache",
            max_size=500,
            policy=AdaptivePolicy(),
            default_ttl=3600  # 1 hora
        )
        
        self.hemisphere_cache = SelectiveCache[Dict[str, Any]](
            name="hemisphere_cache",
            max_size=200,
            policy=PriorityPolicy(),
            default_ttl=1800  # 30 minutos
        )
        
        self.intent_cache = SelectiveCache[Dict[str, Any]](
            name="intent_cache",
            max_size=300,
            policy=AdaptivePolicy(),
            default_ttl=3600  # 1 hora
        )
        
        # Estadísticas
        self.stats = {
            "total_requests": 0,
            "cached_responses": 0,
            "cached_hemisphere_results": 0,
            "cached_intent_analyses": 0,
            "total_time_saved": 0.0,
            "avg_time_saved": 0.0
        }
        
        # Configuración
        self.similarity_threshold = 0.85  # Umbral para considerar mensajes similares
        self.enable_response_cache = True
        self.enable_hemisphere_cache = True
        self.enable_intent_cache = True
        self.auto_invalidation_enabled = True
        
        # Hooks para funciones originales
        self._original_process_message = dual_brain.process_message
        self._original_process_parallel = dual_brain._process_parallel
        self._original_intent_parse = dual_brain.intent_parser.parse
        
        # Reemplazar métodos con versiones cacheadas
        self._patch_methods()
        
        logger.info("Gestor de caché para DualBrain inicializado")
    
    def _patch_methods(self) -> None:
        """Reemplaza métodos originales con versiones que usan caché."""
        # Reemplazar método de procesamiento de mensajes
        self.dual_brain.process_message = self._cached_process_message
        
        # Reemplazar método de procesamiento paralelo
        self.dual_brain._process_parallel = self._cached_process_parallel
        
        # Reemplazar método de análisis de intenciones
        self.dual_brain.intent_parser.parse = self._cached_intent_parse
    
    def _cached_process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Versión cacheada del método process_message.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Respuesta generada
        """
        context = context or {}
        self.stats["total_requests"] += 1
        
        # Verificar caché de respuestas si está habilitado
        if self.enable_response_cache:
            cache_key = self._generate_response_cache_key(message, context)
            cached_response = self.response_cache.get(cache_key)
            
            if cached_response:
                logger.info("Respuesta encontrada en caché")
                self.stats["cached_responses"] += 1
                
                # Estimar tiempo ahorrado (promedio de procesamiento)
                avg_processing_time = self.dual_brain.state.get("avg_processing_time", 0.5)
                self.stats["total_time_saved"] += avg_processing_time
                self.stats["avg_time_saved"] = (
                    self.stats["total_time_saved"] / self.stats["total_requests"]
                )
                
                return cached_response
        
        # Si no está en caché, procesar normalmente
        start_time = time.time()
        response = self._original_process_message(message, context)
        processing_time = time.time() - start_time
        
        # Actualizar tiempo promedio de procesamiento
        avg_processing_time = self.dual_brain.state.get("avg_processing_time", 0.0)
        request_count = self.dual_brain.state.get("request_count", 0)
        
        new_avg = (avg_processing_time * request_count + processing_time) / (request_count + 1)
        self.dual_brain.state.set("avg_processing_time", new_avg)
        self.dual_brain.state.set("request_count", request_count + 1)
        
        # Cachear respuesta si está habilitado
        if self.enable_response_cache:
            cache_key = self._generate_response_cache_key(message, context)
            
            # Metadatos para decisiones de caché
            metadata = {
                "processing_time": processing_time,
                "message_length": len(message),
                "response_length": len(response),
                "computation_cost": processing_time / 2.0,  # Normalizado a 0-1
                "priority": min(1.0, processing_time / 5.0)  # Priorizar respuestas costosas
            }
            
            self.response_cache.set(cache_key, response, metadata=metadata)
        
        return response
    
    def _cached_process_parallel(self, message: str, context: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Versión cacheada del método _process_parallel.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Tupla con resultados de ambos hemisferios
        """
        # Verificar caché de hemisferios si está habilitado
        if self.enable_hemisphere_cache:
            technical_cache_key = self._generate_hemisphere_cache_key(message, context, "technical")
            emotional_cache_key = self._generate_hemisphere_cache_key(message, context, "emotional")
            
            technical_result = self.hemisphere_cache.get(technical_cache_key)
            emotional_result = self.hemisphere_cache.get(emotional_cache_key)
            
            # Si ambos están en caché, usar resultados cacheados
            if technical_result and emotional_result:
                logger.info("Resultados de hemisferios encontrados en caché")
                self.stats["cached_hemisphere_results"] += 1
                return technical_result, emotional_result
            
            # Si solo uno está en caché, procesar el otro
            if technical_result:
                # Procesar solo hemisferio emocional
                emotional_result = self.dual_brain.emotional_hemisphere.process(message, context)
                
                # Cachear resultado emocional
                metadata = {
                    "processing_time": emotional_result.get("processing_time", 0.0),
                    "computation_cost": min(1.0, emotional_result.get("processing_time", 0.0) / 3.0),
                    "priority": emotional_result.get("confidence", 0.5)
                }
                self.hemisphere_cache.set(emotional_cache_key, emotional_result, metadata=metadata)
                
                return technical_result, emotional_result
            
            if emotional_result:
                # Procesar solo hemisferio técnico
                technical_result = self.dual_brain.technical_hemisphere.process(message, context)
                
                # Cachear resultado técnico
                metadata = {
                    "processing_time": technical_result.get("processing_time", 0.0),
                    "computation_cost": min(1.0, technical_result.get("processing_time", 0.0) / 3.0),
                    "priority": technical_result.get("confidence", 0.5)
                }
                self.hemisphere_cache.set(technical_cache_key, technical_result, metadata=metadata)
                
                return technical_result, emotional_result
        
        # Si no están en caché, procesar normalmente
        technical_result, emotional_result = self._original_process_parallel(message, context)
        
        # Cachear resultados si está habilitado
        if self.enable_hemisphere_cache:
            # Cachear resultado técnico
            technical_cache_key = self._generate_hemisphere_cache_key(message, context, "technical")
            technical_metadata = {
                "processing_time": technical_result.get("processing_time", 0.0),
                "computation_cost": min(1.0, technical_result.get("processing_time", 0.0) / 3.0),
                "priority": technical_result.get("confidence", 0.5)
            }
            self.hemisphere_cache.set(technical_cache_key, technical_result, metadata=technical_metadata)
            
            # Cachear resultado emocional
            emotional_cache_key = self._generate_hemisphere_cache_key(message, context, "emotional")
            emotional_metadata = {
                "processing_time": emotional_result.get("processing_time", 0.0),
                "computation_cost": min(1.0, emotional_result.get("processing_time", 0.0) / 3.0),
                "priority": emotional_result.get("confidence", 0.5)
            }
            self.hemisphere_cache.set(emotional_cache_key, emotional_result, metadata=emotional_metadata)
        
        return technical_result, emotional_result
    
    def _cached_intent_parse(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Versión cacheada del método parse del IntentParser.
        
        Args:
            message: Mensaje a analizar
            context: Contexto adicional
            
        Returns:
            Resultado del análisis de intención
        """
        context = context or {}
        
        # Verificar caché de intenciones si está habilitado
        if self.enable_intent_cache:
            cache_key = self._generate_intent_cache_key(message, context)
            cached_result = self.intent_cache.get(cache_key)
            
            if cached_result:
                logger.info("Análisis de intención encontrado en caché")
                self.stats["cached_intent_analyses"] += 1
                return cached_result
        
        # Si no está en caché, analizar normalmente
        start_time = time.time()
        result = self._original_intent_parse(message, context)
        processing_time = time.time() - start_time
        
        # Cachear resultado si está habilitado
        if self.enable_intent_cache:
            cache_key = self._generate_intent_cache_key(message, context)
            
            # Metadatos para decisiones de caché
            metadata = {
                "processing_time": processing_time,
                "message_length": len(message),
                "confidence": result.get("confidence", 0.5),
                "computation_cost": min(1.0, processing_time / 1.0)  # Normalizado a 0-1
            }
            
            self.intent_cache.set(cache_key, result, metadata=metadata)
        
        return result
    
    def _generate_response_cache_key(self, message: str, context: Dict[str, Any]) -> str:
        """
        Genera una clave de caché para respuestas.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Clave de caché
        """
        # Normalizar mensaje (eliminar espacios extra, convertir a minúsculas)
        normalized_message = " ".join(message.lower().split())
        
        # Extraer solo metadatos relevantes del contexto
        relevant_context = {}
        if context:
            for key in ["user_id", "language", "user_hemisphere_preference"]:
                if key in context:
                    relevant_context[key] = context[key]
        
        # Generar hash
        context_str = json.dumps(relevant_context, sort_keys=True) if relevant_context else ""
        key_str = f"{normalized_message}|{context_str}"
        return f"response:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _generate_hemisphere_cache_key(self, message: str, context: Dict[str, Any], hemisphere: str) -> str:
        """
        Genera una clave de caché para resultados de hemisferio.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            hemisphere: Nombre del hemisferio ("technical" o "emotional")
            
        Returns:
            Clave de caché
        """
        # Normalizar mensaje
        normalized_message = " ".join(message.lower().split())
        
        # Extraer solo metadatos relevantes del contexto
        relevant_context = {}
        if context:
            for key in ["user_id", "language"]:
                if key in context:
                    relevant_context[key] = context[key]
        
        # Generar hash
        context_str = json.dumps(relevant_context, sort_keys=True) if relevant_context else ""
        key_str = f"{normalized_message}|{context_str}|{hemisphere}"
        return f"hemisphere:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _generate_intent_cache_key(self, message: str, context: Dict[str, Any]) -> str:
        """
        Genera una clave de caché para análisis de intención.
        
        Args:
            message: Mensaje a analizar
            context: Contexto adicional
            
        Returns:
            Clave de caché
        """
        # Normalizar mensaje
        normalized_message = " ".join(message.lower().split())
        
        # Extraer solo metadatos relevantes del contexto
        relevant_context = {}
        if context:
            for key in ["user_id", "language"]:
                if key in context:
                    relevant_context[key] = context[key]
        
        # Generar hash
        context_str = json.dumps(relevant_context, sort_keys=True) if relevant_context else ""
        key_str = f"{normalized_message}|{context_str}"
        return f"intent:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def invalidate_caches(self, pattern: Optional[str] = None) -> Dict[str, int]:
        """
        Invalida entradas de caché según un patrón.
        
        Args:
            pattern: Patrón para coincidencia (opcional)
            
        Returns:
            Diccionario con número de entradas invalidadas por caché
        """
        results = {}
        
        if pattern:
            # Invalidar por patrón
            results["response_cache"] = self.response_cache.invalidate_by_pattern(pattern)
            results["hemisphere_cache"] = self.hemisphere_cache.invalidate_by_pattern(pattern)
            results["intent_cache"] = self.intent_cache.invalidate_by_pattern(pattern)
        else:
            # Limpiar todo
            self.response_cache.clear()
            self.hemisphere_cache.clear()
            self.intent_cache.clear()
            results = {
                "response_cache": "all",
                "hemisphere_cache": "all",
                "intent_cache": "all"
            }
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas completas del sistema de caché.
        
        Returns:
            Diccionario con métricas
        """
        metrics = {
            "stats": self.stats,
            "response_cache": self.response_cache.get_metrics(),
            "hemisphere_cache": self.hemisphere_cache.get_metrics(),
            "intent_cache": self.intent_cache.get_metrics(),
            "configuration": {
                "enable_response_cache": self.enable_response_cache,
                "enable_hemisphere_cache": self.enable_hemisphere_cache,
                "enable_intent_cache": self.enable_intent_cache,
                "auto_invalidation_enabled": self.auto_invalidation_enabled,
                "similarity_threshold": self.similarity_threshold
            },
            "total_memory_usage": (
                self.response_cache.get_memory_usage() +
                self.hemisphere_cache.get_memory_usage() +
                self.intent_cache.get_memory_usage()
            )
        }
        
        return metrics
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración del gestor de caché.
        
        Args:
            config: Diccionario con configuraciones a actualizar
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Actualizar configuraciones
            if "enable_response_cache" in config:
                self.enable_response_cache = bool(config["enable_response_cache"])
            
            if "enable_hemisphere_cache" in config:
                self.enable_hemisphere_cache = bool(config["enable_hemisphere_cache"])
            
            if "enable_intent_cache" in config:
                self.enable_intent_cache = bool(config["enable_intent_cache"])
            
            if "auto_invalidation_enabled" in config:
                self.auto_invalidation_enabled = bool(config["auto_invalidation_enabled"])
            
            if "similarity_threshold" in config:
                self.similarity_threshold = float(config["similarity_threshold"])
            
            # Actualizar tamaños de caché
            if "response_cache_size" in config:
                self.response_cache.set_max_size(int(config["response_cache_size"]))
            
            if "hemisphere_cache_size" in config:
                self.hemisphere_cache.set_max_size(int(config["hemisphere_cache_size"]))
            
            if "intent_cache_size" in config:
                self.intent_cache.set_max_size(int(config["intent_cache_size"]))
            
            logger.info("Configuración de caché actualizada")
            return True
        except Exception as e:
            logger.error(f"Error al actualizar configuración de caché: {e}")
            return False
    
    def restore_original_methods(self) -> None:
        """Restaura los métodos originales sin caché."""
        self.dual_brain.process_message = self._original_process_message
        self.dual_brain._process_parallel = self._original_process_parallel
        self.dual_brain.intent_parser.parse = self._original_intent_parse
        
        logger.info("Métodos originales restaurados")
    
    def save_cache_state(self) -> bool:
        """
        Guarda el estado actual de los cachés en memoria persistente.
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            # Guardar métricas
            self.memory.store("cache_metrics", self.get_metrics(), permanent=True)
            
            # Guardar estadísticas
            self.memory.store("cache_stats", self.stats, permanent=True)
            
            logger.info("Estado de caché guardado en memoria persistente")
            return True
        except Exception as e:
            logger.error(f"Error al guardar estado de caché: {e}")
            return False
    
    def load_cache_state(self) -> bool:
        """
        Carga el estado de los cachés desde memoria persistente.
        
        Returns:
            True si se cargó correctamente, False en caso contrario
        """
        try:
            # Cargar estadísticas
            saved_stats = self.memory.retrieve("cache_stats", None)
            if saved_stats:
                self.stats = saved_stats
            
            logger.info("Estado de caché cargado desde memoria persistente")
            return True
        except Exception as e:
            logger.error(f"Error al cargar estado de caché: {e}")
            return False
