"""
Sistema de Memoria a Largo Plazo para Vicky
-------------------------------------------

Este módulo implementa un sistema avanzado de memoria a largo plazo
que permite almacenar, organizar, recuperar y olvidar información
de manera eficiente y semánticamente significativa.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
import json
import os
import shutil
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
import numpy as np
from datetime import datetime, timedelta
import pickle
import hashlib
import traceback
import re
from pathlib import Path
import threading
import queue

# Configurar logger
logger = logging.getLogger("vicky.memory.long_term")

@dataclass
class MemoryItem:
    """Elemento individual de memoria."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0 a 1.0
    last_accessed: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    associations: Dict[str, float] = field(default_factory=dict)  # ID -> strength
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el elemento a un diccionario."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "last_accessed": self.last_accessed,
            "creation_time": self.creation_time,
            "access_count": self.access_count,
            "tags": self.tags,
            "associations": self.associations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Crea un elemento de memoria a partir de un diccionario."""
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            last_accessed=data.get("last_accessed", time.time()),
            creation_time=data.get("creation_time", time.time()),
            access_count=data.get("access_count", 0),
            tags=data.get("tags", []),
            associations=data.get("associations", {})
        )


@dataclass
class MemoryCategory:
    """Categoría de memoria para organización jerárquica."""
    id: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    memory_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la categoría a un diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "memory_ids": self.memory_ids,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryCategory':
        """Crea una categoría de memoria a partir de un diccionario."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            children_ids=data.get("children_ids", []),
            memory_ids=data.get("memory_ids", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class MemorySearchResult:
    """Resultado de búsqueda en memoria."""
    item: MemoryItem
    score: float
    category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a un diccionario."""
        return {
            "id": self.item.id,
            "content": self.item.content,
            "score": self.score,
            "category": self.category,
            "metadata": self.item.metadata,
            "importance": self.item.importance,
            "creation_time": self.item.creation_time,
            "tags": self.item.tags
        }


class LongTermMemory:
    """
    Sistema avanzado de memoria a largo plazo.
    
    Esta clase implementa un sistema completo para:
    1. Almacenar información importante de forma persistente
    2. Organizar la información en categorías jerárquicas
    3. Recuperar información mediante búsqueda semántica
    4. Implementar mecanismos de olvido selectivo
    5. Establecer asociaciones entre elementos de memoria
    6. Consolidar información relacionada
    7. Priorizar recuerdos por importancia y relevancia
    """
    
    def __init__(self, storage_path: str = None, embedding_model = None):
        """
        Inicializa el sistema de memoria a largo plazo.
        
        Args:
            storage_path: Ruta al directorio de almacenamiento
            embedding_model: Modelo para generar embeddings
        """
        self.storage_path = storage_path or "/mnt/nvme_fast/vokaflow_data/long_term_memory"
        self.embedding_model = embedding_model
        
        # Rutas de almacenamiento
        self.items_path = os.path.join(self.storage_path, "items")
        self.categories_path = os.path.join(self.storage_path, "categories")
        self.embeddings_path = os.path.join(self.storage_path, "embeddings")
        self.index_path = os.path.join(self.storage_path, "index")
        
        # Crear directorios si no existen
        for path in [self.storage_path, self.items_path, self.categories_path, 
                    self.embeddings_path, self.index_path]:
            os.makedirs(path, exist_ok=True)
        
        # Caché en memoria
        self.items_cache: Dict[str, MemoryItem] = {}
        self.categories_cache: Dict[str, MemoryCategory] = {}
        self.embedding_cache: Dict[str, List[float]] = {}
        
        # Índice invertido para búsqueda por texto
        self.text_index: Dict[str, Set[str]] = {}  # palabra -> conjunto de IDs
        
        # Índice para búsqueda por tags
        self.tag_index: Dict[str, Set[str]] = {}  # tag -> conjunto de IDs
        
        # Configuración
        self.max_cache_size = 1000
        self.importance_threshold = 0.3  # Umbral para olvido
        self.access_decay_rate = 0.99  # Tasa de decaimiento por acceso
        self.time_decay_rate = 0.95  # Tasa de decaimiento por tiempo
        
        # Cargar índices
        self._load_indices()
        
        # Cola de tareas en segundo plano
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.worker_thread.start()
        
        logger.info("Sistema de memoria a largo plazo inicializado")
    
    def _background_worker(self):
        """Trabajador en segundo plano para tareas asíncronas."""
        while True:
            try:
                task, args, kwargs = self.task_queue.get()
                task(*args, **kwargs)
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Error en tarea en segundo plano: {e}")
                logger.debug(traceback.format_exc())
    
    def _enqueue_task(self, task, *args, **kwargs):
        """Encola una tarea para ejecución en segundo plano."""
        self.task_queue.put((task, args, kwargs))
    
    def _load_indices(self):
        """Carga los índices desde el almacenamiento."""
        # Cargar índice de texto
        text_index_path = os.path.join(self.index_path, "text_index.pkl")
        if os.path.exists(text_index_path):
            try:
                with open(text_index_path, "rb") as f:
                    self.text_index = pickle.load(f)
            except Exception as e:
                logger.error(f"Error al cargar índice de texto: {e}")
                self.text_index = {}
        
        # Cargar índice de tags
        tag_index_path = os.path.join(self.index_path, "tag_index.pkl")
        if os.path.exists(tag_index_path):
            try:
                with open(tag_index_path, "rb") as f:
                    self.tag_index = pickle.load(f)
            except Exception as e:
                logger.error(f"Error al cargar índice de tags: {e}")
                self.tag_index = {}
    
    def _save_indices(self):
        """Guarda los índices en el almacenamiento."""
        # Guardar índice de texto
        text_index_path = os.path.join(self.index_path, "text_index.pkl")
        try:
            with open(text_index_path, "wb") as f:
                pickle.dump(self.text_index, f)
        except Exception as e:
            logger.error(f"Error al guardar índice de texto: {e}")
        
        # Guardar índice de tags
        tag_index_path = os.path.join(self.index_path, "tag_index.pkl")
        try:
            with open(tag_index_path, "wb") as f:
                pickle.dump(self.tag_index, f)
        except Exception as e:
            logger.error(f"Error al guardar índice de tags: {e}")
    
    def _update_text_index(self, item_id: str, content: str):
        """
        Actualiza el índice invertido de texto.
        
        Args:
            item_id: ID del elemento de memoria
            content: Contenido del elemento
        """
        # Tokenizar contenido (simplificado)
        words = set(re.findall(r'\b\w+\b', content.lower()))
        
        # Actualizar índice
        for word in words:
            if word not in self.text_index:
                self.text_index[word] = set()
            self.text_index[word].add(item_id)
    
    def _update_tag_index(self, item_id: str, tags: List[str]):
        """
        Actualiza el índice de tags.
        
        Args:
            item_id: ID del elemento de memoria
            tags: Lista de tags
        """
        # Actualizar índice
        for tag in tags:
            tag = tag.lower()
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(item_id)
    
    def _remove_from_indices(self, item_id: str, item: MemoryItem):
        """
        Elimina un elemento de los índices.
        
        Args:
            item_id: ID del elemento de memoria
            item: Elemento de memoria
        """
        # Eliminar de índice de texto
        words = set(re.findall(r'\b\w+\b', item.content.lower()))
        for word in words:
            if word in self.text_index and item_id in self.text_index[word]:
                self.text_index[word].remove(item_id)
                if not self.text_index[word]:
                    del self.text_index[word]
        
        # Eliminar de índice de tags
        for tag in item.tags:
            tag = tag.lower()
            if tag in self.tag_index and item_id in self.tag_index[tag]:
                self.tag_index[tag].remove(item_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
    
    def store(self, content: str, metadata: Dict[str, Any] = None, 
             importance: float = 0.5, tags: List[str] = None, 
             category_id: str = None) -> str:
        """
        Almacena un elemento en la memoria a largo plazo.
        
        Args:
            content: Contenido del elemento
            metadata: Metadatos adicionales
            importance: Importancia del elemento (0.0-1.0)
            tags: Lista de tags para categorización
            category_id: ID de la categoría a la que pertenece
            
        Returns:
            ID del elemento almacenado
        """
        # Generar ID único
        item_id = f"mem_{int(time.time())}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        # Crear elemento de memoria
        item = MemoryItem(
            id=item_id,
            content=content,
            metadata=metadata or {},
            importance=importance,
            creation_time=time.time(),
            last_accessed=time.time(),
            tags=tags or []
        )
        
        # Generar embedding en segundo plano
        if self.embedding_model:
            self._enqueue_task(self._generate_and_store_embedding, item_id, content)
        
        # Guardar elemento
        self._save_item(item)
        
        # Actualizar índices
        self._update_text_index(item_id, content)
        self._update_tag_index(item_id, item.tags)
        
        # Añadir a categoría si se especifica
        if category_id:
            self.add_to_category(item_id, category_id)
        
        # Guardar índices en segundo plano
        self._enqueue_task(self._save_indices)
        
        logger.info(f"Elemento almacenado en memoria a largo plazo: {item_id}")
        return item_id
    
    def _save_item(self, item: MemoryItem):
        """
        Guarda un elemento en el almacenamiento.
        
        Args:
            item: Elemento de memoria
        """
        # Guardar en caché
        self.items_cache[item.id] = item
        
        # Guardar en disco
        item_path = os.path.join(self.items_path, f"{item.id}.json")
        try:
            with open(item_path, "w") as f:
                json.dump(item.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar elemento {item.id}: {e}")
    
    def _generate_and_store_embedding(self, item_id: str, content: str):
        """
        Genera y almacena el embedding para un elemento.
        
        Args:
            item_id: ID del elemento
            content: Contenido del elemento
        """
        try:
            # Generar embedding
            embedding = self.embedding_model.get_embedding(content)
            
            # Guardar en caché
            self.embedding_cache[item_id] = embedding
            
            # Guardar en disco
            embedding_path = os.path.join(self.embeddings_path, f"{item_id}.npy")
            np.save(embedding_path, embedding)
            
            # Actualizar elemento
            item = self.get(item_id)
            if item:
                item.embedding = embedding
                self._save_item(item)
                
            logger.debug(f"Embedding generado para elemento {item_id}")
        except Exception as e:
            logger.error(f"Error al generar embedding para elemento {item_id}: {e}")
    
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """
        Recupera un elemento de la memoria.
        
        Args:
            item_id: ID del elemento
            
        Returns:
            Elemento de memoria o None si no existe
        """
        # Verificar caché
        if item_id in self.items_cache:
            item = self.items_cache[item_id]
            # Actualizar estadísticas de acceso
            item.last_accessed = time.time()
            item.access_count += 1
            return item
        
        # Intentar cargar desde disco
        item_path = os.path.join(self.items_path, f"{item_id}.json")
        if os.path.exists(item_path):
            try:
                with open(item_path, "r") as f:
                    item_data = json.load(f)
                
                # Crear elemento
                item = MemoryItem.from_dict(item_data)
                
                # Actualizar estadísticas de acceso
                item.last_accessed = time.time()
                item.access_count += 1
                
                # Guardar en caché
                self.items_cache[item_id] = item
                
                # Actualizar en disco
                self._save_item(item)
                
                # Cargar embedding si existe
                embedding_path = os.path.join(self.embeddings_path, f"{item_id}.npy")
                if os.path.exists(embedding_path):
                    try:
                        item.embedding = np.load(embedding_path).tolist()
                        self.embedding_cache[item_id] = item.embedding
                    except Exception as e:
                        logger.error(f"Error al cargar embedding para elemento {item_id}: {e}")
                
                return item
            except Exception as e:
                logger.error(f"Error al cargar elemento {item_id}: {e}")
        
        return None
    
    def update(self, item_id: str, content: str = None, metadata: Dict[str, Any] = None,
              importance: float = None, tags: List[str] = None) -> bool:
        """
        Actualiza un elemento de la memoria.
        
        Args:
            item_id: ID del elemento
            content: Nuevo contenido (opcional)
            metadata: Nuevos metadatos (opcional)
            importance: Nueva importancia (opcional)
            tags: Nuevos tags (opcional)
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        # Obtener elemento
        item = self.get(item_id)
        if not item:
            logger.error(f"No se encontró elemento {item_id} para actualizar")
            return False
        
        # Actualizar campos
        if content is not None:
            old_content = item.content
            item.content = content
            
            # Actualizar índice de texto
            self._remove_from_indices(item_id, item)
            self._update_text_index(item_id, content)
            
            # Regenerar embedding en segundo plano
            if self.embedding_model and old_content != content:
                self._enqueue_task(self._generate_and_store_embedding, item_id, content)
        
        if metadata is not None:
            # Actualizar metadatos (merge)
            item.metadata.update(metadata)
        
        if importance is not None:
            item.importance = max(0.0, min(1.0, importance))
        
        if tags is not None:
            old_tags = item.tags
            item.tags = tags
            
            # Actualizar índice de tags
            for tag in old_tags:
                tag = tag.lower()
                if tag in self.tag_index and item_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(item_id)
                    if not self.tag_index[tag]:
                        del self.tag_index[tag]
            
            self._update_tag_index(item_id, tags)
        
        # Guardar cambios
        self._save_item(item)
        
        # Guardar índices en segundo plano
        self._enqueue_task(self._save_indices)
        
        logger.info(f"Elemento {item_id} actualizado")
        return True
    
    def delete(self, item_id: str) -> bool:
        """
        Elimina un elemento de la memoria.
        
        Args:
            item_id: ID del elemento
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        # Obtener elemento
        item = self.get(item_id)
        if not item:
            logger.error(f"No se encontró elemento {item_id} para eliminar")
            return False
        
        # Eliminar de índices
        self._remove_from_indices(item_id, item)
        
        # Eliminar de categorías
        for category in self.list_categories():
            if item_id in category.memory_ids:
                category.memory_ids.remove(item_id)
                self._save_category(category)
        
        # Eliminar de caché
        if item_id in self.items_cache:
            del self.items_cache[item_id]
        
        if item_id in self.embedding_cache:
            del self.embedding_cache[item_id]
        
        # Eliminar archivos
        item_path = os.path.join(self.items_path, f"{item_id}.json")
        if os.path.exists(item_path):
            os.remove(item_path)
        
        embedding_path = os.path.join(self.embeddings_path, f"{item_id}.npy")
        if os.path.exists(embedding_path):
            os.remove(embedding_path)
        
        # Guardar índices en segundo plano
        self._enqueue_task(self._save_indices)
        
        logger.info(f"Elemento {item_id} eliminado")
        return True
    
    def search(self, query: str, limit: int = 10, threshold: float = 0.6,
              categories: List[str] = None, tags: List[str] = None,
              time_range: Tuple[float, float] = None) -> List[MemorySearchResult]:
        """
        Busca elementos en la memoria.
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            threshold: Umbral de similitud (0.0-1.0)
            categories: Lista de IDs de categorías para filtrar
            tags: Lista de tags para filtrar
            time_range: Rango de tiempo (inicio, fin) para filtrar
            
        Returns:
            Lista de resultados de búsqueda
        """
        results = []
        
        # Filtrar por categorías
        candidate_ids = set()
        if categories:
            for category_id in categories:
                category = self.get_category(category_id)
                if category:
                    candidate_ids.update(category.memory_ids)
        
        # Filtrar por tags
        tag_filtered_ids = set()
        if tags:
            for tag in tags:
                tag = tag.lower()
                if tag in self.tag_index:
                    if not tag_filtered_ids:
                        tag_filtered_ids = set(self.tag_index[tag])
                    else:
                        tag_filtered_ids.intersection_update(self.tag_index[tag])
        
        # Combinar filtros
        if categories and tags:
            candidate_ids.intersection_update(tag_filtered_ids)
        elif tags:
            candidate_ids = tag_filtered_ids
        
        # Si hay embedding model, usar búsqueda semántica
        if self.embedding_model:
            try:
                # Generar embedding para la consulta
                query_embedding = self.embedding_model.get_embedding(query)
                
                # Buscar elementos similares
                similarities = []
                
                # Determinar elementos a buscar
                items_to_search = []
                if candidate_ids:
                    # Buscar solo en elementos filtrados
                    for item_id in candidate_ids:
                        item = self.get(item_id)
                        if item:
                            items_to_search.append(item)
                else:
                    # Buscar en todos los elementos
                    for item_id in self._list_all_item_ids():
                        item = self.get(item_id)
                        if item:
                            items_to_search.append(item)
                
                # Calcular similitudes
                for item in items_to_search:
                    # Filtrar por tiempo si se especifica
                    if time_range:
                        start_time, end_time = time_range
                        if item.creation_time < start_time or item.creation_time > end_time:
                            continue
                    
                    # Obtener embedding del elemento
                    item_embedding = None
                    if item.embedding:
                        item_embedding = item.embedding
                    elif item.id in self.embedding_cache:
                        item_embedding = self.embedding_cache[item.id]
                    else:
                        # Intentar cargar desde disco
                        embedding_path = os.path.join(self.embeddings_path, f"{item.id}.npy")
                        if os.path.exists(embedding_path):
                            try:
                                item_embedding = np.load(embedding_path).tolist()
                                self.embedding_cache[item.id] = item_embedding
                                item.embedding = item_embedding
                            except Exception as e:
                                logger.error(f"Error al cargar embedding para elemento {item.id}: {e}")
                    
                    # Si no hay embedding, generarlo
                    if not item_embedding and self.embedding_model:
                        try:
                            item_embedding = self.embedding_model.get_embedding(item.content)
                            self.embedding_cache[item.id] = item_embedding
                            item.embedding = item_embedding
                            
                            # Guardar en disco en segundo plano
                            embedding_path = os.path.join(self.embeddings_path, f"{item.id}.npy")
                            self._enqueue_task(np.save, embedding_path, np.array(item_embedding))
                        except Exception as e:
                            logger.error(f"Error al generar embedding para elemento {item.id}: {e}")
                    
                    # Calcular similitud si hay embedding
                    if item_embedding:
                        similarity = self._cosine_similarity(query_embedding, item_embedding)
                        
                        # Si supera el umbral, añadir a resultados
                        if similarity >= threshold:
                            # Determinar categoría
                            category_name = None
                            for category in self.list_categories():
                                if item.id in category.memory_ids:
                                    category_name = category.name
                                    break
                            
                            # Crear resultado
                            result = MemorySearchResult(
                                item=item,
                                score=similarity,
                                category=category_name
                            )
                            similarities.append((result, similarity))
                
                # Ordenar por similitud
                similarities.sort(key=lambda x: x[1], reverse=True)
                
                # Limitar resultados
                results = [result for result, _ in similarities[:limit]]
                
            except Exception as e:
                logger.error(f"Error en búsqueda semántica: {e}")
                logger.debug(traceback.format_exc())
        
        # Si no hay resultados o no hay embedding model, usar búsqueda por texto
        if not results:
            # Tokenizar consulta
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            
            # Buscar elementos que contengan las palabras
            matching_ids = set()
            for word in query_words:
                if word in self.text_index:
                    if not matching_ids:
                        matching_ids = set(self.text_index[word])
                    else:
                        matching_ids.intersection_update(self.text_index[word])
            
            # Filtrar por categorías y tags si se especifican
            if candidate_ids:
                matching_ids.intersection_update(candidate_ids)
            
            # Obtener elementos
            for item_id in matching_ids:
                item = self.get(item_id)
                if item:
                    # Filtrar por tiempo si se especifica
                    if time_range:
                        start_time, end_time = time_range
                        if item.creation_time < start_time or item.creation_time > end_time:
                            continue
                    
                    # Calcular puntuación simple (proporción de palabras que coinciden)
                    item_words = set(re.findall(r'\b\w+\b', item.content.lower()))
                    matching_words = query_words.intersection(item_words)
                    score = len(matching_words) / max(1, len(query_words))
                    
                    # Si supera el umbral, añadir a resultados
                    if score >= threshold:
                        # Determinar categoría
                        category_name = None
                        for category in self.list_categories():
                            if item.id in category.memory_ids:
                                category_name = category.name
                                break
                        
                        # Crear resultado
                        result = MemorySearchResult(
                            item=item,
                            score=score,
                            category=category_name
                        )
                        results.append(result)
            
            # Ordenar por puntuación
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Limitar resultados
            results = results[:limit]
        
        return results
    
    def _list_all_item_ids(self) -> List[str]:
        """
        Lista todos los IDs de elementos en la memoria.
        
        Returns:
            Lista de IDs
        """
        # Listar archivos en directorio de elementos
        item_files = [f for f in os.listdir(self.items_path) if f.endswith(".json")]
        
        # Extraer IDs
        item_ids = [f.replace(".json", "") for f in item_files]
        
        return item_ids
    
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
    
    def create_category(self, name: str, description: str = "", 
                       parent_id: str = None) -> str:
        """
        Crea una nueva categoría.
        
        Args:
            name: Nombre de la categoría
            description: Descripción de la categoría
            parent_id: ID de la categoría padre
            
        Returns:
            ID de la categoría creada
        """
        # Generar ID único
        category_id = f"cat_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        # Crear categoría
        category = MemoryCategory(
            id=category_id,
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        # Guardar categoría
        self._save_category(category)
        
        # Actualizar categoría padre si existe
        if parent_id:
            parent = self.get_category(parent_id)
            if parent:
                parent.children_ids.append(category_id)
                self._save_category(parent)
        
        logger.info(f"Categoría creada: {category_id} ({name})")
        return category_id
    
    def _save_category(self, category: MemoryCategory):
        """
        Guarda una categoría en el almacenamiento.
        
        Args:
            category: Categoría de memoria
        """
        # Guardar en caché
        self.categories_cache[category.id] = category
        
        # Guardar en disco
        category_path = os.path.join(self.categories_path, f"{category.id}.json")
        try:
            with open(category_path, "w") as f:
                json.dump(category.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar categoría {category.id}: {e}")
    
    def get_category(self, category_id: str) -> Optional[MemoryCategory]:
        """
        Recupera una categoría.
        
        Args:
            category_id: ID de la categoría
            
        Returns:
            Categoría de memoria o None si no existe
        """
        # Verificar caché
        if category_id in self.categories_cache:
            return self.categories_cache[category_id]
        
        # Intentar cargar desde disco
        category_path = os.path.join(self.categories_path, f"{category_id}.json")
        if os.path.exists(category_path):
            try:
                with open(category_path, "r") as f:
                    category_data = json.load(f)
                
                # Crear categoría
                category = MemoryCategory.from_dict(category_data)
                
                # Guardar en caché
                self.categories_cache[category_id] = category
                
                return category
            except Exception as e:
                logger.error(f"Error al cargar categoría {category_id}: {e}")
        
        return None
    
    def update_category(self, category_id: str, name: str = None, 
                       description: str = None, parent_id: str = None) -> bool:
        """
        Actualiza una categoría.
        
        Args:
            category_id: ID de la categoría
            name: Nuevo nombre (opcional)
            description: Nueva descripción (opcional)
            parent_id: Nuevo ID de categoría padre (opcional)
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        # Obtener categoría
        category = self.get_category(category_id)
        if not category:
            logger.error(f"No se encontró categoría {category_id} para actualizar")
            return False
        
        # Actualizar campos
        if name is not None:
            category.name = name
        
        if description is not None:
            category.description = description
        
        if parent_id is not None and parent_id != category.parent_id:
            # Eliminar de categoría padre anterior
            if category.parent_id:
                old_parent = self.get_category(category.parent_id)
                if old_parent and category_id in old_parent.children_ids:
                    old_parent.children_ids.remove(category_id)
                    self._save_category(old_parent)
            
            # Añadir a nueva categoría padre
            category.parent_id = parent_id
            if parent_id:
                new_parent = self.get_category(parent_id)
                if new_parent:
                    new_parent.children_ids.append(category_id)
                    self._save_category(new_parent)
        
        # Guardar cambios
        self._save_category(category)
        
        logger.info(f"Categoría {category_id} actualizada")
        return True
    
    def delete_category(self, category_id: str, recursive: bool = False) -> bool:
        """
        Elimina una categoría.
        
        Args:
            category_id: ID de la categoría
            recursive: Si es True, elimina también las subcategorías
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        # Obtener categoría
        category = self.get_category(category_id)
        if not category:
            logger.error(f"No se encontró categoría {category_id} para eliminar")
            return False
        
        # Verificar si tiene subcategorías
        if category.children_ids and not recursive:
            logger.error(f"La categoría {category_id} tiene subcategorías y recursive=False")
            return False
        
        # Eliminar subcategorías si es recursivo
        if recursive:
            for child_id in list(category.children_ids):
                self.delete_category(child_id, recursive=True)
        
        # Eliminar de categoría padre
        if category.parent_id:
            parent = self.get_category(category.parent_id)
            if parent and category_id in parent.children_ids:
                parent.children_ids.remove(category_id)
                self._save_category(parent)
        
        # Eliminar de caché
        if category_id in self.categories_cache:
            del self.categories_cache[category_id]
        
        # Eliminar archivo
        category_path = os.path.join(self.categories_path, f"{category_id}.json")
        if os.path.exists(category_path):
            os.remove(category_path)
        
        logger.info(f"Categoría {category_id} eliminada")
        return True
    
    def list_categories(self) -> List[MemoryCategory]:
        """
        Lista todas las categorías.
        
        Returns:
            Lista de categorías
        """
        # Listar archivos en directorio de categorías
        category_files = [f for f in os.listdir(self.categories_path) if f.endswith(".json")]
        
        # Cargar categorías
        categories = []
        for file_name in category_files:
            category_id = file_name.replace(".json", "")
            category = self.get_category(category_id)
            if category:
                categories.append(category)
        
        return categories
    
    def get_category_tree(self, root_id: str = None) -> Dict[str, Any]:
        """
        Obtiene el árbol de categorías.
        
        Args:
            root_id: ID de la categoría raíz (opcional)
            
        Returns:
            Diccionario con el árbol de categorías
        """
        # Función recursiva para construir árbol
        def build_tree(category_id):
            category = self.get_category(category_id)
            if not category:
                return None
            
            tree = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "memory_count": len(category.memory_ids),
                "children": []
            }
            
            for child_id in category.children_ids:
                child_tree = build_tree(child_id)
                if child_tree:
                    tree["children"].append(child_tree)
            
            return tree
        
        # Si no se especifica raíz, construir bosque
        if not root_id:
            forest = []
            for category in self.list_categories():
                if not category.parent_id:
                    tree = build_tree(category.id)
                    if tree:
                        forest.append(tree)
            return {"categories": forest}
        
        # Construir árbol desde raíz
        tree = build_tree(root_id)
        if not tree:
            return {}
        
        return tree
    
    def add_to_category(self, item_id: str, category_id: str) -> bool:
        """
        Añade un elemento a una categoría.
        
        Args:
            item_id: ID del elemento
            category_id: ID de la categoría
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        # Verificar que el elemento existe
        item = self.get(item_id)
        if not item:
            logger.error(f"No se encontró elemento {item_id} para añadir a categoría")
            return False
        
        # Verificar que la categoría existe
        category = self.get_category(category_id)
        if not category:
            logger.error(f"No se encontró categoría {category_id}")
            return False
        
        # Añadir a categoría si no está ya
        if item_id not in category.memory_ids:
            category.memory_ids.append(item_id)
            self._save_category(category)
            logger.info(f"Elemento {item_id} añadido a categoría {category_id}")
        
        return True
    
    def remove_from_category(self, item_id: str, category_id: str) -> bool:
        """
        Elimina un elemento de una categoría.
        
        Args:
            item_id: ID del elemento
            category_id: ID de la categoría
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        # Verificar que la categoría existe
        category = self.get_category(category_id)
        if not category:
            logger.error(f"No se encontró categoría {category_id}")
            return False
        
        # Eliminar de categoría si está
        if item_id in category.memory_ids:
            category.memory_ids.remove(item_id)
            self._save_category(category)
            logger.info(f"Elemento {item_id} eliminado de categoría {category_id}")
        
        return True
    
    def list_category_items(self, category_id: str, recursive: bool = False) -> List[MemoryItem]:
        """
        Lista los elementos de una categoría.
        
        Args:
            category_id: ID de la categoría
            recursive: Si es True, incluye elementos de subcategorías
            
        Returns:
            Lista de elementos
        """
        # Verificar que la categoría existe
        category = self.get_category(category_id)
        if not category:
            logger.error(f"No se encontró categoría {category_id}")
            return []
        
        # Obtener IDs de elementos
        item_ids = set(category.memory_ids)
        
        # Incluir elementos de subcategorías si es recursivo
        if recursive:
            for child_id in category.children_ids:
                child_items = self.list_category_items(child_id, recursive=True)
                item_ids.update([item.id for item in child_items])
        
        # Obtener elementos
        items = []
        for item_id in item_ids:
            item = self.get(item_id)
            if item:
                items.append(item)
        
        return items
    
    def create_association(self, source_id: str, target_id: str, strength: float = 0.5) -> bool:
        """
        Crea una asociación entre dos elementos.
        
        Args:
            source_id: ID del elemento origen
            target_id: ID del elemento destino
            strength: Fuerza de la asociación (0.0-1.0)
            
        Returns:
            True si se creó correctamente, False en caso contrario
        """
        # Verificar que los elementos existen
        source = self.get(source_id)
        target = self.get(target_id)
        
        if not source or not target:
            logger.error(f"No se encontraron elementos para crear asociación: {source_id} -> {target_id}")
            return False
        
        # Crear asociación bidireccional
        source.associations[target_id] = strength
        target.associations[source_id] = strength
        
        # Guardar elementos
        self._save_item(source)
        self._save_item(target)
        
        logger.info(f"Asociación creada: {source_id} <-> {target_id} ({strength})")
        return True
    
    def get_associations(self, item_id: str, min_strength: float = 0.0) -> Dict[str, float]:
        """
        Obtiene las asociaciones de un elemento.
        
        Args:
            item_id: ID del elemento
            min_strength: Fuerza mínima de asociación
            
        Returns:
            Diccionario de asociaciones (ID -> fuerza)
        """
        # Verificar que el elemento existe
        item = self.get(item_id)
        if not item:
            logger.error(f"No se encontró elemento {item_id} para obtener asociaciones")
            return {}
        
        # Filtrar por fuerza mínima
        return {k: v for k, v in item.associations.items() if v >= min_strength}
    
    def get_associated_items(self, item_id: str, min_strength: float = 0.0,
                            limit: int = 10) -> List[Tuple[MemoryItem, float]]:
        """
        Obtiene los elementos asociados a un elemento.
        
        Args:
            item_id: ID del elemento
            min_strength: Fuerza mínima de asociación
            limit: Número máximo de elementos
            
        Returns:
            Lista de tuplas (elemento, fuerza)
        """
        # Obtener asociaciones
        associations = self.get_associations(item_id, min_strength)
        
        # Obtener elementos
        items = []
        for target_id, strength in associations.items():
            target = self.get(target_id)
            if target:
                items.append((target, strength))
        
        # Ordenar por fuerza
        items.sort(key=lambda x: x[1], reverse=True)
        
        # Limitar resultados
        return items[:limit]
    
    def consolidate_memories(self, threshold: float = 0.8, max_items: int = 100) -> int:
        """
        Consolida memorias similares.
        
        Args:
            threshold: Umbral de similitud para consolidación
            max_items: Número máximo de elementos a procesar
            
        Returns:
            Número de consolidaciones realizadas
        """
        # Verificar que hay embedding model
        if not self.embedding_model:
            logger.error("No hay modelo de embeddings para consolidar memorias")
            return 0
        
        # Obtener elementos con embeddings
        items_with_embeddings = []
        count = 0
        
        for item_id in self._list_all_item_ids():
            # Limitar número de elementos
            if count >= max_items:
                break
            
            # Obtener elemento
            item = self.get(item_id)
            if not item:
                continue
            
            # Verificar si tiene embedding
            if item.embedding or item.id in self.embedding_cache:
                if not item.embedding:
                    item.embedding = self.embedding_cache[item.id]
                
                items_with_embeddings.append(item)
                count += 1
            else:
                # Intentar cargar desde disco
                embedding_path = os.path.join(self.embeddings_path, f"{item.id}.npy")
                if os.path.exists(embedding_path):
                    try:
                        item.embedding = np.load(embedding_path).tolist()
                        self.embedding_cache[item.id] = item.embedding
                        items_with_embeddings.append(item)
                        count += 1
                    except Exception as e:
                        logger.error(f"Error al cargar embedding para elemento {item.id}: {e}")
        
        # Si no hay suficientes elementos, salir
        if len(items_with_embeddings) < 2:
            return 0
        
        # Buscar pares similares
        consolidations = 0
        processed_ids = set()
        
        for i in range(len(items_with_embeddings)):
            item1 = items_with_embeddings[i]
            
            # Si ya se procesó, saltar
            if item1.id in processed_ids:
                continue
            
            for j in range(i + 1, len(items_with_embeddings)):
                item2 = items_with_embeddings[j]
                
                # Si ya se procesó, saltar
                if item2.id in processed_ids:
                    continue
                
                # Calcular similitud
                similarity = self._cosine_similarity(item1.embedding, item2.embedding)
                
                # Si supera el umbral, consolidar
                if similarity >= threshold:
                    # Consolidar
                    self._consolidate_pair(item1, item2)
                    
                    # Marcar como procesados
                    processed_ids.add(item2.id)
                    
                    consolidations += 1
        
        logger.info(f"Consolidación de memorias completada: {consolidations} consolidaciones")
        return consolidations
    
    def _consolidate_pair(self, item1: MemoryItem, item2: MemoryItem) -> None:
        """
        Consolida un par de elementos.
        
        Args:
            item1: Primer elemento
            item2: Segundo elemento
        """
        # Determinar elemento principal (el más importante o reciente)
        if item1.importance > item2.importance:
            main_item, secondary_item = item1, item2
        elif item2.importance > item1.importance:
            main_item, secondary_item = item2, item1
        else:
            # Si tienen la misma importancia, usar el más reciente
            if item1.creation_time > item2.creation_time:
                main_item, secondary_item = item1, item2
            else:
                main_item, secondary_item = item2, item1
        
        # Actualizar elemento principal
        # - Combinar metadatos
        for key, value in secondary_item.metadata.items():
            if key not in main_item.metadata:
                main_item.metadata[key] = value
        
        # - Combinar tags
        main_item.tags = list(set(main_item.tags + secondary_item.tags))
        
        # - Actualizar importancia (promedio ponderado)
        total_importance = main_item.importance + secondary_item.importance
        main_item.importance = min(1.0, total_importance * 0.6)
        
        # - Combinar asociaciones
        for target_id, strength in secondary_item.associations.items():
            if target_id != main_item.id:
                if target_id in main_item.associations:
                    # Tomar el máximo
                    main_item.associations[target_id] = max(main_item.associations[target_id], strength)
                else:
                    main_item.associations[target_id] = strength
                
                # Actualizar asociación en el elemento destino
                target = self.get(target_id)
                if target:
                    if secondary_item.id in target.associations:
                        del target.associations[secondary_item.id]
                    target.associations[main_item.id] = strength
                    self._save_item(target)
        
        # - Añadir referencia al elemento secundario
        if "consolidated_from" not in main_item.metadata:
            main_item.metadata["consolidated_from"] = []
        main_item.metadata["consolidated_from"].append(secondary_item.id)
        
        # Guardar elemento principal
        self._save_item(main_item)
        
        # Mover elemento secundario a categorías del principal
        for category in self.list_categories():
            if secondary_item.id in category.memory_ids:
                category.memory_ids.remove(secondary_item.id)
                if main_item.id not in category.memory_ids:
                    category.memory_ids.append(main_item.id)
                self._save_category(category)
        
        # Eliminar elemento secundario
        self.delete(secondary_item.id)
        
        logger.info(f"Elementos consolidados: {main_item.id} <- {secondary_item.id}")
    
    def forget_old_memories(self, max_age_days: int = 365, 
                           importance_threshold: float = 0.3,
                           max_to_forget: int = 100) -> int:
        """
        Olvida memorias antiguas y poco importantes.
        
        Args:
            max_age_days: Edad máxima en días
            importance_threshold: Umbral de importancia
            max_to_forget: Número máximo de elementos a olvidar
            
        Returns:
            Número de elementos olvidados
        """
        # Calcular tiempo límite
        max_age_seconds = max_age_days * 24 * 60 * 60
        time_threshold = time.time() - max_age_seconds
        
        # Obtener elementos antiguos
        old_items = []
        
        for item_id in self._list_all_item_ids():
            # Obtener elemento
            item = self.get(item_id)
            if not item:
                continue
            
            # Verificar edad
            if item.creation_time < time_threshold:
                # Verificar importancia
                if item.importance < importance_threshold:
                    old_items.append(item)
        
        # Ordenar por importancia (menor primero)
        old_items.sort(key=lambda x: x.importance)
        
        # Limitar número de elementos
        old_items = old_items[:max_to_forget]
        
        # Olvidar elementos
        forgotten_count = 0
        for item in old_items:
            if self.delete(item.id):
                forgotten_count += 1
        
        logger.info(f"Olvido de memorias completado: {forgotten_count} elementos olvidados")
        return forgotten_count
    
    def backup(self, backup_dir: str = None) -> bool:
        """
        Realiza una copia de seguridad de la memoria.
        
        Args:
            backup_dir: Directorio de destino (opcional)
            
        Returns:
            True si se realizó correctamente, False en caso contrario
        """
        try:
            # Determinar directorio de destino
            if not backup_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(self.storage_path, f"backup_{timestamp}")
            
            # Crear directorio si no existe
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copiar directorios
            for subdir in ["items", "categories", "embeddings", "index"]:
                src_dir = os.path.join(self.storage_path, subdir)
                dst_dir = os.path.join(backup_dir, subdir)
                
                if os.path.exists(src_dir):
                    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            
            logger.info(f"Copia de seguridad realizada en {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Error al realizar copia de seguridad: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def restore(self, backup_dir: str) -> bool:
        """
        Restaura una copia de seguridad de la memoria.
        
        Args:
            backup_dir: Directorio de origen
            
        Returns:
            True si se restauró correctamente, False en caso contrario
        """
        try:
            # Verificar que el directorio existe
            if not os.path.exists(backup_dir):
                logger.error(f"No se encontró directorio de copia de seguridad: {backup_dir}")
                return False
            
            # Limpiar caché
            self.items_cache.clear()
            self.categories_cache.clear()
            self.embedding_cache.clear()
            
            # Copiar directorios
            for subdir in ["items", "categories", "embeddings", "index"]:
                src_dir = os.path.join(backup_dir, subdir)
                dst_dir = os.path.join(self.storage_path, subdir)
                
                if os.path.exists(src_dir):
                    # Eliminar directorio destino si existe
                    if os.path.exists(dst_dir):
                        shutil.rmtree(dst_dir)
                    
                    # Copiar directorio
                    shutil.copytree(src_dir, dst_dir)
            
            # Recargar índices
            self._load_indices()
            
            logger.info(f"Copia de seguridad restaurada desde {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Error al restaurar copia de seguridad: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la memoria.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Contar elementos
            item_count = len(os.listdir(self.items_path))
            
            # Contar categorías
            category_count = len(os.listdir(self.categories_path))
            
            # Calcular tamaño en disco
            total_size = 0
            for path, dirs, files in os.walk(self.storage_path):
                for f in files:
                    fp = os.path.join(path, f)
                    total_size += os.path.getsize(fp)
            
            # Convertir a MB
            total_size_mb = total_size / (1024 * 1024)
            
            # Obtener elementos más importantes
            important_items = []
            for item_id in self._list_all_item_ids()[:100]:  # Limitar a 100 para eficiencia
                item = self.get(item_id)
                if item:
                    important_items.append((item.id, item.importance))
            
            # Ordenar por importancia
            important_items.sort(key=lambda x: x[1], reverse=True)
            
            # Limitar a 10
            important_items = important_items[:10]
            
            # Estadísticas de categorías
            category_stats = []
            for category in self.list_categories():
                category_stats.append({
                    "id": category.id,
                    "name": category.name,
                    "item_count": len(category.memory_ids),
                    "has_children": len(category.children_ids) > 0
                })
            
            # Ordenar por número de elementos
            category_stats.sort(key=lambda x: x["item_count"], reverse=True)
            
            # Estadísticas de caché
            cache_stats = {
                "items_cache_size": len(self.items_cache),
                "categories_cache_size": len(self.categories_cache),
                "embedding_cache_size": len(self.embedding_cache)
            }
            
            # Estadísticas de índices
            index_stats = {
                "text_index_size": len(self.text_index),
                "tag_index_size": len(self.tag_index)
            }
            
            return {
                "item_count": item_count,
                "category_count": category_count,
                "total_size_mb": total_size_mb,
                "important_items": important_items,
                "top_categories": category_stats[:5],
                "cache_stats": cache_stats,
                "index_stats": index_stats,
                "last_updated": time.time()
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            logger.debug(traceback.format_exc())
            return {"error": str(e)}
