"""
Gestión de estado para Vicky
"""
import logging
from typing import Dict, Any, List, Optional
import json
import os
import time

logger = logging.getLogger("vicky.state")

class State:
    """
    Clase para gestionar el estado de Vicky.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Inicializa el estado.
        
        Args:
            storage_path: Ruta al directorio de almacenamiento
        """
        self.storage_path = storage_path or "/cache/vokaflow_data/state"
        self.state = {}
        self.ensure_storage_path()
        self.load()
        
    def ensure_storage_path(self) -> None:
        """Asegura que el directorio de almacenamiento existe."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
    
    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor en el estado.
        
        Args:
            key: Clave
            value: Valor
        """
        self.state[key] = value
        self.save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del estado.
        
        Args:
            key: Clave
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor asociado a la clave
        """
        return self.state.get(key, default)
    
    def delete(self, key: str) -> None:
        """
        Elimina un valor del estado.
        
        Args:
            key: Clave
        """
        if key in self.state:
            del self.state[key]
            self.save()
    
    def save(self) -> None:
        """Guarda el estado en disco."""
        try:
            file_path = os.path.join(self.storage_path, "state.json")
            with open(file_path, "w") as f:
                json.dump({
                    "state": self.state,
                    "timestamp": time.time()
                }, f)
        except Exception as e:
            logger.error(f"Error al guardar estado: {e}")
    
    def load(self) -> None:
        """Carga el estado desde disco."""
        try:
            file_path = os.path.join(self.storage_path, "state.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    self.state = data.get("state", {})
                    logger.info(f"Estado cargado desde {file_path}")
            else:
                logger.info("No se encontró archivo de estado, se utilizará un estado vacío")
        except Exception as e:
            logger.error(f"Error al cargar estado: {e}")
    
    def reset(self) -> None:
        """Reinicia el estado."""
        self.state = {}
        self.save()
        logger.info("Estado reiniciado")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Obtiene todo el estado.
        
        Returns:
            Diccionario con todo el estado
        """
        return self.state.copy()
