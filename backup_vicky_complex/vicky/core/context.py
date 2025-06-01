"""
Gestión de contexto para Vicky
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("vicky.context")

class Context:
    """
    Clase para gestionar el contexto de una conversación.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Inicializa el contexto.
        
        Args:
            max_history: Número máximo de mensajes a mantener en el historial
        """
        self.max_history = max_history
        self.history = []
        self.metadata = {}
        
    def add_message(self, role: str, content: str) -> None:
        """
        Añade un mensaje al historial.
        
        Args:
            role: Rol del mensaje (user, assistant)
            content: Contenido del mensaje
        """
        self.history.append({"role": role, "content": content})
        
        # Limitar el historial al tamaño máximo
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Obtiene el historial de mensajes.
        
        Returns:
            Lista de mensajes
        """
        return self.history
    
    def clear_history(self) -> None:
        """Limpia el historial de mensajes."""
        self.history = []
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Establece un valor en los metadatos.
        
        Args:
            key: Clave
            value: Valor
        """
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de los metadatos.
        
        Args:
            key: Clave
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor asociado a la clave
        """
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el contexto a un diccionario.
        
        Returns:
            Diccionario con el contexto
        """
        return {
            "history": self.history,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """
        Crea un contexto a partir de un diccionario.
        
        Args:
            data: Diccionario con los datos del contexto
            
        Returns:
            Instancia de Context
        """
        context = cls()
        context.history = data.get("history", [])
        context.metadata = data.get("metadata", {})
        return context

    def get_global_context(self) -> Dict[str, Any]:
        """
        Obtiene el contexto global del sistema.
        
        Returns:
            Diccionario con contexto global
        """
        return {
            "history_size": len(self.history),
            "metadata": self.metadata.copy(),
            "last_interaction": self.history[-1] if self.history else None
        }
        
    def get_size(self) -> int:
        """
        Obtiene el tamaño actual del contexto.
        
        Returns:
            Número de mensajes en el historial
        """
        return len(self.history)
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del contexto (metadatos o propiedades especiales).
        
        Args:
            key: Clave a buscar
            default: Valor por defecto
            
        Returns:
            Valor encontrado o valor por defecto
        """
        # Buscar primero en metadatos
        if key in self.metadata:
            return self.metadata[key]
        
        # Propiedades especiales del contexto
        if key == "history":
            return self.history
        elif key == "history_size":
            return len(self.history)
        elif key == "last_message":
            return self.history[-1] if self.history else None
        
        return default
