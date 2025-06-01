"""
Módulo de Evaluación de Contexto para VokaFlow
----------------------------------------------

Este módulo implementa algoritmos avanzados para la evaluación y gestión
del contexto conversacional, permitiendo a Vicky mantener conversaciones
coherentes, relevantes y con memoria contextual.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
import re
import numpy as np
from collections import Counter, defaultdict
import traceback

# Importaciones internas
from .context import Context
from .memory import Memory
from ..models.embedding_model import EmbeddingModel

# Configurar logger
logger = logging.getLogger("vicky.context_evaluation")

@dataclass
class ContextualEntity:
    """Entidad identificada en el contexto conversacional."""
    name: str
    type: str
    relevance: float  # 0.0 a 1.0
    first_mention_index: int
    last_mention_index: int
    mention_count: int = 1
    attributes: Dict[str, Any] = field(default_factory=dict)
    related_entities: List[str] = field(default_factory=list)
    
    def update_mention(self, message_index: int) -> None:
        """Actualiza información de mención de la entidad."""
        self.last_mention_index = message_index
        self.mention_count += 1
        
    def calculate_recency(self, current_index: int) -> float:
        """Calcula qué tan reciente es la entidad (0.0-1.0)."""
        if current_index == self.last_mention_index:
            return 1.0
        
        # Decaimiento exponencial basado en la distancia
        distance = current_index - self.last_mention_index
        return max(0.0, min(1.0, np.exp(-0.5 * distance)))
    
    def calculate_importance(self, current_index: int) -> float:
        """Calcula la importancia general de la entidad."""
        recency = self.calculate_recency(current_index)
        frequency = min(1.0, self.mention_count / 5.0)  # Normalizado a máximo 5 menciones
        
        # Combinar factores (recency tiene más peso)
        return 0.6 * recency + 0.3 * frequency + 0.1 * self.relevance


@dataclass
class ConversationSegment:
    """Segmento temático de una conversación."""
    start_index: int
    end_index: int
    main_topic: str
    subtopics: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    coherence_score: float = 0.0  # 0.0 a 1.0
    importance_score: float = 0.0  # 0.0 a 1.0
    
    def contains_index(self, index: int) -> bool:
        """Verifica si el segmento contiene un índice de mensaje."""
        return self.start_index <= index <= self.end_index
    
    def get_length(self) -> int:
        """Obtiene la longitud del segmento en número de mensajes."""
        return self.end_index - self.start_index + 1


@dataclass
class ContextEvaluationResult:
    """Resultado de la evaluación de contexto."""
    relevant_entities: List[ContextualEntity]
    active_topics: List[str]
    conversation_segments: List[ConversationSegment]
    context_coherence: float  # 0.0 a 1.0
    topic_shift_detected: bool
    reference_resolution: Dict[str, str]  # Mapeo de referencias a entidades
    context_summary: str
    evaluation_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a un diccionario."""
        return {
            "relevant_entities": [
                {
                    "name": e.name,
                    "type": e.type,
                    "relevance": e.relevance,
                    "mention_count": e.mention_count,
                    "importance": e.calculate_importance(0)  # Valor actual
                } for e in self.relevant_entities
            ],
            "active_topics": self.active_topics,
            "segments_count": len(self.conversation_segments),
            "context_coherence": self.context_coherence,
            "topic_shift_detected": self.topic_shift_detected,
            "references_resolved": len(self.reference_resolution),
            "context_summary": self.context_summary,
            "evaluation_time": self.evaluation_time
        }


class ContextEvaluator:
    """
    Evaluador avanzado de contexto conversacional.
    
    Esta clase implementa algoritmos para:
    1. Identificar y rastrear entidades mencionadas en la conversación
    2. Detectar temas y subtemas activos
    3. Segmentar la conversación en bloques temáticos
    4. Evaluar la coherencia contextual
    5. Resolver referencias anafóricas (pronombres, etc.)
    6. Generar resúmenes contextuales
    """
    
    def __init__(self, memory: Memory, embedding_model: Optional[EmbeddingModel] = None):
        """
        Inicializa el evaluador de contexto.
        
        Args:
            memory: Sistema de memoria para almacenar información contextual
            embedding_model: Modelo de embeddings para análisis semántico (opcional)
        """
        self.memory = memory
        self.embedding_model = embedding_model
        
        # Entidades y temas identificados
        self.entities: Dict[str, ContextualEntity] = {}
        self.topics: Dict[str, float] = {}  # Tema -> relevancia
        self.segments: List[ConversationSegment] = []
        
        # Configuración
        self.max_entities = 50
        self.max_topics = 10
        self.max_segments = 5
        self.recency_decay_factor = 0.8  # Factor de decaimiento por antigüedad
        self.topic_shift_threshold = 0.6  # Umbral para detectar cambio de tema
        
        # Patrones para detección de referencias
        self._init_reference_patterns()
        
        logger.info("Evaluador de contexto inicializado")
    
    def _init_reference_patterns(self):
        """Inicializa patrones para detección de referencias."""
        # Patrones para pronombres y referencias
        self.reference_patterns = {
            "pronombres_personales": re.compile(r'\b(él|ella|ellos|ellas|lo|la|le|les|se)\b', re.IGNORECASE),
            "pronombres_demostrativos": re.compile(r'\b(este|esta|estos|estas|eso|esa|esos|esas|aquello|aquella|aquellos|aquellas)\b', re.IGNORECASE),
            "referencias_temporales": re.compile(r'\b(antes|después|luego|anteriormente|previamente|posteriormente)\b', re.IGNORECASE),
            "referencias_espaciales": re.compile(r'\b(aquí|allí|ahí|arriba|abajo|dentro|fuera)\b', re.IGNORECASE)
        }
    
    def evaluate_context(self, context: Context, current_message: str) -> ContextEvaluationResult:
        """
        Evalúa el contexto conversacional actual.
        
        Args:
            context: Contexto de la conversación
            current_message: Mensaje actual a evaluar
            
        Returns:
            Resultado de la evaluación de contexto
        """
        start_time = time.time()
        
        try:
            # Obtener historial de conversación
            history = context.get_history()
            
            # Actualizar entidades y temas
            self._update_entities_and_topics(history, current_message)
            
            # Segmentar conversación
            self._segment_conversation(history, current_message)
            
            # Evaluar coherencia contextual
            coherence = self._evaluate_coherence(history, current_message)
            
            # Detectar cambio de tema
            topic_shift = self._detect_topic_shift(history, current_message)
            
            # Resolver referencias
            references = self._resolve_references(history, current_message)
            
            # Generar resumen contextual
            summary = self._generate_context_summary(history, current_message)
            
            # Obtener entidades relevantes ordenadas por importancia
            current_index = len(history)
            relevant_entities = sorted(
                self.entities.values(),
                key=lambda e: e.calculate_importance(current_index),
                reverse=True
            )[:10]  # Limitar a 10 entidades más relevantes
            
            # Obtener temas activos ordenados por relevancia
            active_topics = sorted(
                self.topics.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Limitar a 5 temas más relevantes
            
            # Crear resultado
            result = ContextEvaluationResult(
                relevant_entities=relevant_entities,
                active_topics=[topic for topic, _ in active_topics],
                conversation_segments=self.segments,
                context_coherence=coherence,
                topic_shift_detected=topic_shift,
                reference_resolution=references,
                context_summary=summary,
                evaluation_time=time.time() - start_time
            )
            
            # Guardar resultado en memoria
            self.memory.store("last_context_evaluation", result.to_dict())
            
            return result
            
        except Exception as e:
            logger.error(f"Error en evaluación de contexto: {e}")
            logger.debug(traceback.format_exc())
            
            # Devolver resultado por defecto en caso de error
            return ContextEvaluationResult(
                relevant_entities=[],
                active_topics=[],
                conversation_segments=[],
                context_coherence=0.5,
                topic_shift_detected=False,
                reference_resolution={},
                context_summary="Error en evaluación de contexto",
                evaluation_time=time.time() - start_time
            )
    
    def _update_entities_and_topics(self, history: List[Dict[str, str]], current_message: str) -> None:
        """
        Actualiza el registro de entidades y temas basado en el historial y mensaje actual.
        
        Args:
            history: Historial de conversación
            current_message: Mensaje actual
        """
        # Extraer entidades del mensaje actual
        current_index = len(history)
        new_entities = self._extract_entities(current_message)
        
        # Actualizar entidades existentes o añadir nuevas
        for entity_name, entity_data in new_entities.items():
            if entity_name in self.entities:
                # Actualizar entidad existente
                self.entities[entity_name].update_mention(current_index)
                # Actualizar atributos si hay nuevos
                for attr, value in entity_data["attributes"].items():
                    self.entities[entity_name].attributes[attr] = value
            else:
                # Añadir nueva entidad
                self.entities[entity_name] = ContextualEntity(
                    name=entity_name,
                    type=entity_data["type"],
                    relevance=entity_data["relevance"],
                    first_mention_index=current_index,
                    last_mention_index=current_index,
                    attributes=entity_data["attributes"]
                )
        
        # Extraer temas del mensaje actual
        new_topics = self._extract_topics(current_message)
        
        # Actualizar temas
        for topic, relevance in new_topics.items():
            if topic in self.topics:
                # Actualizar relevancia (promedio ponderado favoreciendo lo más reciente)
                self.topics[topic] = 0.7 * relevance + 0.3 * self.topics[topic]
            else:
                # Añadir nuevo tema
                self.topics[topic] = relevance
        
        # Aplicar decaimiento a temas antiguos
        for topic in list(self.topics.keys()):
            self.topics[topic] *= self.recency_decay_factor
            # Eliminar temas con relevancia muy baja
            if self.topics[topic] < 0.1:
                del self.topics[topic]
        
        # Limitar número de entidades (mantener las más importantes)
        if len(self.entities) > self.max_entities:
            self.entities = dict(
                sorted(
                    self.entities.items(),
                    key=lambda x: x[1].calculate_importance(current_index),
                    reverse=True
                )[:self.max_entities]
            )
        
        # Limitar número de temas (mantener los más relevantes)
        if len(self.topics) > self.max_topics:
            self.topics = dict(
                sorted(
                    self.topics.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:self.max_topics]
            )
    
    def _extract_entities(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extrae entidades de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario de entidades extraídas con sus atributos
        """
        entities = {}
        
        # En una implementación real, aquí se usaría NER (Named Entity Recognition)
        # Esta es una implementación simplificada
        
        # Detectar nombres propios (simplificado)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        for match in re.finditer(name_pattern, text):
            name = match.group(0)
            entities[name] = {
                "type": "person",  # Asumimos que es una persona
                "relevance": 0.7,
                "attributes": {},
            }
        
        # Detectar tecnologías y lenguajes de programación
        tech_keywords = [
            "Python", "JavaScript", "Java", "C++", "Ruby", "Go", "Rust",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask",
            "TensorFlow", "PyTorch", "Keras", "scikit-learn",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "SQL", "MongoDB", "PostgreSQL", "MySQL", "Redis"
        ]
        
        for tech in tech_keywords:
            if re.search(r'\b' + re.escape(tech) + r'\b', text, re.IGNORECASE):
                entities[tech] = {
                    "type": "technology",
                    "relevance": 0.8,
                    "attributes": {},
                }
        
        # Detectar conceptos (simplificado)
        concept_pattern = r'\b(?:concepto|idea|teoría|método|enfoque|estrategia|técnica|proceso|sistema)\s+de\s+([A-Za-z\s]+)\b'
        for match in re.finditer(concept_pattern, text, re.IGNORECASE):
            concept = match.group(1).strip()
            entities[concept] = {
                "type": "concept",
                "relevance": 0.6,
                "attributes": {},
            }
        
        return entities
    
    def _extract_topics(self, text: str) -> Dict[str, float]:
        """
        Extrae temas de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario de temas con su relevancia
        """
        topics = {}
        
        # En una implementación real, aquí se usaría topic modeling
        # Esta es una implementación simplificada
        
        # Lista de posibles temas
        potential_topics = [
            "programación", "desarrollo", "tecnología", "inteligencia artificial",
            "aprendizaje automático", "desarrollo web", "bases de datos",
            "seguridad informática", "cloud computing", "devops",
            "frontend", "backend", "fullstack", "mobile", "desktop",
            "algoritmos", "estructuras de datos", "optimización",
            "arquitectura de software", "patrones de diseño"
        ]
        
        # Detectar temas basados en palabras clave
        for topic in potential_topics:
            # Buscar tema en el texto
            if re.search(r'\b' + re.escape(topic) + r'\b', text, re.IGNORECASE):
                # Asignar relevancia basada en la posición (más relevante si aparece al principio)
                position = text.lower().find(topic.lower())
                position_factor = 1.0 - (position / len(text)) * 0.5  # 0.5-1.0
                
                # Asignar relevancia basada en frecuencia
                frequency = len(re.findall(r'\b' + re.escape(topic) + r'\b', text, re.IGNORECASE))
                frequency_factor = min(1.0, frequency / 3.0)  # Máximo 3 menciones
                
                # Relevancia combinada
                relevance = 0.7 * position_factor + 0.3 * frequency_factor
                topics[topic] = relevance
        
        return topics
    
    def _segment_conversation(self, history: List[Dict[str, str]], current_message: str) -> None:
        """
        Segmenta la conversación en bloques temáticos.
        
        Args:
            history: Historial de conversación
            current_message: Mensaje actual
        """
        # Si no hay suficientes mensajes, no segmentar
        if len(history) < 3:
            return
        
        # Obtener temas ordenados por relevancia
        sorted_topics = sorted(
            self.topics.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        if not sorted_topics:
            return
        
        # Determinar tema principal actual
        current_main_topic = sorted_topics[0][0]
        
        # Verificar si hay un segmento activo con el mismo tema principal
        current_segment = None
        if self.segments and self.segments[-1].main_topic == current_main_topic:
            # Extender segmento existente
            current_segment = self.segments[-1]
            current_segment.end_index = len(history)
            
            # Actualizar subtemas
            current_segment.subtopics = [topic for topic, _ in sorted_topics[1:4]]
            
            # Actualizar entidades
            current_segment.entities = [
                entity.name for entity in sorted(
                    self.entities.values(),
                    key=lambda e: e.calculate_importance(len(history)),
                    reverse=True
                )[:5]
            ]
        else:
            # Crear nuevo segmento
            new_segment = ConversationSegment(
                start_index=max(0, len(history) - 2),  # Comenzar un poco antes
                end_index=len(history),
                main_topic=current_main_topic,
                subtopics=[topic for topic, _ in sorted_topics[1:4]],
                entities=[
                    entity.name for entity in sorted(
                        self.entities.values(),
                        key=lambda e: e.calculate_importance(len(history)),
                        reverse=True
                    )[:5]
                ],
                coherence_score=0.7,  # Valor inicial
                importance_score=0.8  # Valor inicial
            )
            
            self.segments.append(new_segment)
        
        # Limitar número de segmentos
        if len(self.segments) > self.max_segments:
            self.segments = self.segments[-self.max_segments:]
    
    def _evaluate_coherence(self, history: List[Dict[str, str]], current_message: str) -> float:
        """
        Evalúa la coherencia contextual de la conversación.
        
        Args:
            history: Historial de conversación
            current_message: Mensaje actual
            
        Returns:
            Puntuación de coherencia (0.0-1.0)
        """
        # Si no hay suficiente historial, asumir coherencia media
        if len(history) < 2:
            return 0.5
        
        # Factores que afectan la coherencia
        factors = []
        
        # 1. Continuidad temática
        if self.topics:
            # Verificar si los temas actuales están relacionados con mensajes anteriores
            previous_message = history[-1]["content"]
            previous_topics = self._extract_topics(previous_message)
            
            # Calcular solapamiento de temas
            common_topics = set(self.topics.keys()).intersection(previous_topics.keys())
            topic_continuity = len(common_topics) / max(1, min(len(self.topics), len(previous_topics)))
            factors.append(("topic_continuity", topic_continuity))
        
        # 2. Referencias a entidades previas
        if self.entities:
            # Contar referencias a entidades conocidas
            entity_references = 0
            for entity_name in self.entities:
                if re.search(r'\b' + re.escape(entity_name) + r'\b', current_message, re.IGNORECASE):
                    entity_references += 1
            
            entity_reference_score = min(1.0, entity_references / 3.0)  # Normalizar a máximo 3 referencias
            factors.append(("entity_references", entity_reference_score))
        
        # 3. Presencia de marcadores de cohesión
        cohesion_markers = [
            r'\b(?:por lo tanto|por consiguiente|en consecuencia|así que|entonces)\b',
            r'\b(?:además|también|asimismo|igualmente|del mismo modo)\b',
            r'\b(?:pero|sin embargo|no obstante|aunque|a pesar de)\b',
            r'\b(?:por ejemplo|como|tal como|en particular)\b',
            r'\b(?:en primer lugar|en segundo lugar|finalmente|por último)\b'
        ]
        
        cohesion_count = 0
        for marker in cohesion_markers:
            if re.search(marker, current_message, re.IGNORECASE):
                cohesion_count += 1
        
        cohesion_score = min(1.0, cohesion_count / 2.0)  # Normalizar a máximo 2 marcadores
        factors.append(("cohesion_markers", cohesion_score))
        
        # 4. Longitud apropiada de respuesta
        prev_length = len(previous_message) if len(history) > 0 else 0
        current_length = len(current_message)
        
        # Penalizar diferencias extremas de longitud
        length_ratio = min(prev_length, current_length) / max(1, max(prev_length, current_length))
        length_score = min(1.0, length_ratio + 0.3)  # Añadir offset para no penalizar demasiado
        factors.append(("length_appropriateness", length_score))
        
        # Calcular coherencia combinada (ponderada)
        weights = {
            "topic_continuity": 0.4,
            "entity_references": 0.3,
            "cohesion_markers": 0.2,
            "length_appropriateness": 0.1
        }
        
        coherence = 0.5  # Valor por defecto
        total_weight = 0.0
        
        for factor_name, factor_value in factors:
            if factor_name in weights:
                coherence += weights[factor_name] * factor_value
                total_weight += weights[factor_name]
        
        # Normalizar si hay factores
        if total_weight > 0:
            coherence = coherence / total_weight
        
        return max(0.0, min(1.0, coherence))
    
    def _detect_topic_shift(self, history: List[Dict[str, str]], current_message: str) -> bool:
        """
        Detecta si hay un cambio significativo de tema.
        
        Args:
            history: Historial de conversación
            current_message: Mensaje actual
            
        Returns:
            True si se detecta cambio de tema, False en caso contrario
        """
        # Si no hay suficiente historial, no hay cambio
        if len(history) < 2:
            return False
        
        # Extraer temas del mensaje anterior y actual
        previous_message = history[-1]["content"]
        previous_topics = self._extract_topics(previous_message)
        current_topics = self._extract_topics(current_message)
        
        # Si no hay temas, no podemos determinar cambio
        if not previous_topics or not current_topics:
            return False
        
        # Calcular solapamiento de temas
        common_topics = set(current_topics.keys()).intersection(previous_topics.keys())
        topic_overlap = len(common_topics) / max(1, min(len(current_topics), len(previous_topics)))
        
        # Detectar marcadores explícitos de cambio de tema
        topic_shift_markers = [
            r'\b(?:cambiando de tema|por otro lado|en otro orden de cosas)\b',
            r'\b(?:pasando a otro tema|hablando de otra cosa|sobre otro asunto)\b',
            r'\b(?:dejando eso de lado|olvidando lo anterior|volviendo a lo importante)\b'
        ]
        
        explicit_shift = any(re.search(marker, current_message, re.IGNORECASE) for marker in topic_shift_markers)
        
        # Determinar cambio de tema
        return explicit_shift or topic_overlap < (1.0 - self.topic_shift_threshold)
    
    def _resolve_references(self, history: List[Dict[str, str]], current_message: str) -> Dict[str, str]:
        """
        Resuelve referencias anafóricas en el mensaje actual.
        
        Args:
            history: Historial de conversación
            current_message: Mensaje actual
            
        Returns:
            Diccionario de referencias resueltas
        """
        resolved_references = {}
        
        # Si no hay suficiente historial o entidades, no podemos resolver
        if len(history) < 1 or not self.entities:
            return resolved_references
        
        # Obtener entidades ordenadas por importancia
        current_index = len(history)
        sorted_entities = sorted(
            self.entities.values(),
            key=lambda e: e.calculate_importance(current_index),
            reverse=True
        )
        
        # Buscar pronombres y referencias
        for ref_type, pattern in self.reference_patterns.items():
            for match in pattern.finditer(current_message):
                reference = match.group(0).lower()
                
                # Intentar resolver basado en tipo de referencia
                if ref_type == "pronombres_personales":
                    # Resolver pronombres personales
                    if reference in ["él", "lo", "le"]:
                        # Buscar entidad masculina más reciente
                        for entity in sorted_entities:
                            if entity.type == "person" and entity.attributes.get("gender", "unknown") == "male":
                                resolved_references[reference] = entity.name
                                break
                    elif reference in ["ella", "la", "le"]:
                        # Buscar entidad femenina más reciente
                        for entity in sorted_entities:
                            if entity.type == "person" and entity.attributes.get("gender", "unknown") == "female":
                                resolved_references[reference] = entity.name
                                break
                    elif reference in ["ellos", "ellas", "les"]:
                        # Buscar múltiples entidades
                        entities_names = [e.name for e in sorted_entities[:2]]
                        if entities_names:
                            resolved_references[reference] = ", ".join(entities_names)
                
                elif ref_type == "pronombres_demostrativos":
                    # Resolver pronombres demostrativos (generalmente al concepto más reciente)
                    for entity in sorted_entities:
                        if entity.type == "concept":
                            resolved_references[reference] = entity.name
                            break
        
        return resolved_references
    
    def _generate_context_summary(self, history: List[Dict[str, str]], current_message: str) -> str:
        """
        Genera un resumen del contexto actual.
        
        Args:
            history: Historial de conversación
            current_message: Mensaje actual
            
        Returns:
            Resumen del contexto
        """
        # Si no hay suficiente historial, no hay resumen
        if len(history) < 2:
            return "Conversación iniciada recientemente."
        
        # Obtener temas principales
        main_topics = sorted(
            self.topics.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Obtener entidades principales
        current_index = len(history)
        main_entities = sorted(
            self.entities.values(),
            key=lambda e: e.calculate_importance(current_index),
            reverse=True
        )[:5]
        
        # Construir resumen
        summary_parts = []
        
        # Añadir temas
        if main_topics:
            topics_str = ", ".join([topic for topic, _ in main_topics])
            summary_parts.append(f"Temas principales: {topics_str}.")
        
        # Añadir entidades
        if main_entities:
            entities_str = ", ".join([entity.name for entity in main_entities])
            summary_parts.append(f"Entidades relevantes: {entities_str}.")
        
        # Añadir información sobre coherencia
        coherence = self._evaluate_coherence(history, current_message)
        if coherence > 0.7:
            summary_parts.append("La conversación mantiene alta coherencia temática.")
        elif coherence > 0.4:
            summary_parts.append("La conversación tiene coherencia moderada.")
        else:
            summary_parts.append("La conversación muestra baja coherencia entre mensajes.")
        
        # Añadir información sobre cambio de tema
        if self._detect_topic_shift(history, current_message):
            summary_parts.append("Se ha detectado un cambio de tema en el mensaje actual.")
        
        # Combinar partes
        if summary_parts:
            return " ".join(summary_parts)
        else:
            return "No hay suficiente contexto para generar un resumen."
    
    def get_context_for_processing(self, context: Context, current_message: str) -> Dict[str, Any]:
        """
        Obtiene información contextual procesada para uso en generación de respuestas.
        
        Args:
            context: Contexto de la conversación
            current_message: Mensaje actual
            
        Returns:
            Diccionario con información contextual procesada
        """
        # Evaluar contexto
        evaluation = self.evaluate_context(context, current_message)
        
        # Construir contexto procesado
        processed_context = {
            "active_topics": evaluation.active_topics,
            "relevant_entities": [
                {
                    "name": entity.name,
                    "type": entity.type,
                    "importance": entity.calculate_importance(len(context.get_history()))
                }
                for entity in evaluation.relevant_entities[:5]  # Top 5 entidades
            ],
            "topic_shift": evaluation.topic_shift_detected,
            "context_coherence": evaluation.context_coherence,
            "resolved_references": evaluation.reference_resolution,
            "context_summary": evaluation.context_summary
        }
        
        return processed_context
