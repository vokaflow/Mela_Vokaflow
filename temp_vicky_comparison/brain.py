"""
Núcleo central de Vicky, la IA de VokaFlow.

Este módulo implementa la lógica principal del cerebro de Vicky,
incluyendo la gestión de modelos, el procesamiento del lenguaje natural
y la coordinación de los hemisferios técnico y emocional.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
import json
import os

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vicky.brain")

class VickyBrain:
    """
    Núcleo central de Vicky, la IA de VokaFlow.
    
    Coordina los diferentes componentes del sistema para procesar
    consultas del usuario y generar respuestas coherentes y adaptadas.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el cerebro de Vicky.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Inicializar componentes básicos
        self.model_manager = ModelManager()
        self.context = Context()
        self.memory = Memory()
        self.state = State()
        
        # Inicializar cerebro dual como motor principal de procesamiento
        self.dual_brain = DualBrain(
            model_manager=self.model_manager,
            context=self.context,
            memory=self.memory,
            state=self.state
        )
        
        logger.info("Cerebro de Vicky inicializado")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Carga la configuración del sistema.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
            
        Returns:
            Diccionario con la configuración
        """
        # Implementación simple para cargar configuración
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar configuración: {e}")
        
        # Configuración por defecto
        return {
            "name": "Vicky",
            "version": "0.2.0",
            "hemisphere_balance": {
                "technical": 0.6,
                "emotional": 0.4
            },
            "combination_strategy": "hybrid_fusion"
        }
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje y genera una respuesta.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Diccionario con la respuesta y metadatos
        """
        logger.info(f"Procesando mensaje: {message[:50]}...")
        start_time = time.time()
        context = context or {}
        
        # Actualizar contexto con metadatos
        for key, value in context.items():
            self.context.set_metadata(key, value)
        
        # Añadir mensaje al historial de contexto
        self.context.add_message("user", message)
        
        try:
            # Procesar mensaje con el cerebro dual
            technical_response, emotional_response = self.dual_brain.process_dual(message, context)
            
            # Combinar respuestas
            combined_response = self.dual_brain.combine_responses(
                technical_response, 
                emotional_response,
                message
            )
            
            # Añadir respuesta al historial de contexto
            self.context.add_message("assistant", combined_response)
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            # Obtener balance actual de hemisferios
            hemisphere_balance = self.dual_brain.get_hemisphere_weights()
            
            # Construir respuesta
            response = {
                "response": combined_response,
                "context": context,
                "metadata": {
                    "processingTime": processing_time,
                    "hemisphere": hemisphere_balance,
                    "confidence": 0.92  # En un sistema real, esto vendría del modelo
                }
            }
            
            logger.info(f"Mensaje procesado en {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}")
            
            # Respuesta de fallback
            return {
                "response": "Lo siento, no puedo procesar tu consulta en este momento.",
                "context": context,
                "metadata": {
                    "processingTime": time.time() - start_time,
                    "error": str(e)
                }
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema.
        
        Returns:
            Diccionario con información del estado del sistema
        """
        try:
            # Obtener estadísticas del cerebro dual
            dual_brain_stats = self.dual_brain.get_processing_stats()
            
            # Obtener modelos cargados
            loaded_models = self.model_manager.get_loaded_models()
            
            # Construir estado del sistema
            system_status = {
                "status": "online",
                "version": self.config.get("version", "0.2.0"),
                "uptime": time.time() - self.state.get("start_time", time.time()),
                "loadedModels": loaded_models,
                "memoryUsage": self._get_memory_usage(),
                "processingStats": dual_brain_stats,
                "hemisphereBalance": self.dual_brain.get_hemisphere_weights()
            }
            
            return system_status
        except Exception as e:
            logger.error(f"Error al obtener estado del sistema: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """
        Obtiene información sobre el uso de memoria.
        
        Returns:
            Diccionario con información de memoria
        """
        # En un sistema real, esto obtendría información real del sistema
        # Por ahora, devolvemos valores simulados
        return {
            "total": 16384,  # MB
            "used": 8192,    # MB
            "free": 8192     # MB
        }
    
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
            # Validar que los pesos sumen 1.0
            if abs((technical_weight + emotional_weight) - 1.0) > 0.001:
                logger.error(f"Los pesos deben sumar 1.0: {technical_weight} + {emotional_weight} = {technical_weight + emotional_weight}")
                return False
            
            # Establecer nuevos pesos
            result = self.dual_brain.set_hemisphere_weights({
                "technical": technical_weight,
                "emotional": emotional_weight
            })
            
            if result:
                # Actualizar configuración
                self.config["hemisphere_balance"] = {
                    "technical": technical_weight,
                    "emotional": emotional_weight
                }
                
                logger.info(f"Balance de hemisferios actualizado: técnico={technical_weight}, emocional={emotional_weight}")
            
            return result
        except Exception as e:
            logger.error(f"Error al establecer balance de hemisferios: {e}")
            return False


# Clases auxiliares simuladas para el ejemplo
class ModelManager:
    def __init__(self):
        self.models = {
            "language": "qwen-7b",
            "translation": "nllb-200",
            "speech": "whisper-medium"
        }
    
    def get_loaded_models(self) -> List[str]:
        return list(self.models.values())


class Context:
    def __init__(self):
        self.metadata = {}
        self.messages = []
    
    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})


class Memory:
    def __init__(self):
        self.data = {}
    
    def store(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def retrieve(self, key: str) -> Any:
        return self.data.get(key)


class State:
    def __init__(self):
        self.state = {"start_time": time.time()}
    
    def set(self, key: str, value: Any) -> None:
        self.state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)


class DualBrain:
    def __init__(self, model_manager, context, memory, state):
        self.model_manager = model_manager
        self.context = context
        self.memory = memory
        self.state = state
        
        # Configuración inicial de pesos
        self.weights = {
            "technical": 0.6,
            "emotional": 0.4
        }
        
        # Estadísticas de procesamiento
        self.stats = {
            "total_requests": 0,
            "average_response_time": 0,
            "requests_per_minute": 0
        }
    
    def process_dual(self, message: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Procesa un mensaje con ambos hemisferios.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Tupla con respuestas (técnica, emocional)
        """
        # Incrementar contador de solicitudes
        self.stats["total_requests"] += 1
        
        # Simular procesamiento técnico
        technical_response = f"Análisis técnico de '{message}'. Puedo ayudarte con información precisa sobre este tema."
        
        # Simular procesamiento emocional
        emotional_response = f"Entiendo cómo te sientes respecto a '{message}'. Estoy aquí para ayudarte."
        
        return technical_response, emotional_response
    
    def combine_responses(self, technical: str, emotional: str, query: str) -> str:
        """
        Combina las respuestas de ambos hemisferios.
        
        Args:
            technical: Respuesta del hemisferio técnico
            emotional: Respuesta del hemisferio emocional
            query: Consulta original
            
        Returns:
            Respuesta combinada
        """
        # Determinar si la consulta es más técnica o emocional
        is_technical_query = any(word in query.lower() for word in ["cómo", "qué", "cuándo", "dónde", "por qué", "código", "programa"])
        is_emotional_query = any(word in query.lower() for word in ["siento", "creo", "pienso", "me gusta", "odio", "amo", "preocupa"])
        
        # Ajustar pesos temporalmente según el tipo de consulta
        temp_weights = dict(self.weights)
        
        if is_technical_query and not is_emotional_query:
            temp_weights["technical"] = min(0.8, temp_weights["technical"] * 1.3)
            temp_weights["emotional"] = 1.0 - temp_weights["technical"]
        elif is_emotional_query and not is_technical_query:
            temp_weights["emotional"] = min(0.8, temp_weights["emotional"] * 1.3)
            temp_weights["technical"] = 1.0 - temp_weights["emotional"]
        
        # Combinar respuestas según los pesos
        if temp_weights["technical"] > 0.7:
            # Principalmente técnica con toque emocional
            combined = f"{technical} {emotional.split('.')[-2] if len(emotional.split('.')) > 1 else emotional}"
        elif temp_weights["emotional"] > 0.7:
            # Principalmente emocional con datos técnicos
            combined = f"{emotional} {technical.split('.')[-2] if len(technical.split('.')) > 1 else technical}"
        else:
            # Equilibrado
            tech_parts = technical.split('.')
            emot_parts = emotional.split('.')
            
            combined = f"{emot_parts[0]}. {tech_parts[0]}. "
            if len(tech_parts) > 1 and len(emot_parts) > 1:
                combined += f"{emot_parts[1]}. {tech_parts[1]}."
        
        return combined
    
    def get_hemisphere_weights(self) -> Dict[str, float]:
        """
        Obtiene los pesos actuales de los hemisferios.
        
        Returns:
            Diccionario con los pesos
        """
        return dict(self.weights)
    
    def set_hemisphere_weights(self, weights: Dict[str, float]) -> bool:
        """
        Establece nuevos pesos para los hemisferios.
        
        Args:
            weights: Diccionario con los nuevos pesos
            
        Returns:
            True si se establecieron correctamente
        """
        if "technical" in weights and "emotional" in weights:
            self.weights["technical"] = weights["technical"]
            self.weights["emotional"] = weights["emotional"]
            return True
        return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de procesamiento.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "totalRequests": self.stats["total_requests"],
            "averageResponseTime": 0.8,  # Valor simulado
            "requestsPerMinute": 2.5     # Valor simulado
        }
