"""
Sistema de Combinación de Hemisferios
-------------------------------------

Este módulo implementa un sistema flexible para combinar las respuestas
de los hemisferios técnico y emocional, permitiendo ajustar la estrategia
de combinación según el contexto, tipo de consulta y preferencias del usuario.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from src.vicky.core.context import Context
from src.vicky.utils.performance_metrics import track_performance
from src.vicky.core.entity_types import Entity
from src.vicky.core.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)

class CombinationStrategy(Enum):
    """Estrategias disponibles para combinar respuestas de hemisferios."""
    WEIGHTED_AVERAGE = "weighted_average"
    CONTEXTUAL_SELECTION = "contextual_selection"
    ENTITY_BASED = "entity_based"
    SENTIMENT_ALIGNED = "sentiment_aligned"
    ALTERNATING_PARAGRAPHS = "alternating_paragraphs"
    HYBRID_FUSION = "hybrid_fusion"
    QUERY_TYPE_OPTIMIZED = "query_type_optimized"


class HemisphereCombiner:
    """
    Clase principal para combinar respuestas de los hemisferios técnico y emocional.
    
    Esta clase proporciona múltiples estrategias para combinar las respuestas
    y selecciona la más adecuada según el contexto y configuración.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el combinador de hemisferios con la configuración proporcionada.
        
        Args:
            config: Diccionario con la configuración del combinador
        """
        self.config = config
        self.default_strategy = CombinationStrategy(
            config.get("default_strategy", "weighted_average")
        )
        self.strategy_weights = config.get("strategy_weights", {
            "technical": 0.6,
            "emotional": 0.4
        })
        
        # Inicializar extractor de entidades
        self.entity_extractor = EntityExtractor()
        
        # Mapeo de estrategias a sus funciones de implementación
        self.strategy_map = {
            CombinationStrategy.WEIGHTED_AVERAGE: self._weighted_average_strategy,
            CombinationStrategy.CONTEXTUAL_SELECTION: self._contextual_selection_strategy,
            CombinationStrategy.ENTITY_BASED: self._entity_based_strategy,
            CombinationStrategy.SENTIMENT_ALIGNED: self._sentiment_aligned_strategy,
            CombinationStrategy.ALTERNATING_PARAGRAPHS: self._alternating_paragraphs_strategy,
            CombinationStrategy.HYBRID_FUSION: self._hybrid_fusion_strategy,
            CombinationStrategy.QUERY_TYPE_OPTIMIZED: self._query_type_optimized_strategy,
        }
        
        # Configuración para estrategias específicas
        self.query_type_config = config.get("query_type_config", {
            "technical": ["code", "data", "analysis", "how_to"],
            "emotional": ["creative", "personal", "opinion", "advice"],
            "balanced": ["general", "conversation", "explanation"]
        })
        
        logger.info(f"HemisphereCombiner inicializado con estrategia por defecto: {self.default_strategy.value}")
    
    def combine(self, 
                technical_response: str, 
                emotional_response: str, 
                context: Context,
                strategy: Optional[CombinationStrategy] = None) -> str:
        """
        Combina las respuestas de los hemisferios técnico y emocional.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            strategy: Estrategia de combinación a utilizar (opcional)
            
        Returns:
            Respuesta combinada
        """
        if not strategy:
            strategy = self._determine_best_strategy(context, technical_response, emotional_response)
        
        logger.debug(f"Usando estrategia de combinación: {strategy.value}")
        
        # Obtener la función de estrategia correspondiente
        strategy_func = self.strategy_map.get(strategy, self.strategy_map[self.default_strategy])
        
        # Aplicar la estrategia seleccionada
        combined_response = strategy_func(technical_response, emotional_response, context)
        
        # Registrar métricas sobre la combinación
        self._log_combination_metrics(technical_response, emotional_response, combined_response, strategy)
        
        return combined_response
    
    def _determine_best_strategy(self, 
                               context: Context, 
                               technical_response: str, 
                               emotional_response: str) -> CombinationStrategy:
        """
        Determina la mejor estrategia de combinación basada en el contexto.
        
        Args:
            context: Contexto de la consulta
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            
        Returns:
            Estrategia de combinación óptima
        """
        query_type = context.get("query_type", "general")
        user_preferences = context.get("user_preferences", {})
        
        # Verificar si hay una preferencia explícita del usuario
        if "combination_strategy" in user_preferences:
            strategy_name = user_preferences["combination_strategy"]
            try:
                return CombinationStrategy(strategy_name)
            except ValueError:
                logger.warning(f"Estrategia desconocida: {strategy_name}, usando la predeterminada")
        
        # Determinar por tipo de consulta
        if query_type in self.query_type_config["technical"]:
            return CombinationStrategy.WEIGHTED_AVERAGE  # Favorece técnico
        elif query_type in self.query_type_config["emotional"]:
            return CombinationStrategy.SENTIMENT_ALIGNED  # Favorece emocional
        elif "code" in context.get("entities", []) or "data" in context.get("entities", []):
            return CombinationStrategy.ENTITY_BASED
        elif len(technical_response) > 500 and len(emotional_response) > 500:
            return CombinationStrategy.ALTERNATING_PARAGRAPHS
        
        # Por defecto, usar la estrategia híbrida para consultas generales
        return CombinationStrategy.HYBRID_FUSION
    
    def _weighted_average_strategy(self, 
                                 technical_response: str, 
                                 emotional_response: str, 
                                 context: Context) -> str:
        """
        Combina respuestas usando ponderación configurable.
        
        Esta estrategia es útil cuando queremos dar más peso a uno de los hemisferios
        según el tipo de consulta o preferencias del usuario.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta combinada con ponderación
        """
        # Ajustar pesos según el contexto si es necesario
        weights = dict(self.strategy_weights)
        query_type = context.get("query_type", "general")
        
        if query_type in self.query_type_config["technical"]:
            weights["technical"] = min(weights["technical"] * 1.5, 0.9)
            weights["emotional"] = 1.0 - weights["technical"]
        elif query_type in self.query_type_config["emotional"]:
            weights["emotional"] = min(weights["emotional"] * 1.5, 0.9)
            weights["technical"] = 1.0 - weights["emotional"]
        
        # Dividir en párrafos para mejor combinación
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Asegurar que tenemos suficientes párrafos para combinar
        max_paragraphs = max(len(tech_paragraphs), len(emot_paragraphs))
        tech_paragraphs = self._normalize_paragraphs(tech_paragraphs, max_paragraphs)
        emot_paragraphs = self._normalize_paragraphs(emot_paragraphs, max_paragraphs)
        
        # Combinar párrafos con ponderación
        combined_paragraphs = []
        for i in range(max_paragraphs):
            if random.random() < weights["technical"]:
                combined_paragraphs.append(tech_paragraphs[i])
            else:
                combined_paragraphs.append(emot_paragraphs[i])
        
        return '\n\n'.join(combined_paragraphs)
    
    def _contextual_selection_strategy(self, 
                                     technical_response: str, 
                                     emotional_response: str, 
                                     context: Context) -> str:
        """
        Selecciona partes de cada respuesta según el contexto.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta combinada contextualmente
        """
        # Extraer entidades y temas clave del contexto
        entities = context.get("entities", [])
        query = context.get("query", "")
        
        # Dividir en párrafos
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Seleccionar párrafos relevantes de cada respuesta
        selected_paragraphs = []
        
        # Introducción - preferir emocional para engagement
        selected_paragraphs.append(emot_paragraphs[0] if emot_paragraphs else "")
        
        # Contenido principal - seleccionar según relevancia
        tech_relevance = self._calculate_relevance(tech_paragraphs[1:], query, entities)
        emot_relevance = self._calculate_relevance(emot_paragraphs[1:], query, entities)
        
        # Combinar los párrafos más relevantes
        for i in range(1, min(len(tech_paragraphs), len(emot_paragraphs))):
            if i < len(tech_relevance) and i < len(emot_relevance):
                if tech_relevance[i-1] > emot_relevance[i-1]:
                    selected_paragraphs.append(tech_paragraphs[i])
                else:
                    selected_paragraphs.append(emot_paragraphs[i])
        
        # Conclusión - preferir técnico para precisión
        if len(tech_paragraphs) > 2:
            selected_paragraphs.append(tech_paragraphs[-1])
        
        return '\n\n'.join(selected_paragraphs)
    
    def _entity_based_strategy(self, 
                             technical_response: str, 
                             emotional_response: str, 
                             context: Context) -> str:
        """
        Combina respuestas basándose en las entidades detectadas.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta combinada basada en entidades
        """
        # Extraer entidades de ambas respuestas
        tech_entities = self.entity_extractor.extract_entities(technical_response)
        emot_entities = self.entity_extractor.extract_entities(emotional_response)
        
        # Identificar entidades técnicas vs. emocionales
        technical_entity_types = ["CODE", "DATA", "TECHNICAL_TERM", "MEASUREMENT"]
        emotional_entity_types = ["PERSON", "ORGANIZATION", "CREATIVE_WORK", "EMOTION"]
        
        # Dividir en párrafos
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Combinar basado en la densidad de entidades relevantes
        combined_paragraphs = []
        
        # Siempre comenzar con una introducción emocional para engagement
        combined_paragraphs.append(emot_paragraphs[0] if emot_paragraphs else "")
        
        # Para cada párrafo, elegir la versión con más entidades relevantes al contexto
        for i in range(1, min(len(tech_paragraphs), len(emot_paragraphs))):
            tech_paragraph = tech_paragraphs[i]
            emot_paragraph = emot_paragraphs[i]
            
            # Contar entidades relevantes en cada párrafo
            tech_count = sum(1 for e in tech_entities if e.text in tech_paragraph and e.type in technical_entity_types)
            emot_count = sum(1 for e in emot_entities if e.text in emot_paragraph and e.type in emotional_entity_types)
            
            # Seleccionar el párrafo con más entidades relevantes
            if tech_count > emot_count:
                combined_paragraphs.append(tech_paragraph)
            else:
                combined_paragraphs.append(emot_paragraph)
        
        # Asegurar que tenemos una conclusión técnica para precisión
        if len(tech_paragraphs) > 2:
            combined_paragraphs.append(tech_paragraphs[-1])
        
        return '\n\n'.join(combined_paragraphs)
    
    def _sentiment_aligned_strategy(self, 
                                  technical_response: str, 
                                  emotional_response: str, 
                                  context: Context) -> str:
        """
        Combina respuestas alineando el sentimiento con el contexto.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta combinada con sentimiento alineado
        """
        # Obtener el sentimiento del contexto
        sentiment = context.get("sentiment", "neutral")
        
        # Dividir en párrafos
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Normalizar longitudes
        max_paragraphs = max(len(tech_paragraphs), len(emot_paragraphs))
        tech_paragraphs = self._normalize_paragraphs(tech_paragraphs, max_paragraphs)
        emot_paragraphs = self._normalize_paragraphs(emot_paragraphs, max_paragraphs)
        
        # Combinar según el sentimiento
        combined_paragraphs = []
        
        # Introducción emocional para engagement
        combined_paragraphs.append(emot_paragraphs[0])
        
        # Contenido principal - ajustar según sentimiento
        if sentiment in ["positive", "excited", "curious"]:
            # Para sentimientos positivos, favorecer el hemisferio emocional
            ratio = 0.7  # 70% emocional, 30% técnico
        elif sentiment in ["negative", "confused", "frustrated"]:
            # Para sentimientos negativos, favorecer el hemisferio técnico (más preciso)
            ratio = 0.3  # 30% emocional, 70% técnico
        else:
            # Para sentimiento neutral, equilibrar
            ratio = 0.5
        
        # Aplicar ratio para selección de párrafos
        for i in range(1, max_paragraphs - 1):
            if random.random() < ratio:
                combined_paragraphs.append(emot_paragraphs[i])
            else:
                combined_paragraphs.append(tech_paragraphs[i])
        
        # Conclusión técnica para precisión
        combined_paragraphs.append(tech_paragraphs[-1])
        
        return '\n\n'.join(combined_paragraphs)
    
    def _alternating_paragraphs_strategy(self, 
                                       technical_response: str, 
                                       emotional_response: str, 
                                       context: Context) -> str:
        """
        Alterna párrafos de ambas respuestas.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta con párrafos alternados
        """
        # Dividir en párrafos
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Determinar cuál hemisferio debe comenzar según el contexto
        query_type = context.get("query_type", "general")
        start_with_emotional = query_type in self.query_type_config["emotional"]
        
        # Alternar párrafos
        combined_paragraphs = []
        max_paragraphs = max(len(tech_paragraphs), len(emot_paragraphs))
        
        for i in range(max_paragraphs):
            if i % 2 == (0 if start_with_emotional else 1):
                # Párrafo emocional
                if i < len(emot_paragraphs):
                    combined_paragraphs.append(emot_paragraphs[i])
            else:
                # Párrafo técnico
                if i < len(tech_paragraphs):
                    combined_paragraphs.append(tech_paragraphs[i])
        
        return '\n\n'.join(combined_paragraphs)
    
    def _hybrid_fusion_strategy(self, 
                              technical_response: str, 
                              emotional_response: str, 
                              context: Context) -> str:
        """
        Fusiona elementos de ambas respuestas en cada párrafo.
        
        Esta es la estrategia más sofisticada que intenta crear una
        respuesta coherente tomando lo mejor de ambos hemisferios.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta fusionada híbrida
        """
        # Dividir en párrafos
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Normalizar longitudes
        max_paragraphs = max(len(tech_paragraphs), len(emot_paragraphs))
        tech_paragraphs = self._normalize_paragraphs(tech_paragraphs, max_paragraphs)
        emot_paragraphs = self._normalize_paragraphs(emot_paragraphs, max_paragraphs)
        
        # Fusionar párrafos
        combined_paragraphs = []
        
        # Introducción - usar emocional para engagement
        combined_paragraphs.append(emot_paragraphs[0])
        
        # Contenido principal - fusionar información
        for i in range(1, max_paragraphs - 1):
            # Extraer información clave de cada párrafo
            tech_info = self._extract_key_information(tech_paragraphs[i])
            emot_info = self._extract_key_information(emot_paragraphs[i])
            
            # Crear un párrafo fusionado
            if i % 2 == 0:
                # Comenzar con técnico, terminar con emocional
                fused = f"{tech_info} {emot_info}"
            else:
                # Comenzar con emocional, reforzar con técnico
                fused = f"{emot_info} {tech_info}"
            
            combined_paragraphs.append(fused)
        
        # Conclusión - combinar precisión técnica con tono emocional
        if len(tech_paragraphs) > 1 and len(emot_paragraphs) > 1:
            tech_conclusion = tech_paragraphs[-1]
            emot_tone = self._extract_emotional_tone(emot_paragraphs[-1])
            
            combined_conclusion = f"{tech_conclusion} {emot_tone}"
            combined_paragraphs.append(combined_conclusion)
        
        return '\n\n'.join(combined_paragraphs)
    
    def _query_type_optimized_strategy(self, 
                                     technical_response: str, 
                                     emotional_response: str, 
                                     context: Context) -> str:
        """
        Optimiza la combinación según el tipo específico de consulta.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            context: Contexto de la consulta
            
        Returns:
            Respuesta optimizada para el tipo de consulta
        """
        query_type = context.get("query_type", "general")
        
        # Estrategias específicas por tipo de consulta
        if query_type == "code":
            # Para código, usar principalmente técnico con introducción emocional
            return self._combine_with_ratio(technical_response, emotional_response, 0.9, intro_emotional=True)
        
        elif query_type == "creative":
            # Para creatividad, usar principalmente emocional con datos técnicos
            return self._combine_with_ratio(technical_response, emotional_response, 0.2, intro_emotional=True)
        
        elif query_type == "explanation":
            # Para explicaciones, alternar párrafos
            return self._alternating_paragraphs_strategy(technical_response, emotional_response, context)
        
        elif query_type == "how_to":
            # Para tutoriales, técnico con tono emocional
            return self._combine_with_ratio(technical_response, emotional_response, 0.7, intro_emotional=True)
        
        elif query_type == "opinion":
            # Para opiniones, principalmente emocional con datos técnicos
            return self._combine_with_ratio(technical_response, emotional_response, 0.3, intro_emotional=True)
        
        # Por defecto, usar estrategia híbrida
        return self._hybrid_fusion_strategy(technical_response, emotional_response, context)
    
    def _combine_with_ratio(self, 
                          technical_response: str, 
                          emotional_response: str, 
                          tech_ratio: float,
                          intro_emotional: bool = False) -> str:
        """
        Combina respuestas con un ratio específico.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            tech_ratio: Proporción de contenido técnico (0.0-1.0)
            intro_emotional: Si se debe usar introducción emocional
            
        Returns:
            Respuesta combinada con el ratio especificado
        """
        import random
        
        # Dividir en párrafos
        tech_paragraphs = technical_response.split('\n\n')
        emot_paragraphs = emotional_response.split('\n\n')
        
        # Normalizar longitudes
        max_paragraphs = max(len(tech_paragraphs), len(emot_paragraphs))
        tech_paragraphs = self._normalize_paragraphs(tech_paragraphs, max_paragraphs)
        emot_paragraphs = self._normalize_paragraphs(emot_paragraphs, max_paragraphs)
        
        # Combinar según ratio
        combined_paragraphs = []
        
        # Introducción
        if intro_emotional and emot_paragraphs:
            combined_paragraphs.append(emot_paragraphs[0])
        else:
            combined_paragraphs.append(tech_paragraphs[0])
        
        # Contenido principal
        for i in range(1, max_paragraphs - 1):
            if random.random() < tech_ratio:
                combined_paragraphs.append(tech_paragraphs[i])
            else:
                combined_paragraphs.append(emot_paragraphs[i])
        
        # Conclusión
        if tech_ratio > 0.5:
            combined_paragraphs.append(tech_paragraphs[-1])
        else:
            combined_paragraphs.append(emot_paragraphs[-1])
        
        return '\n\n'.join(combined_paragraphs)
    
    def _normalize_paragraphs(self, paragraphs: List[str], target_length: int) -> List[str]:
        """
        Normaliza la lista de párrafos a la longitud objetivo.
        
        Args:
            paragraphs: Lista de párrafos
            target_length: Longitud objetivo
            
        Returns:
            Lista normalizada de párrafos
        """
        if len(paragraphs) == 0:
            return [""] * target_length
        
        if len(paragraphs) >= target_length:
            return paragraphs[:target_length]
        
        # Extender la lista repitiendo los últimos párrafos
        extended = paragraphs.copy()
        while len(extended) < target_length:
            extended.append(paragraphs[-1])
        
        return extended
    
    def _calculate_relevance(self, paragraphs: List[str], query: str, entities: List[str]) -> List[float]:
        """
        Calcula la relevancia de cada párrafo respecto a la consulta y entidades.
        
        Args:
            paragraphs: Lista de párrafos
            query: Consulta original
            entities: Entidades detectadas
            
        Returns:
            Lista de puntuaciones de relevancia
        """
        relevance_scores = []
        
        for paragraph in paragraphs:
            # Calcular relevancia basada en coincidencia de palabras clave
            query_words = set(query.lower().split())
            paragraph_words = set(paragraph.lower().split())
            
            # Intersección de palabras
            common_words = query_words.intersection(paragraph_words)
            word_score = len(common_words) / max(len(query_words), 1)
            
            # Relevancia de entidades
            entity_score = 0
            for entity in entities:
                if entity.lower() in paragraph.lower():
                    entity_score += 1
            entity_score = entity_score / max(len(entities), 1)
            
            # Combinar puntuaciones
            combined_score = 0.7 * word_score + 0.3 * entity_score
            relevance_scores.append(combined_score)
        
        return relevance_scores
    
    def _extract_key_information(self, paragraph: str) -> str:
        """
        Extrae información clave de un párrafo.
        
        Args:
            paragraph: Párrafo de texto
            
        Returns:
            Información clave extraída
        """
        # Implementación simple - en producción podría usar NLP más avanzado
        sentences = paragraph.split('. ')
        
        if len(sentences) <= 2:
            return paragraph
        
        # Extraer primera y última oración (suelen contener información clave)
        key_info = f"{sentences[0]}. {sentences[-1]}"
        
        return key_info
    
    def _extract_emotional_tone(self, paragraph: str) -> str:
        """
        Extrae el tono emocional de un párrafo.
        
        Args:
            paragraph: Párrafo de texto
            
        Returns:
            Frase con tono emocional
        """
        # Implementación simple - en producción podría usar análisis de sentimiento
        sentences = paragraph.split('. ')
        
        # Buscar frases con palabras emocionales
        emotional_words = ["importante", "emocionante", "interesante", "valioso", 
                          "fascinante", "útil", "esencial", "recomendable"]
        
        for sentence in sentences:
            for word in emotional_words:
                if word in sentence.lower():
                    return sentence
        
        # Si no encuentra, devolver la última oración
        return sentences[-1] if sentences else ""
    
    def _log_combination_metrics(self, 
                               technical_response: str, 
                               emotional_response: str, 
                               combined_response: str,
                               strategy: CombinationStrategy) -> None:
        """
        Registra métricas sobre el proceso de combinación.
        
        Args:
            technical_response: Respuesta del hemisferio técnico
            emotional_response: Respuesta del hemisferio emocional
            combined_response: Respuesta combinada
            strategy: Estrategia utilizada
        """
        # Calcular longitudes
        tech_length = len(technical_response)
        emot_length = len(emotional_response)
        combined_length = len(combined_response)
        
        # Calcular proporción de contenido
        tech_ratio = tech_length / max(tech_length + emot_length, 1)
        emot_ratio = emot_length / max(tech_length + emot_length, 1)
        
        # Registrar métricas
        logger.info(f"Métricas de combinación - Estrategia: {strategy.value}")
        logger.info(f"Longitud técnica: {tech_length}, Longitud emocional: {emot_length}, Longitud combinada: {combined_length}")
        logger.info(f"Ratio técnico: {tech_ratio:.2f}, Ratio emocional: {emot_ratio:.2f}")
        
        # Aquí se podrían registrar métricas adicionales en un sistema de monitoreo
