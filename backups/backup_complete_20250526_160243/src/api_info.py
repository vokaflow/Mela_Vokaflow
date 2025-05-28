"""
Información de la API VokaFlow
"""
from datetime import datetime
from typing import Dict, Any

class APIInfo:
    def __init__(self, app_name: str, version: str, description: str):
        self.app_name = app_name
        self.version = version
        self.description = description
        
    def get_api_info(self) -> Dict[str, Any]:
        """Obtiene información de la API"""
        return {
            "name": self.app_name,
            "version": self.version,
            "description": self.description,
            "endpoints_count": 25,
            "features": {
                "core": [
                    "Traducción automática",
                    "Text-to-Speech",
                    "Speech-to-Text", 
                    "Asistente Vicky",
                    "Gestión de usuarios"
                ]
            },
            "documentation": {
                "api_reference": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            },
            "changelog": [
                {
                    "version": "1.0.0",
                    "date": "2024-05-25",
                    "changes": ["Lanzamiento inicial"]
                }
            ]
        }

# Instancia global
_api_info = None

def initialize_api_info(app_name: str, version: str, description: str):
    """Inicializa la información de la API"""
    global _api_info
    _api_info = APIInfo(app_name, version, description)
    return _api_info

def get_api_info():
    """Obtiene la instancia de información de la API"""
    return _api_info
