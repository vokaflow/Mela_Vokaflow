"""
Capa de Integración para VokaFlow
---------------------------------

Este módulo proporciona una capa de abstracción para la integración entre
los diferentes componentes del sistema VokaFlow, facilitando la comunicación
entre el Motor Dual-Hemisferio (DualBrain), el Gestor de Modelos y el 
Gestor de Personalidad.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field

from .model_manager import ModelManager
from .personality_manager import PersonalityManager
from .context import Context
from .memory import Memory
from .state import State
from .dual_brain import DualBrain, IntentParser, ResponseGenerator

# Configurar logger
logger = logging.getLogger("vicky.integration")

@dataclass
class IntegrationMetrics:
    """Métricas de rendimiento para la capa de integración."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    total_response_time: float = 0.0
    model_load_failures: int = 0
    personality_load_failures: int = 0
    last_error: str = ""
    last_request_timestamp: float = 0.0


class IntegrationLayer:
    """
    Capa de integración que coordina la comunicación entre los componentes
    principales del sistema VokaFlow.
    """
    
    def __init__(self, model_manager: ModelManager, 
                 personality_manager: PersonalityManager,
                 context: Context, memory: Memory, state: State):
        """
        Inicializa la capa de integración.
        
        Args:
            model_manager: Gestor de modelos de IA
            personality_manager: Gestor de personalidad
            context: Sistema de contexto
            memory: Sistema de memoria
            state: Sistema de estado
        """
        self.model_manager = model_manager
        self.personality_manager = personality_manager
        self.context = context
        self.memory = memory
        self.state = state
        
        # Inicializar el cerebro dual
        self.dual_brain = DualBrain(
            model_manager=model_manager,
            personality_manager=personality_manager,
            context=context,
            memory=memory,
            state=state
        )
        
        # Métricas de integración
        self.metrics = IntegrationMetrics()
        
        # Configuración de integración
        self.config = {
            "auto_load_models": True,
            "auto_load_personality": True,
            "fallback_enabled": True,
            "performance_monitoring": True,
            "cache_responses": True,
            "cache_size": 100
        }
        
        # Caché de respuestas
        self.response_cache = {}
        
        logger.info("Capa de integración inicializada")
    
    def initialize_components(self) -> bool:
        """
        Inicializa todos los componentes necesarios para el funcionamiento
        del sistema.
        
        Returns:
            True si todos los componentes se inicializaron correctamente,
            False en caso contrario
        """
        success = True
        
        try:
            # Cargar configuraciones de personalidad
            if self.config["auto_load_personality"]:
                if not self.dual_brain.load_configuration():
                    logger.warning("No se pudieron cargar las configuraciones de personalidad")
                    self.metrics.personality_load_failures += 1
                    success = False
            
            # Precargar modelos esenciales
            if self.config["auto_load_models"]:
                models_to_load = ["language", "embedding"]
                for model_type in models_to_load:
                    if not self.model_manager.get_model(model_type):
                        logger.warning(f"No se pudo cargar el modelo {model_type}")
                        self.metrics.model_load_failures += 1
                        success = False
            
            return success
        except Exception as e:
            logger.error(f"Error al inicializar componentes: {e}")
            self.metrics.last_error = str(e)
            return False
    
    def process_request(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa una solicitud de usuario utilizando el cerebro dual.
        
        Args:
            message: Mensaje del usuario
            context: Contexto adicional (opcional)
            
        Returns:
            Diccionario con la respuesta y metadatos
        """
        start_time = time.time()
        self.metrics.total_requests += 1
        self.metrics.last_request_timestamp = start_time
        context = context or {}
        
        # Verificar caché si está habilitado
        cache_key = f"{message}_{hash(frozenset(context.items()))}"
        if self.config["cache_responses"] and cache_key in self.response_cache:
            logger.info("Respuesta encontrada en caché")
            cached_response = self.response_cache[cache_key]
            # Actualizar métricas
            self.metrics.successful_requests += 1
            return cached_response
        
        try:
            # Procesar mensaje con el cerebro dual
            response = self.dual_brain.process_message(message, context)
            
            # Preparar resultado
            result = {
                "response": response,
                "success": True,
                "processing_time": time.time() - start_time,
                "timestamp": time.time(),
                "message_id": f"msg_{int(time.time() * 1000)}",
                "context_used": context
            }
            
            # Actualizar métricas
            self.metrics.successful_requests += 1
            self.metrics.total_response_time += result["processing_time"]
            self.metrics.avg_response_time = (
                self.metrics.total_response_time / self.metrics.successful_requests
            )
            
            # Guardar en caché si está habilitado
            if self.config["cache_responses"]:
                # Limitar tamaño de caché
                if len(self.response_cache) >= self.config["cache_size"]:
                    # Eliminar entrada más antigua
                    oldest_key = next(iter(self.response_cache))
                    del self.response_cache[oldest_key]
                
                self.response_cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Error al procesar solicitud: {e}")
            
            # Actualizar métricas
            self.metrics.failed_requests += 1
            self.metrics.last_error = str(e)
            
            # Intentar fallback si está habilitado
            if self.config["fallback_enabled"]:
                try:
                    fallback_response = self._process_fallback(message, context)
                    return {
                        "response": fallback_response,
                        "success": True,
                        "fallback": True,
                        "processing_time": time.time() - start_time,
                        "timestamp": time.time(),
                        "message_id": f"msg_{int(time.time() * 1000)}",
                        "error": str(e)
                    }
                except Exception as fallback_error:
                    logger.error(f"Error en fallback: {fallback_error}")
            
            # Si todo falla, devolver error
            return {
                "response": f"Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}",
                "success": False,
                "processing_time": time.time() - start_time,
                "timestamp": time.time(),
                "message_id": f"msg_{int(time.time() * 1000)}",
                "error": str(e)
            }
    
    def _process_fallback(self, message: str, context: Dict[str, Any]) -> str:
        """
        Procesa una solicitud utilizando un método de respaldo.
        
        Args:
            message: Mensaje del usuario
            context: Contexto adicional
            
        Returns:
            Respuesta generada
        """
        logger.info("Utilizando procesamiento de fallback")
        
        # Intentar usar el modelo de lenguaje directamente
        language_model = self.model_manager.get_model("language")
        if language_model:
            # Aplicar personalidad si está disponible
            enhanced_message = message
            if hasattr(self.personality_manager, 'apply_personality_to_prompt'):
                enhanced_message = self.personality_manager.apply_personality_to_prompt(message)
            
            return language_model.generate(enhanced_message)
        else:
            return "Lo siento, no puedo procesar tu mensaje en este momento."
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración de la capa de integración.
        
        Args:
            config_updates: Diccionario con actualizaciones de configuración
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            for key, value in config_updates.items():
                if key in self.config:
                    self.config[key] = value
                else:
                    logger.warning(f"Configuración desconocida: {key}")
            
            logger.info(f"Configuración actualizada: {config_updates}")
            return True
        except Exception as e:
            logger.error(f"Error al actualizar configuración: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento de la capa de integración.
        
        Returns:
            Diccionario con métricas
        """
        # Obtener métricas del cerebro dual
        dual_brain_metrics = self.dual_brain.get_processing_stats()
        
        # Combinar con métricas de integración
        combined_metrics = {
            "integration": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (
                    self.metrics.successful_requests / self.metrics.total_requests
                    if self.metrics.total_requests > 0 else 0
                ),
                "avg_response_time": self.metrics.avg_response_time,
                "model_load_failures": self.metrics.model_load_failures,
                "personality_load_failures": self.metrics.personality_load_failures,
                "last_error": self.metrics.last_error,
                "cache_size": len(self.response_cache),
                "cache_enabled": self.config["cache_responses"]
            },
            "dual_brain": dual_brain_metrics
        }
        
        return combined_metrics
    
    def clear_cache(self) -> bool:
        """
        Limpia la caché de respuestas.
        
        Returns:
            True si se limpió correctamente, False en caso contrario
        """
        try:
            self.response_cache.clear()
            logger.info("Caché de respuestas limpiada")
            return True
        except Exception as e:
            logger.error(f"Error al limpiar caché: {e}")
            return False
    
    def set_hemisphere_balance(self, technical_weight: float, emotional_weight: float) -> bool:
        """
        Establece el balance entre hemisferios técnico y emocional.
        
        Args:
            technical_weight: Peso para el hemisferio técnico (0.0-1.0)
            emotional_weight: Peso para el hemisferio emocional (0.0-1.0)
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            weights = {
                "technical": max(0.0, min(1.0, technical_weight)),
                "emotional": max(0.0, min(1.0, emotional_weight))
            }
            
            return self.dual_brain.set_hemisphere_weights(weights)
        except Exception as e:
            logger.error(f"Error al establecer balance de hemisferios: {e}")
            return False
    
    def set_response_strategy(self, strategy: str) -> bool:
        """
        Establece la estrategia de generación de respuestas.
        
        Args:
            strategy: Nombre de la estrategia
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            return self.dual_brain.set_combination_strategy(strategy)
        except Exception as e:
            logger.error(f"Error al establecer estrategia de respuesta: {e}")
            return False
