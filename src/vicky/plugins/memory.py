"""
Plugin de memoria para Vicky
"""
import logging
import os
import json
from typing import Dict, Any, Optional, List
import re
import time

from .base import Plugin

logger = logging.getLogger("vicky.plugins.memory")

class MemoryPlugin(Plugin):
    """
    Plugin para gestión de memoria y recuerdos.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa el plugin de memoria.
        
        Args:
            config: Configuración del plugin
        """
        super().__init__("memory", config)
        
        # Configuración por defecto
        self.max_history = self.config.get("max_history", 100)
        self.vector_db_path = self.config.get("vector_db_path", "/mnt/nvme_fast/vokaflow_data/vector_db")
        
        # Asegurar que el directorio de la base de datos vectorial existe
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Patrones para detectar comandos de memoria
        self.memory_patterns = [
            r"^(?:recuerda|remember)(?:\s+esto)?\s*:\s*(.+)$",
            r"^(?:guarda|save)(?:\s+esto)?\s*:\s*(.+)$",
            r"^(?:olvida|forget)(?:\s+esto)?\s*:\s*(.+)$",
            r"^(?:qué sabes sobre|what do you know about)\s+(.+)$",
            r"^(?:busca|search)(?:\s+esto)?\s*:\s*(.+)$"
        ]
        
        # Cargar memoria
        self.memories = self._load_memories()
        
        logger.info("Plugin de memoria inicializado")
    
    def _load_memories(self) -> Dict[str, Any]:
        """
        Carga las memorias desde el almacenamiento.
        
        Returns:
            Diccionario con las memorias
        """
        memory_file = os.path.join(self.vector_db_path, "memories.json")
        if os.path.exists(memory_file):
            try:
                with open(memory_file, "r") as f:
                    memories = json.load(f)
                logger.info(f"Memorias cargadas desde {memory_file}")
                return memories
            except Exception as e:
                logger.error(f"Error al cargar memorias: {e}")
                return {}
        else:
            logger.info("No se encontró archivo de memorias, se creará uno nuevo")
            return {}
    
    def _save_memories(self) -> bool:
        """
        Guarda las memorias en el almacenamiento.
        
        Returns:
            True si se guardaron correctamente, False en caso contrario
        """
        memory_file = os.path.join(self.vector_db_path, "memories.json")
        try:
            with open(memory_file, "w") as f:
                json.dump(self.memories, f, indent=2)
            logger.info(f"Memorias guardadas en {memory_file}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar memorias: {e}")
            return False
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Procesa un mensaje para detectar y ejecutar comandos de memoria.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Respuesta o None si no es un comando de memoria
        """
        # Verificar si es un comando de memoria
        for pattern in self.memory_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                # Extraer contenido
                content = match.group(1).strip()
                
                # Determinar tipo de comando
                if re.match(r"^(?:recuerda|remember|guarda|save)", message, re.IGNORECASE):
                    return self._save_memory(content, context)
                elif re.match(r"^(?:olvida|forget)", message, re.IGNORECASE):
                    return self._forget_memory(content)
                elif re.match(r"^(?:qué sabes sobre|what do you know about|busca|search)", message, re.IGNORECASE):
                    return self._search_memory(content)
        
        return None
    
    def _save_memory(self, content: str, context: Dict[str, Any] = None) -> str:
        """
        Guarda un recuerdo.
        
        Args:
            content: Contenido a recordar
            context: Contexto adicional
            
        Returns:
            Mensaje de confirmación
        """
        # Generar ID único para el recuerdo
        memory_id = f"mem_{int(time.time())}_{len(self.memories) + 1}"
        
        # Crear recuerdo
        memory = {
            "id": memory_id,
            "content": content,
            "timestamp": time.time(),
            "context": context or {}
        }
        
        # Guardar recuerdo
        self.memories[memory_id] = memory
        self._save_memories()
        
        # Generar embedding para búsqueda semántica
        try:
            # Obtener el cerebro de Vicky
            from ..core.brain import VickyBrain
            brain = VickyBrain()
            
            # Obtener modelo de embeddings
            embedding_model = brain.model_manager.get_model("embedding")
            
            if embedding_model:
                # Generar embedding
                embedding = embedding_model.encode(content)
                
                # Guardar embedding
                embedding_file = os.path.join(self.vector_db_path, f"{memory_id}.npy")
                import numpy as np
                np.save(embedding_file, embedding)
        except Exception as e:
            logger.error(f"Error al generar embedding para recuerdo: {e}")
        
        return f"He guardado este recuerdo: '{content}'"
    
    def _forget_memory(self, content: str) -> str:
        """
        Elimina un recuerdo.
        
        Args:
            content: Contenido a olvidar
            
        Returns:
            Mensaje de confirmación
        """
        # Buscar recuerdos que coincidan con el contenido
        matches = []
        for memory_id, memory in self.memories.items():
            if content.lower() in memory["content"].lower():
                matches.append(memory_id)
        
        if not matches:
            return f"No encontré ningún recuerdo que contenga '{content}'"
        
        # Eliminar recuerdos
        for memory_id in matches:
            del self.memories[memory_id]
            
            # Eliminar embedding si existe
            embedding_file = os.path.join(self.vector_db_path, f"{memory_id}.npy")
            if os.path.exists(embedding_file):
                os.remove(embedding_file)
        
        self._save_memories()
        
        return f"He olvidado {len(matches)} recuerdo(s) que contenían '{content}'"
    
    def _search_memory(self, query: str) -> str:
        """
        Busca recuerdos relacionados con una consulta.
        
        Args:
            query: Consulta de búsqueda
            
        Returns:
            Resultados de la búsqueda
        """
        if not self.memories:
            return "No tengo ningún recuerdo almacenado"
        
        try:
            # Obtener el cerebro de Vicky
            from ..core.brain import VickyBrain
            brain = VickyBrain()
            
            # Obtener modelo de embeddings
            embedding_model = brain.model_manager.get_model("embedding")
            
            if embedding_model:
                # Generar embedding para la consulta
                query_embedding = embedding_model.encode(query)
                
                # Buscar recuerdos similares
                results = []
                for memory_id, memory in self.memories.items():
                    # Cargar embedding del recuerdo
                    embedding_file = os.path.join(self.vector_db_path, f"{memory_id}.npy")
                    if os.path.exists(embedding_file):
                        import numpy as np
                        memory_embedding = np.load(embedding_file)
                        
                        # Calcular similitud
                        from sklearn.metrics.pairwise import cosine_similarity
                        similarity = cosine_similarity([query_embedding], [memory_embedding])[0][0]
                        
                        # Añadir a resultados si supera umbral
                        if similarity > 0.5:
                            results.append((memory, similarity))
                
                # Ordenar por similitud
                results.sort(key=lambda x: x[1], reverse=True)
                
                # Limitar resultados
                results = results[:5]
                
                if not results:
                    return f"No encontré recuerdos relacionados con '{query}'"
                
                # Formatear resultados
                response = f"Esto es lo que sé sobre '{query}':\n\n"
                for memory, similarity in results:
                    response += f"- {memory['content']} (similitud: {similarity:.2f})\n"
                
                return response
        except Exception as e:
            logger.error(f"Error al buscar recuerdos: {e}")
        
        # Búsqueda de respaldo (texto simple)
        results = []
        for memory_id, memory in self.memories.items():
            if query.lower() in memory["content"].lower():
                results.append(memory)
        
        if not results:
            return f"No encontré recuerdos relacionados con '{query}'"
        
        # Formatear resultados
        response = f"Esto es lo que sé sobre '{query}':\n\n"
        for memory in results[:5]:
            response += f"- {memory['content']}\n"
        
        return response
