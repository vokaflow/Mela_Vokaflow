"""
Servicio de Memoria para Vicky
------------------------------

Este servicio proporciona una interfaz para interactuar con el sistema
de memoria a largo plazo de Vicky, facilitando el almacenamiento,
recuperación y gestión de información importante.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime
import traceback

from ..core.memory import Memory
from ..memory.long_term_memory import LongTermMemory, MemoryItem, MemoryCategory, MemorySearchResult

# Configurar logger
logger = logging.getLogger("vicky.services.memory")

class MemoryService:
    """
    Servicio para gestionar la memoria a largo plazo de Vicky.
    
    Este servicio proporciona una interfaz de alto nivel para:
    1. Almacenar información importante
    2. Recuperar información relevante
    3. Organizar la información en categorías
    4. Gestionar asociaciones entre elementos
    5. Realizar mantenimiento de la memoria
    """
    
    def __init__(self, short_term_memory: Memory = None, 
                long_term_memory: LongTermMemory = None,
                embedding_model = None):
        """
        Inicializa el servicio de memoria.
        
        Args:
            short_term_memory: Sistema de memoria a corto plazo
            long_term_memory: Sistema de memoria a largo plazo
            embedding_model: Modelo para generar embeddings
        """
        # Inicializar memorias
        self.short_term = short_term_memory or Memory()
        self.long_term = long_term_memory or LongTermMemory(embedding_model=embedding_model)
        self.embedding_model = embedding_model
        
        # Configuración
        self.auto_consolidation = True
        self.auto_consolidation_interval = 24 * 60 * 60  # 24 horas
        self.auto_forget = True
        self.auto_forget_interval = 7 * 24 * 60 * 60  # 7 días
        
        # Último mantenimiento
        self.last_consolidation = time.time()
        self.last_forget = time.time()
        
        logger.info("Servicio de memoria inicializado")
    
    def remember(self, content: str, metadata: Dict[str, Any] = None, 
                importance: float = 0.5, tags: List[str] = None, 
                category: str = None, permanent: bool = True) -> str:
        """
        Almacena información en la memoria.
        
        Args:
            content: Contenido a recordar
            metadata: Metadatos adicionales
            importance: Importancia (0.0-1.0)
            tags: Lista de tags
            category: Nombre de categoría (se crea si no existe)
            permanent: Si es True, se almacena en memoria a largo plazo
            
        Returns:
            ID del elemento almacenado
        """
        try:
            # Almacenar en memoria a corto plazo
            self.short_term.store(f"memory_{int(time.time())}", {
                "content": content,
                "metadata": metadata,
                "importance": importance,
                "tags": tags,
                "timestamp": time.time()
            }, permanent=False)
            
            # Si es permanente, almacenar en memoria a largo plazo
            if permanent:
                # Resolver categoría
                category_id = None
                if category:
                    # Buscar categoría por nombre
                    for cat in self.long_term.list_categories():
                        if cat.name.lower() == category.lower():
                            category_id = cat.id
                            break
                    
                    # Si no existe, crearla
                    if not category_id:
                        category_id = self.long_term.create_category(category)
                
                # Almacenar en memoria a largo plazo
                memory_id = self.long_term.store(
                    content=content,
                    metadata=metadata,
                    importance=importance,
                    tags=tags,
                    category_id=category_id
                )
                
                # Ejecutar mantenimiento si es necesario
                self._check_maintenance()
                
                return memory_id
            
            return f"st_{int(time.time())}"
        except Exception as e:
            logger.error(f"Error al almacenar en memoria: {e}")
            logger.debug(traceback.format_exc())
            return ""
    
    def recall(self, query: str, limit: int = 5, include_short_term: bool = True,
              categories: List[str] = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera información de la memoria.
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            include_short_term: Si es True, incluye resultados de la memoria a corto plazo
            categories: Lista de nombres de categorías para filtrar
            tags: Lista de tags para filtrar
            
        Returns:
            Lista de resultados
        """
        try:
            results = []
            
            # Buscar en memoria a largo plazo
            # Convertir nombres de categorías a IDs
            category_ids = None
            if categories:
                category_ids = []
                for category_name in categories:
                    for cat in self.long_term.list_categories():
                        if cat.name.lower() == category_name.lower():
                            category_ids.append(cat.id)
                            break
            
            # Realizar búsqueda
            lt_results = self.long_term.search(
                query=query,
                limit=limit,
                categories=category_ids,
                tags=tags
            )
            
            # Convertir resultados
            for result in lt_results:
                results.append({
                    "id": result.item.id,
                    "content": result.item.content,
                    "score": result.score,
                    "category": result.category,
                    "tags": result.item.tags,
                    "importance": result.item.importance,
                    "creation_time": result.item.creation_time,
                    "source": "long_term"
                })
            
            # Buscar en memoria a corto plazo si se solicita
            if include_short_term:
                # Obtener todas las claves que empiezan con "memory_"
                memory_keys = [k for k in self.short_term.list_keys() if k.startswith("memory_")]
                
                # Obtener elementos
                st_items = []
                for key in memory_keys:
                    item_data = self.short_term.retrieve(key)
                    if item_data:
                        # Filtrar por tags si se especifican
                        if tags and not any(tag in item_data.get("tags", []) for tag in tags):
                            continue
                        
                        # Calcular puntuación simple (coincidencia de palabras)
                        content = item_data.get("content", "")
                        query_words = set(query.lower().split())
                        content_words = set(content.lower().split())
                        matching_words = query_words.intersection(content_words)
                        
                        if matching_words:
                            score = len(matching_words) / len(query_words)
                            
                            # Si supera umbral mínimo, añadir a resultados
                            if score >= 0.3:
                                st_items.append({
                                    "id": key,
                                    "content": content,
                                    "score": score,
                                    "category": None,
                                    "tags": item_data.get("tags", []),
                                    "importance": item_data.get("importance", 0.5),
                                    "creation_time": item_data.get("timestamp", time.time()),
                                    "source": "short_term"
                                })
                
                # Ordenar por puntuación
                st_items.sort(key=lambda x: x["score"], reverse=True)
                
                # Añadir a resultados
                results.extend(st_items[:limit])
            
            # Ordenar resultados combinados por puntuación
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # Limitar resultados
            return results[:limit]
        except Exception as e:
            logger.error(f"Error al recuperar de memoria: {e}")
            logger.debug(traceback.format_exc())
            return []
    
    def forget(self, item_id: str) -> bool:
        """
        Elimina información de la memoria.
        
        Args:
            item_id: ID del elemento
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Determinar tipo de memoria
            if item_id.startswith("mem_"):
                # Memoria a largo plazo
                return self.long_term.delete(item_id)
            elif item_id.startswith("st_") or item_id.startswith("memory_"):
                # Memoria a corto plazo
                self.short_term.forget(item_id)
                return True
            else:
                logger.error(f"Tipo de ID de memoria desconocido: {item_id}")
                return False
        except Exception as e:
            logger.error(f"Error al olvidar memoria: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def create_memory_category(self, name: str, description: str = "",
                              parent: str = None) -> str:
        """
        Crea una categoría de memoria.
        
        Args:
            name: Nombre de la categoría
            description: Descripción de la categoría
            parent: Nombre de la categoría padre
            
        Returns:
            ID de la categoría creada
        """
        try:
            # Resolver categoría padre
            parent_id = None
            if parent:
                for cat in self.long_term.list_categories():
                    if cat.name.lower() == parent.lower():
                        parent_id = cat.id
                        break
            
            # Crear categoría
            return self.long_term.create_category(
                name=name,
                description=description,
                parent_id=parent_id
            )
        except Exception as e:
            logger.error(f"Error al crear categoría de memoria: {e}")
            logger.debug(traceback.format_exc())
            return ""
    
    def get_memory_categories(self) -> List[Dict[str, Any]]:
        """
        Obtiene las categorías de memoria.
        
        Returns:
            Lista de categorías
        """
        try:
            # Obtener categorías
            categories = self.long_term.list_categories()
            
            # Convertir a diccionarios
            return [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description,
                    "parent_id": cat.parent_id,
                    "item_count": len(cat.memory_ids)
                }
                for cat in categories
            ]
        except Exception as e:
            logger.error(f"Error al obtener categorías de memoria: {e}")
            logger.debug(traceback.format_exc())
            return []
    
    def get_memory_category_tree(self) -> Dict[str, Any]:
        """
        Obtiene el árbol de categorías de memoria.
        
        Returns:
            Árbol de categorías
        """
        try:
            return self.long_term.get_category_tree()
        except Exception as e:
            logger.error(f"Error al obtener árbol de categorías: {e}")
            logger.debug(traceback.format_exc())
            return {"categories": []}
    
    def associate_memories(self, source_id: str, target_id: str, 
                          strength: float = 0.5) -> bool:
        """
        Asocia dos elementos de memoria.
        
        Args:
            source_id: ID del elemento origen
            target_id: ID del elemento destino
            strength: Fuerza de la asociación (0.0-1.0)
            
        Returns:
            True si se asoció correctamente, False en caso contrario
        """
        try:
            return self.long_term.create_association(
                source_id=source_id,
                target_id=target_id,
                strength=strength
            )
        except Exception as e:
            logger.error(f"Error al asociar memorias: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def get_related_memories(self, item_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene elementos de memoria relacionados.
        
        Args:
            item_id: ID del elemento
            limit: Número máximo de resultados
            
        Returns:
            Lista de elementos relacionados
        """
        try:
            # Obtener elementos asociados
            related_items = self.long_term.get_associated_items(
                item_id=item_id,
                limit=limit
            )
            
            # Convertir a diccionarios
            return [
                {
                    "id": item.id,
                    "content": item.content,
                    "strength": strength,
                    "tags": item.tags,
                    "importance": item.importance,
                    "creation_time": item.creation_time
                }
                for item, strength in related_items
            ]
        except Exception as e:
            logger.error(f"Error al obtener memorias relacionadas: {e}")
            logger.debug(traceback.format_exc())
            return []
    
    def _check_maintenance(self) -> None:
        """
        Verifica si es necesario realizar mantenimiento de la memoria.
        """
        current_time = time.time()
        
        # Verificar consolidación
        if self.auto_consolidation and (current_time - self.last_consolidation) >= self.auto_consolidation_interval:
            # Ejecutar consolidación en segundo plano
            self.long_term._enqueue_task(self._run_consolidation)
            self.last_consolidation = current_time
        
        # Verificar olvido
        if self.auto_forget and (current_time - self.last_forget) >= self.auto_forget_interval:
            # Ejecutar olvido en segundo plano
            self.long_term._enqueue_task(self._run_forget)
            self.last_forget = current_time
    
    def _run_consolidation(self) -> None:
        """
        Ejecuta consolidación de memoria.
        """
        try:
            logger.info("Iniciando consolidación de memoria")
            consolidated = self.long_term.consolidate_memories()
            logger.info(f"Consolidación de memoria completada: {consolidated} consolidaciones")
        except Exception as e:
            logger.error(f"Error en consolidación de memoria: {e}")
            logger.debug(traceback.format_exc())
    
    def _run_forget(self) -> None:
        """
        Ejecuta olvido de memoria.
        """
        try:
            logger.info("Iniciando olvido de memoria")
            forgotten = self.long_term.forget_old_memories()
            logger.info(f"Olvido de memoria completado: {forgotten} elementos olvidados")
        except Exception as e:
            logger.error(f"Error en olvido de memoria: {e}")
            logger.debug(traceback.format_exc())
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la memoria.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Obtener estadísticas de memoria a largo plazo
            lt_stats = self.long_term.get_stats()
            
            # Obtener estadísticas de memoria a corto plazo
            st_keys = self.short_term.list_keys()
            st_memory_keys = [k for k in st_keys if k.startswith("memory_")]
            
            # Combinar estadísticas
            return {
                "long_term": lt_stats,
                "short_term": {
                    "total_items": len(st_keys),
                    "memory_items": len(st_memory_keys)
                },
                "last_consolidation": self.last_consolidation,
                "last_forget": self.last_forget,
                "auto_consolidation": self.auto_consolidation,
                "auto_forget": self.auto_forget
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de memoria: {e}")
            logger.debug(traceback.format_exc())
            return {"error": str(e)}
    
    def backup_memory(self, backup_dir: str = None) -> bool:
        """
        Realiza una copia de seguridad de la memoria.
        
        Args:
            backup_dir: Directorio de destino (opcional)
            
        Returns:
            True si se realizó correctamente, False en caso contrario
        """
        try:
            return self.long_term.backup(backup_dir)
        except Exception as e:
            logger.error(f"Error al realizar copia de seguridad: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def restore_memory(self, backup_dir: str) -> bool:
        """
        Restaura una copia de seguridad de la memoria.
        
        Args:
            backup_dir: Directorio de origen
            
        Returns:
            True si se restauró correctamente, False en caso contrario
        """
        try:
            return self.long_term.restore(backup_dir)
        except Exception as e:
            logger.error(f"Error al restaurar copia de seguridad: {e}")
            logger.debug(traceback.format_exc())
            return False
