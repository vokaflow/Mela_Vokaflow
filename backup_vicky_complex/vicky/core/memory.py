"""
Sistema de memoria para Vicky
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import json
import os
import time

logger = logging.getLogger("vicky.memory")

class Memory:
    """
    Clase para gestionar la memoria de Vicky.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Inicializa la memoria.
        
        Args:
            storage_path: Ruta al directorio de almacenamiento
        """
        self.storage_path = storage_path or "/mnt/nvme_fast/vokaflow_data/memory"
        self.short_term = {}  # Memoria a corto plazo (en RAM)
        self.ensure_storage_path()
        
    def ensure_storage_path(self) -> None:
        """Asegura que el directorio de almacenamiento existe."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
    
    def store(self, key: str, value: Any, permanent: bool = False, collection: str = None) -> None:
        """
        Almacena un valor en la memoria.
        
        Args:
            key: Clave
            value: Valor
            permanent: Si es True, se almacena en la memoria a largo plazo
            collection: Colección donde almacenar (opcional)
        """
        # Si hay una colección, prefijar la clave
        if collection:
            key = f"{collection}_{key}"
            
        # Almacenar en memoria a corto plazo
        self.short_term[key] = value
        
        # Si es permanente, almacenar en disco
        if permanent:
            self._store_permanent(key, value)
    
    def _store_permanent(self, key: str, value: Any) -> None:
        """
        Almacena un valor en la memoria a largo plazo.
        
        Args:
            key: Clave
            value: Valor
        """
        try:
            # Crear directorio si no existe
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Almacenar en disco
            file_path = os.path.join(self.storage_path, f"{key}.json")
            with open(file_path, "w") as f:
                json.dump({
                    "value": value,
                    "timestamp": time.time()
                }, f)
        except Exception as e:
            logger.error(f"Error al almacenar en memoria permanente: {e}")
    
    def retrieve(self, key: str, default: Any = None, collection: str = None) -> Any:
        """
        Recupera un valor de la memoria.
        
        Args:
            key: Clave
            default: Valor por defecto si la clave no existe
            collection: Colección donde buscar (opcional)
            
        Returns:
            Valor asociado a la clave
        """
        # Si hay una colección, prefijar la clave
        if collection:
            key = f"{collection}_{key}"
            
        # Intentar recuperar de la memoria a corto plazo
        if key in self.short_term:
            return self.short_term[key]
        
        # Intentar recuperar de la memoria a largo plazo
        try:
            file_path = os.path.join(self.storage_path, f"{key}.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    # Almacenar en memoria a corto plazo para acceso más rápido
                    self.short_term[key] = data["value"]
                    return data["value"]
        except Exception as e:
            logger.error(f"Error al recuperar de memoria permanente: {e}")
        
        return default
    
    def forget(self, key: str) -> None:
        """
        Elimina un valor de la memoria.
        
        Args:
            key: Clave
        """
        # Eliminar de la memoria a corto plazo
        if key in self.short_term:
            del self.short_term[key]
        
        # Eliminar de la memoria a largo plazo
        try:
            file_path = os.path.join(self.storage_path, f"{key}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error al eliminar de memoria permanente: {e}")
    
    def list_keys(self, pattern: str = "*") -> List[str]:
        """
        Lista las claves en la memoria.
        
        Args:
            pattern: Patrón para filtrar las claves
            
        Returns:
            Lista de claves
        """
        keys = set(self.short_term.keys())
        
        # Añadir claves de la memoria a largo plazo
        try:
            import glob
            file_pattern = os.path.join(self.storage_path, f"{pattern.replace('*', '**')}.json")
            for file_path in glob.glob(file_pattern, recursive=True):
                key = os.path.basename(file_path).replace(".json", "")
                keys.add(key)
        except Exception as e:
            logger.error(f"Error al listar claves de memoria permanente: {e}")
        
        return list(keys)
    
    def get_all_keys(self) -> List[str]:
        """
        Obtiene todas las claves almacenadas en memoria.
        
        Returns:
            Lista de todas las claves
        """
        return self.list_keys()
    
    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una conversación.
        
        Args:
            conversation_id: ID de la conversación
            limit: Número máximo de mensajes a devolver
            
        Returns:
            Lista de mensajes de la conversación
        """
        history_key = f"conversation_history_{conversation_id}"
        history = self.retrieve(history_key, [])
        
        # Devolver solo los últimos 'limit' mensajes
        return history[-limit:] if len(history) > limit else history
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene las preferencias de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con las preferencias del usuario
        """
        prefs_key = f"user_preferences_{user_id}"
        return self.retrieve(prefs_key, {})
