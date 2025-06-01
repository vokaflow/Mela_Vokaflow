"""
Configuración de Vicky
"""
import os
import yaml
from typing import Dict, Any, Optional

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo YAML
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Diccionario con la configuración
    """
    # Usar la ruta proporcionada o la predeterminada
    path = config_path or os.environ.get("VICKY_CONFIG", "/opt/vokaflow/config/vicky.yaml")
    
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
        return {}

# Cargar configuración
config = load_config()
