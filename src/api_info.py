#!/usr/bin/env python3
"""
Información de la API para VokaFlow
"""
from typing import Dict, Any
from datetime import datetime

class APIInfo:
    def __init__(self, app_name: str, version: str, description: str):
        self.app_name = app_name
        self.version = version
        self.description = description
        self.start_time = datetime.now()
    
    def get_api_info(self) -> Dict[str, Any]:
        """Obtiene información de la API"""
        return {
            "name": self.app_name,
            "version": self.version,
            "description": self.description,
            "endpoints_count": 136,  # Número total de endpoints
            "documentation": {
                "api_reference": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            },
            "changelog": [
                {
                    "version": "1.0.0",
                    "date": "2025-05-20",
                    "changes": ["Lanzamiento inicial de la API"]
                },
                {
                    "version": "0.9.5",
                    "date": "2025-05-15",
                    "changes": ["Mejoras en el manejo de errores"]
                },
                {
                    "version": "0.9.0",
                    "date": "2025-05-10",
                    "changes": ["Beta pública"]
                }
            ],
            "features": {
                "core": [
                    "Traducción de texto en tiempo real",
                    "Síntesis de voz con 10+ voces",
                    "Reconocimiento de voz multiidioma",
                    "Integración con Kinect para detección de movimiento",
                    "API RESTful completa",
                    "Gestión de usuarios y permisos",
                    "Autenticación OAuth2 y API Keys",
                    "Analíticas de uso en tiempo real",
                    "Soporte para múltiples idiomas",
                    "Documentación interactiva"
                ],
                "premium": [
                    "Voces personalizadas entrenadas con tu voz",
                    "Procesamiento de lenguaje natural avanzado",
                    "Análisis de sentimiento",
                    "Webhooks para integraciones",
                    "Acceso a modelos de IA de última generación"
                ]
            }
        }

# Función para inicializar la información de la API
def initialize_api_info(app_name: str, version: str, description: str) -> APIInfo:
    """Inicializa la información de la API"""
    return APIInfo(app_name, version, description)

# Instancia global
_api_info = None

# Función para obtener la instancia global
def get_api_info() -> APIInfo:
    """Obtiene la instancia global de API Info"""
    global _api_info
    if _api_info is None:
        _api_info = APIInfo("VokaFlow API", "1.0.0", "API para el sistema de comunicación VokaFlow")
    return _api_info
