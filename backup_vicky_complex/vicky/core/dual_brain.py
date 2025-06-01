import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimpleHemisphere:
    """
    Implementación simple de un hemisferio cerebral.
    """
    
    def __init__(self, hemisphere_type: str):
        """
        Inicializa el hemisferio.
        
        Args:
            hemisphere_type: Tipo de hemisferio ('technical' o 'emotional')
        """
        self.hemisphere_type = hemisphere_type
        
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una consulta desde la perspectiva del hemisferio.
        
        Args:
            query: Consulta a procesar
            context: Contexto de la consulta
            
        Returns:
            Respuesta del hemisferio
        """
        if self.hemisphere_type == "technical":
            return self._technical_response(query, context)
        else:
            return self._emotional_response(query, context)
    
    def _technical_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera una respuesta técnica."""
        # Respuesta técnica básica
        if "hola" in query.lower():
            response = "Buenas. Soy el componente técnico de Vicky. ¿En qué puedo asistirte técnicamente?"
        elif "cómo estás" in query.lower():
            response = "Estado del sistema: Operativo. Todos los componentes funcionando correctamente."
        elif "backend" in query.lower() or "servidor" in query.lower():
            response = "El backend está funcionando correctamente. Puedo ayudarte con consultas técnicas sobre endpoints, rendimiento y configuración del sistema."
        else:
            response = f"Procesando consulta técnica: '{query}'. Análisis en curso..."
        
        return {
            "response": response,
            "confidence": 0.8,
            "hemisphere": "technical"
        }
    
    def _emotional_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera una respuesta emocional."""
        # Respuesta emocional básica
        if "hola" in query.lower():
            response = "¡Hola! 😊 Me alegra mucho saludarte. Soy el lado emocional de Vicky, aquí para ayudarte con calidez y comprensión."
        elif "cómo estás" in query.lower():
            response = "¡Estoy fantástica! 🌟 Siempre lista para conectar contigo y ayudarte de la mejor manera posible. ¿Cómo estás tú?"
        elif "backend" in query.lower() or "servidor" in query.lower():
            response = "Entiendo que quieres saber sobre el backend. ¡Me emociona poder ayudarte! Es genial poder trabajar juntos en esto."
        else:
            response = f"¡Qué interesante tu consulta! Me emociona poder ayudarte con '{query}'. Siempre es un placer asistirte. 💝"
        
        return {
            "response": response,
            "confidence": 0.8,
            "hemisphere": "emotional"
        }

class DualBrain:
    """
    A dual-hemisphere brain for processing information with both technical and emotional aspects.
    """

    def __init__(self):
        """
        Initializes the DualBrain with default settings.
        """
        self.default_weights = {"technical": 0.5, "emotional": 0.5}
        self.default_combination_strategy = "weighted_average"
        self.state = {}  # To store processing stats
        
        # Inicializar hemisferios
        self.technical_hemisphere = SimpleHemisphere("technical")
        self.emotional_hemisphere = SimpleHemisphere("emotional")

    def set_hemisphere_weights(self, weights: Dict[str, float]) -> bool:
        """
        Establece los pesos para cada hemisferio.
        
        Args:
            weights: Diccionario con pesos para cada hemisferio
            
        Returns:
            True si se establecieron correctamente, False en caso contrario
        """
        try:
            # Validar pesos
            if "technical" not in weights or "emotional" not in weights:
                logger.warning("Pesos de hemisferios incompletos")
                return False
            
            # Normalizar pesos
            total = weights["technical"] + weights["emotional"]
            if total == 0:
                logger.warning("La suma de pesos no puede ser cero")
                return False
            
            normalized_weights = {
                "technical": weights["technical"] / total,
                "emotional": weights["emotional"] / total
            }
            
            # Establecer pesos
            self.default_weights = normalized_weights
            
            logger.info(f"Pesos de hemisferios establecidos: {normalized_weights}")
            return True
        except Exception as e:
            logger.error(f"Error al establecer pesos de hemisferios: {e}")
            return False

    def set_combination_strategy(self, strategy: str) -> bool:
        """
        Establece la estrategia de combinación de respuestas.
        
        Args:
            strategy: Nombre de la estrategia
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            # Validar estrategia
            valid_strategies = [
                "weighted_average", "contextual_selection", "entity_based",
                "sentiment_aligned", "alternating_paragraphs", "hybrid_fusion",
                "query_type_optimized"
            ]
            
            if strategy not in valid_strategies:
                logger.warning(f"Estrategia desconocida: {strategy}")
                return False
            
            # Establecer estrategia
            self.default_combination_strategy = strategy
            
            logger.info(f"Estrategia de combinación establecida: {strategy}")
            return True
        except Exception as e:
            logger.error(f"Error al establecer estrategia de combinación: {e}")
            return False

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de procesamiento del cerebro dual.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            stats = {
                "total_processed": self.state.get("total_processed", 0),
                "avg_processing_time": self.state.get("avg_processing_time", 0.0),
                "technical_usage": self.state.get("technical_usage", 0),
                "emotional_usage": self.state.get("emotional_usage", 0),
                "combination_strategy": self.default_combination_strategy,
                "hemisphere_weights": self.default_weights
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}

    def get_hemisphere_weights(self) -> Dict[str, float]:
        """
        Obtiene los pesos actuales de los hemisferios.
        
        Returns:
            Diccionario con pesos para cada hemisferio
        """
        return dict(self.default_weights)
