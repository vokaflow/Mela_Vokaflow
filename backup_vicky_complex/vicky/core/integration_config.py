"""
Configuración de Integración para VokaFlow
-----------------------------------------

Este módulo proporciona funcionalidades para gestionar la configuración
de integración entre los componentes del sistema VokaFlow.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import os
import json
import logging
import yaml
from typing import Dict, Any, List, Optional

# Configurar logger
logger = logging.getLogger("vicky.integration.config")

class IntegrationConfig:
    """
    Gestor de configuración para la integración de componentes en VokaFlow.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.config_path = config_path or os.environ.get(
            "INTEGRATION_CONFIG", 
            "/opt/vokaflow/config/integration.yaml"
        )
        
        # Configuración por defecto
        self.default_config = {
            "model_integration": {
                "auto_load_models": True,
                "preload_models": ["language", "embedding"],
                "model_timeout": 30,  # segundos
                "fallback_models": {
                    "language": "qwen",
                    "embedding": "sentence-transformers"
                }
            },
            "personality_integration": {
                "auto_load_personality": True,
                "default_personality": "Vicky_Personalidad_Estándar.json",
                "default_conversation_style": "Vicky_Estilo_Profesional.json",
                "default_cognitive_abilities": "Vicky_Capacidades_Completas.json"
            },
            "dual_brain": {
                "default_technical_weight": 0.5,
                "default_emotional_weight": 0.5,
                "default_combination_strategy": "integrated",
                "parallel_processing": True,
                "max_processing_time": 60  # segundos
            },
            "performance": {
                "cache_responses": True,
                "cache_size": 100,
                "log_performance_metrics": True,
                "optimize_for_latency": False,
                "optimize_for_quality": True
            },
            "error_handling": {
                "fallback_enabled": True,
                "max_retries": 2,
                "log_detailed_errors": True
            }
        }
        
        # Cargar configuración
        self.config = self._load_config()
        
        logger.info("Configuración de integración inicializada")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo YAML.
        
        Returns:
            Diccionario con la configuración
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f)
                
                # Combinar con configuración por defecto
                merged_config = self._merge_configs(self.default_config, config)
                logger.info(f"Configuración cargada desde {self.config_path}")
                return merged_config
            else:
                logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
                logger.info("Utilizando configuración por defecto")
                return self.default_config
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            return self.default_config
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combina dos diccionarios de configuración, manteniendo la estructura anidada.
        
        Args:
            default: Configuración por defecto
            override: Configuración que sobrescribe
            
        Returns:
            Configuración combinada
        """
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config(self, section: str = None, key: str = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            section: Sección de configuración (opcional)
            key: Clave de configuración (opcional)
            
        Returns:
            Valor de configuración o diccionario completo
        """
        if section is None:
            return self.config
        
        if section not in self.config:
            logger.warning(f"Sección de configuración no encontrada: {section}")
            return {}
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            logger.warning(f"Clave de configuración no encontrada: {section}.{key}")
            return None
        
        return self.config[section][key]
    
    def update_config(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        Actualiza la configuración.
        
        Args:
            updates: Diccionario con actualizaciones
            save: Si True, guarda la configuración en disco
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Actualizar configuración en memoria
            self.config = self._merge_configs(self.config, updates)
            
            # Guardar en disco si se solicita
            if save:
                return self.save_config()
            
            return True
        except Exception as e:
            logger.error(f"Error al actualizar configuración: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Guarda la configuración en disco.
        
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Guardar configuración
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Configuración guardada en {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar configuración: {e}")
            return False
    
    def reset_to_default(self, section: str = None) -> bool:
        """
        Restablece la configuración a los valores por defecto.
        
        Args:
            section: Sección a restablecer (opcional, si es None se restablece todo)
            
        Returns:
            True si se restableció correctamente, False en caso contrario
        """
        try:
            if section is None:
                self.config = self.default_config.copy()
            elif section in self.config and section in self.default_config:
                self.config[section] = self.default_config[section].copy()
            else:
                logger.warning(f"Sección de configuración no encontrada: {section}")
                return False
            
            logger.info(f"Configuración restablecida: {section or 'completa'}")
            return True
        except Exception as e:
            logger.error(f"Error al restablecer configuración: {e}")
            return False
