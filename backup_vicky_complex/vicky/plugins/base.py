"""
Clase base para plugins de Vicky
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("vicky.plugins.base")

class Plugin:
    """
    Clase base para todos los plugins de Vicky.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """
        Inicializa el plugin.
        
        Args:
            name: Nombre del plugin
            config: Configuración del plugin
        """
        self.name = name
        self.config = config or {}
        self.enabled = True
        
        logger.info(f"Inicializando plugin {name}")
    
    def initialize(self) -> bool:
        """
        Inicializa el plugin.
        
        Returns:
            True si se inicializó correctamente, False en caso contrario
        """
        logger.info(f"Plugin {self.name} inicializado")
        return True
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Procesa un mensaje.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Respuesta generada o None si el plugin no procesa este mensaje
        """
        # Implementación base que no hace nada
        return None
    
    def shutdown(self) -> None:
        """Detiene el plugin."""
        logger.info(f"Plugin {self.name} detenido")
