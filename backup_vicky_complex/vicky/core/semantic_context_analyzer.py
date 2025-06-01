"""
Analizador Semántico de Contexto para VokaFlow
----------------------------------------------

Este módulo implementa algoritmos avanzados para el análisis semántico
del contexto conversacional, permitiendo una comprensión más profunda
de las relaciones entre conceptos, temas y entidades.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Set, Union
import numpy as np
from dataclasses import dataclass, field
import traceback

# Importaciones internas
from .context import Context
from .memory import Memory
from ..models.embedding_model import EmbeddingModel

# Configurar logger
logger = logging.getLogger("vicky.semantic_context_analyzer")

@dataclass
class SemanticRelation:
    """Relación semántica entre dos conceptos."""
    source: str
    target: str
    relation_type: str  # similarity, causality, part_of, etc.
    strength: float  # 0.0 a 1.0
    confidence: float  # 0.0 a 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la relación a un diccionario."""
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "strength": self.strength,
            "confidence": self.confidence
        }


@dataclass
class SemanticAnalysisResult:
    """Resultado del análisis semántico del contexto."""
    concept_embeddings: Dict[str, List[float]]
    concept_clusters: Dict[str, List[str]]
    semantic_relations: List[SemanticRelation]
    topic_coherence: float  # 0.0 a 1.0
    semantic_shift: float  # 0.0 a 1.0 (grado de cambio semántico)
    key_concepts: List[str]
    analysis_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a un diccionario."""
        return {
            "concept_clusters": self.concept_clusters,
            "semantic_relations": [r.to_dict() for r in self.semantic_relations],
            "topic_coherence": self.topic_coherence,
            "semantic_shift": self.semantic_shift,
            "key_concepts": self.key_concepts,
            "analysis_time": self.analysis_time
        }


class SemanticContextAnalyzer:
    """
    Analizador semántico avanzado para contexto conversacional.
    
    Esta clase implementa algoritmos para:
    1. Generar embeddings de conceptos y entidades
    2. Identificar relaciones semánticas entre conceptos
    3. Agrupar conceptos relacionados en clusters
    4. Evaluar coherencia semántica del contexto
    5. Detectar cambios semánticos en la conversación
    6. Identificar conceptos clave para la comprensión
    """
    
    def __init__(self, embedding_model: EmbeddingModel, memory: Memory):
        """
        Inicializa el analizador semántico de contexto.
        
        Args:
            embedding_model: Modelo de embeddings para análisis semántico
            memory: Sistema de memoria para almacenar información contextual
        """
        self.embedding_model = embedding_model
        self.memory = memory
        
        # Caché de embeddings
        self.embedding_cache: Dict[str, List[float]] = {}
        
        # Relaciones semánticas identificadas
        self.relations: List[SemanticRelation] = []
        
        # Configuración
        self.similarity_threshold = 0.7  # Umbral para considerar similitud
        self.max_relations = 100
        self.max_cached_embeddings = 200
        
        logger.info("Analizador semántico de contexto inicializado")
    
    def analyze(self, context: Context, current_message: str) -> SemanticAnalysisResult:
        """
        Realiza análisis semántico del contexto conversacional.
        
        Args:
            context: Contexto de la conversación
            current_message: Mensaje actual
            
        Returns:
            Resultado del análisis semántico
        """
        start_time = time.time()
        
        try:
            # Extraer conceptos y entidades del contexto y mensaje actual
            concepts = self._extract_concepts(context, current_message)
            
            # Generar embeddings para conceptos
            concept_embeddings = self._generate_embeddings(concepts)
            
            # Identificar relaciones semánticas
            semantic_relations = self._identify_relations(concept_embeddings)
            
            # Agrupar conceptos en clusters
            concept_clusters = self._cluster_concepts(concept_embeddings, semantic_relations)
            
            # Evaluar coherencia semántica
            topic_coherence = self._evaluate_coherence(concept_embeddings, semantic_relations)
            
            # Detectar cambio semántico
            semantic_shift = self._detect_semantic_shift(context, current_message, concept_embeddings)
            
            # Identificar conceptos clave
            key_concepts = self._identify_key_concepts(concept_embeddings, semantic_relations)
            
            # Crear resultado
            result = SemanticAnalysisResult(
                concept_embeddings=concept_embeddings,
                concept_clusters=concept_clusters,
                semantic_relations=semantic_relations,
                topic_coherence=topic_coherence,
                semantic_shift=semantic_shift,
                key_concepts=key_concepts,
                analysis_time=time.time() - start_time
            )
            
            # Guardar resultado en memoria
            self.memory.store("last_semantic_analysis", result.to_dict())
            
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis semántico de contexto: {e}")
            logger.debug(traceback.format_exc())
            
            # Devolver resultado por defecto en caso de error
            return SemanticAnalysisResult(
                concept_embeddings={},
                concept_clusters={},
                semantic_relations=[],
                topic_coherence=0.5,
                semantic_shift=0.0,
                key_concepts=[],
                analysis_time=time.time() - start_time
            )
    
    def _extract_concepts(self, context: Context, current_message: str) -> List[str]:
        """
        Extrae conceptos y entidades del contexto y mensaje actual.
        
        Args:
            context: Contexto de la conversación
            current_message: Mensaje actual
            
        Returns:
            Lista de conceptos y entidades
        """
        concepts = set()
        
        # Extraer de mensaje actual
        message_concepts = self._extract_concepts_from_text(current_message)
        concepts.update(message_concepts)
        
        # Extraer de historial reciente
        history = context.get_history()
        for entry in history[-3:]:  # Últimos 3 mensajes
            if "content" in entry:
                history_concepts = self._extract_concepts_from_text(entry["content"])
                concepts.update(history_concepts)
        
        # Extraer de metadatos de contexto
        metadata = context.metadata
        if "topics" in metadata:
            concepts.update(metadata["topics"])
        if "entities" in metadata:
            concepts.update(metadata["entities"])
        
        return list(concepts)
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """
        Extrae conceptos de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de conceptos extraídos
        """
        # En una implementación real, aquí se usaría NLP avanzado
        # Esta es una implementación simplificada
        
        # Lista de conceptos técnicos comunes
        tech_concepts = [
            "programación", "desarrollo", "algoritmo", "estructura de datos",
            "base de datos", "frontend", "backend", "api", "servidor",
            "cliente", "red", "seguridad", "cloud", "contenedor",
            "inteligencia artificial", "machine learning", "deep learning",
            "procesamiento de lenguaje natural", "visión por computadora"
        ]
        
        # Extraer conceptos que aparecen en el texto
        found_concepts = []
        for concept in tech_concepts:
            if concept.lower() in text.lower():
                found_concepts.append(concept)
        
        # Limitar número de conceptos
        return found_concepts[:10]  # Máximo 10 conceptos
    
    def _generate_embeddings(self, concepts: List[str]) -> Dict[str, List[float]]:
        """
        Genera embeddings para conceptos.
        
        Args:
            concepts: Lista de conceptos
            
        Returns:
            Diccionario de conceptos con sus embeddings
        """
        embeddings = {}
        
        for concept in concepts:
            # Verificar si ya está en caché
            if concept in self.embedding_cache:
                embeddings[concept] = self.embedding_cache[concept]
            else:
                # Generar nuevo embedding
                try:
                    embedding = self.embedding_model.get_embedding(concept)
                    embeddings[concept] = embedding
                    
                    # Añadir a caché
                    self.embedding_cache[concept] = embedding
                except Exception as e:
                    logger.error(f"Error al generar embedding para '{concept}': {e}")
        
        # Limitar tamaño de caché
        if len(self.embedding_cache) > self.max_cached_embeddings:
            # Eliminar entradas más antiguas (simplificado)
            excess = len(self.embedding_cache) - self.max_cached_embeddings
            keys_to_remove = list(self.embedding_cache.keys())[:excess]
            for key in keys_to_remove:
                del self.embedding_cache[key]
        
        return embeddings
    
    def _identify_relations(self, concept_embeddings: Dict[str, List[float]]) -> List[SemanticRelation]:
        """
        Identifica relaciones semánticas entre conceptos.
        
        Args:
            concept_embeddings: Diccionario de conceptos con sus embeddings
            
        Returns:
            Lista de relaciones semánticas
        """
        relations = []
        
        # Calcular similitud entre todos los pares de conceptos
        concepts = list(concept_embeddings.keys())
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                concept1 = concepts[i]
                concept2 = concepts[j]
                
                # Calcular similitud coseno
                similarity = self._cosine_similarity(
                    concept_embeddings[concept1],
                    concept_embeddings[concept2]
                )
                
                # Si supera el umbral, crear relación
                if similarity >= self.similarity_threshold:
                    relation = SemanticRelation(
                        source=concept1,
                        target=concept2,
                        relation_type="similarity",
                        strength=similarity,
                        confidence=0.8  # Valor predeterminado
                    )
                    relations.append(relation)
        
        # Ordenar por fuerza de relación
        relations.sort(key=lambda r: r.strength, reverse=True)
        
        # Limitar número de relaciones
        if len(relations) > self.max_relations:
            relations = relations[:self.max_relations]
        
        return relations
    
    def _cluster_concepts(self, concept_embeddings: Dict[str, List[float]], 
                         relations: List[SemanticRelation]) -> Dict[str, List[str]]:
        """
        Agrupa conceptos en clusters basados en similitud semántica.
        
        Args:
            concept_embeddings: Diccionario de conceptos con sus embeddings
            relations: Lista de relaciones semánticas
            
        Returns:
            Diccionario de clusters con sus conceptos
        """
        # Implementación simplificada de clustering
        # En una implementación real, se usaría un algoritmo como K-means o clustering jerárquico
        
        # Crear grafo de relaciones
        graph = {}
        for relation in relations:
            if relation.source not in graph:
                graph[relation.source] = []
            if relation.target not in graph:
                graph[relation.target] = []
            
            graph[relation.source].append((relation.target, relation.strength))
            graph[relation.target].append((relation.source, relation.strength))
        
        # Inicializar clusters
        clusters = {}
        visited = set()
        
        # Función para DFS
        def dfs(node, cluster_id):
            visited.add(node)
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(node)
            
            if node in graph:
                for neighbor, _ in graph[node]:
                    if neighbor not in visited:
                        dfs(neighbor, cluster_id)
        
        # Ejecutar DFS para cada nodo no visitado
        cluster_id = 0
        for concept in concept_embeddings:
            if concept not in visited:
                dfs(concept, f"cluster_{cluster_id}")
                cluster_id += 1
        
        return clusters
    
    def _evaluate_coherence(self, concept_embeddings: Dict[str, List[float]], 
                           relations: List[SemanticRelation]) -> float:
        """
        Evalúa la coherencia semántica del contexto.
        
        Args:
            concept_embeddings: Diccionario de conceptos con sus embeddings
            relations: Lista de relaciones semánticas
            
        Returns:
            Puntuación de coherencia (0.0-1.0)
        """
        # Si no hay suficientes conceptos o relaciones, coherencia media
        if len(concept_embeddings) < 2 or not relations:
            return 0.5
        
        # Calcular densidad de relaciones
        max_possible_relations = len(concept_embeddings) * (len(concept_embeddings) - 1) / 2
        relation_density = len(relations) / max_possible_relations
        
        # Calcular fuerza promedio de relaciones
        avg_strength = sum(r.strength for r in relations) / len(relations)
        
        # Combinar factores
        coherence = 0.7 * avg_strength + 0.3 * relation_density
        
        return max(0.0, min(1.0, coherence))
    
    def _detect_semantic_shift(self, context: Context, current_message: str, 
                              current_embeddings: Dict[str, List[float]]) -> float:
        """
        Detecta cambios semánticos en la conversación.
        
        Args:
            context: Contexto de la conversación
            current_message: Mensaje actual
            current_embeddings: Embeddings actuales
            
        Returns:
            Grado de cambio semántico (0.0-1.0)
        """
        # Obtener análisis semántico anterior
        previous_analysis = self.memory.retrieve("last_semantic_analysis", None)
        
        # Si no hay análisis previo, no hay cambio
        if not previous_analysis:
            return 0.0
        
        # Obtener conceptos clave anteriores
        previous_key_concepts = previous_analysis.get("key_concepts", [])
        
        # Si no hay conceptos clave anteriores, no hay cambio
        if not previous_key_concepts:
            return 0.0
        
        # Calcular solapamiento de conceptos
        current_concepts = set(current_embeddings.keys())
        previous_concepts = set(previous_key_concepts)
        
        common_concepts = current_concepts.intersection(previous_concepts)
        
        # Calcular Jaccard similarity
        if not current_concepts and not previous_concepts:
            concept_similarity = 1.0
        elif not current_concepts or not previous_concepts:
            concept_similarity = 0.0
        else:
            concept_similarity = len(common_concepts) / len(current_concepts.union(previous_concepts))
        
        # Convertir a grado de cambio (inverso de similitud)
        semantic_shift = 1.0 - concept_similarity
        
        return semantic_shift
    
    def _identify_key_concepts(self, concept_embeddings: Dict[str, List[float]], 
                              relations: List[SemanticRelation]) -> List[str]:
        """
        Identifica conceptos clave en el contexto actual.
        
        Args:
            concept_embeddings: Diccionario de conceptos con sus embeddings
            relations: Lista de relaciones semánticas
            
        Returns:
            Lista de conceptos clave
        """
        # Si no hay conceptos, lista vacía
        if not concept_embeddings:
            return []
        
        # Calcular centralidad de conceptos (número de relaciones)
        centrality = {concept: 0 for concept in concept_embeddings}
        
        for relation in relations:
            centrality[relation.source] = centrality.get(relation.source, 0) + 1
            centrality[relation.target] = centrality.get(relation.target, 0) + 1
        
        # Ordenar conceptos por centralidad
        sorted_concepts = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Seleccionar top conceptos
        key_concepts = [concept for concept, _ in sorted_concepts[:5]]
        
        return key_concepts
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula la similitud coseno entre dos vectores.
        
        Args:
            vec1: Primer vector
            vec2: Segundo vector
            
        Returns:
            Similitud coseno (0.0-1.0)
        """
        # Convertir a arrays de numpy
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        # Calcular producto punto
        dot_product = np.dot(vec1_np, vec2_np)
        
        # Calcular normas
        norm_vec1 = np.linalg.norm(vec1_np)
        norm_vec2 = np.linalg.norm(vec2_np)
        
        # Evitar división por cero
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        # Calcular similitud
        similarity = dot_product / (norm_vec1 * norm_vec2)
        
        return max(0.0, min(1.0, similarity))
