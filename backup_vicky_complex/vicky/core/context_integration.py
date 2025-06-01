"""
Integración de Evaluación de Contexto con DualBrain
--------------------------------------------------

Este módulo implementa la integración entre los algoritmos de evaluación
de contexto y el Motor Dual-Hemisferio (DualBrain), permitiendo que las
respuestas generadas sean contextualmente coherentes y relevantes.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
import json

# Importaciones internas
from .context import Context
from .memory import Memory
from .dual_brain import DualBrain
from .context_evaluation import ContextEvaluator
from .semantic_context_analyzer import SemanticContextAnalyzer

# Configurar logger
logger = logging.getLogger("vicky.context_integration")

class ContextualDualBrain:
    """
    Integración del Motor Dual-Hemisferio con evaluación de contexto.
    
    Esta clase extiende las capacidades del DualBrain para:
    1. Incorporar análisis contextual en el procesamiento
    2. Ajustar pesos de hemisferios basados en contexto
    3. Mantener coherencia conversacional
    4. Adaptar estrategias de respuesta según el contexto
    5. Mejorar la relevancia de las respuestas
    """
    
    def __init__(self, dual_brain: DualBrain, context: Context, memory: Memory):
        """
        Inicializa la integración contextual.
        
        Args:
            dual_brain: Instancia del Motor Dual-Hemisferio
            context: Sistema de contexto conversacional
            memory: Sistema de memoria
        """
        self.dual_brain = dual_brain
        self.context = context
        self.memory = memory
        
        # Inicializar evaluadores de contexto
        self.context_evaluator = ContextEvaluator(memory)
        
        # Intentar inicializar analizador semántico si hay modelo de embeddings
        self.semantic_analyzer = None
        try:
            embedding_model = self.dual_brain.model_manager.get_model("embedding")
            if embedding_model:
                self.semantic_analyzer = SemanticContextAnalyzer(embedding_model, memory)
                logger.info("Analizador semántico inicializado correctamente")
        except Exception as e:
            logger.warning(f"No se pudo inicializar analizador semántico: {e}")
        
        # Configuración
        self.context_weight = 0.3  # Peso del contexto en la generación
        self.coherence_threshold = 0.6  # Umbral para mantener coherencia
        
        logger.info("Integración contextual con DualBrain inicializada")
    
    def process_message(self, message: str) -> str:
        """
        Procesa un mensaje con conciencia contextual.
        
        Args:
            message: Mensaje a procesar
            
        Returns:
            Respuesta generada
        """
        start_time = time.time()
        
        try:
            # Evaluar contexto
            context_evaluation = self.context_evaluator.evaluate_context(
                self.context, message
            )
            
            # Realizar análisis semántico si está disponible
            semantic_analysis = None
            if self.semantic_analyzer:
                semantic_analysis = self.semantic_analyzer.analyze(
                    self.context, message
                )
            
            # Preparar contexto enriquecido para DualBrain
            enriched_context = self._prepare_enriched_context(
                message, context_evaluation, semantic_analysis
            )
            
            # Ajustar pesos de hemisferios basados en contexto
            hemisphere_weights = self._adjust_hemisphere_weights(
                message, context_evaluation, semantic_analysis
            )
            
            # Seleccionar estrategia de combinación basada en contexto
            combination_strategy = self._select_combination_strategy(
                message, context_evaluation, semantic_analysis
            )
            
            # Configurar DualBrain con ajustes contextuales
            self.dual_brain.set_hemisphere_weights(hemisphere_weights)
            self.dual_brain.set_combination_strategy(combination_strategy)
            
            # Procesar mensaje con DualBrain
            response = self.dual_brain.process_message(message, enriched_context)
            
            # Verificar coherencia de la respuesta
            if context_evaluation.context_coherence > self.coherence_threshold:
                response = self._ensure_coherence(
                    response, message, context_evaluation
                )
            
            # Actualizar contexto con la nueva interacción
            self.context.add_message("user", message)
            self.context.add_message("assistant", response)
            
            # Registrar estadísticas
            processing_time = time.time() - start_time
            self._log_processing_stats(
                message, response, context_evaluation, 
                semantic_analysis, processing_time
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error en procesamiento contextual: {e}")
            
            # Fallback a procesamiento simple
            try:
                response = self.dual_brain.process_message(message)
                
                # Actualizar contexto incluso en caso de error
                self.context.add_message("user", message)
                self.context.add_message("assistant", response)
                
                return response
            except Exception as fallback_error:
                logger.error(f"Error en fallback: {fallback_error}")
                return "Lo siento, ocurrió un error al procesar tu mensaje."
    
    def _prepare_enriched_context(self, message: str, 
                                 context_evaluation, 
                                 semantic_analysis) -> Dict[str, Any]:
        """
        Prepara un contexto enriquecido para DualBrain.
        
        Args:
            message: Mensaje a procesar
            context_evaluation: Resultado de evaluación de contexto
            semantic_analysis: Resultado de análisis semántico
            
        Returns:
            Diccionario con contexto enriquecido
        """
        # Contexto base
        enriched_context = {
            "conversation_history": self.context.get_history(),
            "message": message
        }
        
        # Añadir información de evaluación de contexto
        if context_evaluation:
            enriched_context.update({
                "active_topics": context_evaluation.active_topics,
                "relevant_entities": [
                    {
                        "name": entity.name,
                        "type": entity.type,
                        "relevance": entity.relevance
                    }
                    for entity in context_evaluation.relevant_entities[:5]
                ],
                "context_coherence": context_evaluation.context_coherence,
                "topic_shift": context_evaluation.topic_shift_detected,
                "context_summary": context_evaluation.context_summary
            })
        
        # Añadir información de análisis semántico
        if semantic_analysis:
            enriched_context.update({
                "semantic_clusters": semantic_analysis.concept_clusters,
                "key_concepts": semantic_analysis.key_concepts,
                "semantic_coherence": semantic_analysis.topic_coherence,
                "semantic_shift": semantic_analysis.semantic_shift
            })
        
        # Añadir metadatos del contexto
        enriched_context.update(self.context.metadata)
        
        return enriched_context
    
    def _adjust_hemisphere_weights(self, message: str,
                                  context_evaluation,
                                  semantic_analysis) -> Dict[str, float]:
        """
        Ajusta los pesos de los hemisferios basados en contexto.
        
        Args:
            message: Mensaje a procesar
            context_evaluation: Resultado de evaluación de contexto
            semantic_analysis: Resultado de análisis semántico
            
        Returns:
            Diccionario con pesos ajustados
        """
        # Pesos base
        weights = {
            "technical": 0.5,
            "emotional": 0.5
        }
        
        # Ajustar según evaluación de contexto
        if context_evaluation:
            # Si hay un cambio de tema, favorecer hemisferio emocional
            if context_evaluation.topic_shift_detected:
                weights["emotional"] += 0.1
                weights["technical"] -= 0.1
            
            # Si hay baja coherencia, favorecer hemisferio técnico
            if context_evaluation.context_coherence < 0.4:
                weights["technical"] += 0.1
                weights["emotional"] -= 0.1
            
            # Ajustar según entidades relevantes
            for entity in context_evaluation.relevant_entities[:3]:
                if entity.type in ["technology", "code", "system"]:
                    weights["technical"] += 0.05
                    weights["emotional"] -= 0.05
                elif entity.type in ["person", "emotion", "experience"]:
                    weights["emotional"] += 0.05
                    weights["technical"] -= 0.05
        
        # Ajustar según análisis semántico
        if semantic_analysis:
            # Si hay alto cambio semántico, favorecer hemisferio emocional
            if semantic_analysis.semantic_shift > 0.7:
                weights["emotional"] += 0.1
                weights["technical"] -= 0.1
            
            # Si hay alta coherencia semántica, equilibrar hemisferios
            if semantic_analysis.topic_coherence > 0.8:
                weights["technical"] = max(0.4, min(0.6, weights["technical"]))
                weights["emotional"] = 1.0 - weights["technical"]
        
        # Normalizar pesos
        total = weights["technical"] + weights["emotional"]
        weights["technical"] /= total
        weights["emotional"] /= total
        
        # Limitar rango (0.2-0.8)
        weights["technical"] = max(0.2, min(0.8, weights["technical"]))
        weights["emotional"] = 1.0 - weights["technical"]
        
        return weights
    
    def _select_combination_strategy(self, message: str,
                                    context_evaluation,
                                    semantic_analysis) -> str:
        """
        Selecciona la estrategia de combinación basada en contexto.
        
        Args:
            message: Mensaje a procesar
            context_evaluation: Resultado de evaluación de contexto
            semantic_analysis: Resultado de análisis semántico
            
        Returns:
            Nombre de la estrategia de combinación
        """
        # Estrategia por defecto
        strategy = "integrated"
        
        # Ajustar según evaluación de contexto
        if context_evaluation:
            # Si hay un cambio de tema, usar estrategia emocional primero
            if context_evaluation.topic_shift_detected:
                strategy = "emotional_first"
            
            # Si hay alta coherencia, usar estrategia integrada
            elif context_evaluation.context_coherence > 0.7:
                strategy = "integrated"
            
            # Si hay referencias técnicas claras, usar técnica primero
            elif any(e.type in ["technology", "code", "system"] 
                    for e in context_evaluation.relevant_entities[:2]):
                strategy = "technical_first"
        
        # Ajustar según análisis semántico
        if semantic_analysis:
            # Si
