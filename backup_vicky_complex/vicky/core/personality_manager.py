"""
Gestor de personalidades de Vicky AI
Carga y gestiona las configuraciones de personalidad desde archivos JSON
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class PersonalityManager:
    """
    Gestor de personalidades de Vicky AI
    """
    
    def __init__(self, personalities_dir: str = None):
        """
        Inicializa el gestor de personalidades
        
        Args:
            personalities_dir: Directorio donde están los archivos JSON de personalidades
        """
        self.personalities_dir = personalities_dir or self._get_default_personalities_dir()
        self.personalities: Dict[str, Dict[str, Any]] = {}
        self.current_personality = None
        self.load_personalities()
    
    def _get_default_personalities_dir(self) -> str:
        """
        Obtiene el directorio por defecto de personalidades
        """
        # Intentar encontrar el directorio de personalidades
        possible_paths = [
            "/opt/vokaflow/data/personality",
            "./data/personality",
            "../data/personality",
            "../../data/personality"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Si no encuentra ninguno, crear el directorio por defecto
        default_path = "/opt/vokaflow/data/personality"
        os.makedirs(default_path, exist_ok=True)
        return default_path
    
    def load_personalities(self):
        """
        Carga todas las personalidades desde archivos JSON
        """
        try:
            if not os.path.exists(self.personalities_dir):
                logger.warning(f"Directorio de personalidades no encontrado: {self.personalities_dir}")
                self._create_default_personality()
                return
            
            json_files = Path(self.personalities_dir).glob("*.json")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        personality_data = json.load(f)
                    
                    # Extraer nombre de la personalidad del archivo o del contenido
                    personality_name = personality_data.get('nombre', json_file.stem)
                    self.personalities[personality_name] = personality_data
                    
                    logger.info(f"Personalidad cargada: {personality_name}")
                    
                except Exception as e:
                    logger.error(f"Error al cargar personalidad {json_file}: {e}")
            
            # Establecer personalidad por defecto
            if self.personalities:
                default_personality = self._find_default_personality()
                self.set_personality(default_personality)
                logger.info(f"Personalidades cargadas: {len(self.personalities)}")
            else:
                logger.warning("No se encontraron personalidades válidas")
                self._create_default_personality()
                
        except Exception as e:
            logger.error(f"Error al cargar personalidades: {e}")
            self._create_default_personality()
    
    def _find_default_personality(self) -> str:
        """
        Encuentra la personalidad por defecto
        """
        # Prioridades para personalidad por defecto
        preferred_names = [
            "Vicky_Sistema_Conversacional_Emocional",
            "Vicky_Autosupervision_Backend", 
            "Sistema de Evaluación y Evolución Continua"
        ]
        
        for name in preferred_names:
            if name in self.personalities:
                return name
        
        # Si no encuentra ninguna preferida, usar la primera disponible
        return list(self.personalities.keys())[0] if self.personalities else "default"
    
    def _create_default_personality(self):
        """
        Crea una personalidad por defecto si no hay ninguna disponible
        """
        default_personality = {
            "nombre": "Vicky Default",
            "version": "1.0.0",
            "descripcion": "Personalidad por defecto de Vicky AI",
            "caracteristicas": {
                "nivel_tecnico": 0.7,
                "nivel_emocional": 0.6,
                "estilo_comunicacion": "profesional_amigable",
                "especializaciones": ["asistencia_general", "backend_management"],
                "capacidades": {
                    "procesamiento_lenguaje": True,
                    "gestion_backend": True,
                    "analisis_emocional": True,
                    "aprendizaje_continuo": True
                }
            },
            "configuracion": {
                "respuesta_maxima_longitud": 2000,
                "nivel_detalle_respuestas": "medio",
                "usar_emojis": True,
                "idioma_preferido": "es"
            }
        }
        
        self.personalities["default"] = default_personality
        self.current_personality = "default"
        logger.info("Personalidad por defecto creada")
    
    def set_personality(self, personality_name: str) -> bool:
        """
        Establece la personalidad activa
        
        Args:
            personality_name: Nombre de la personalidad
            
        Returns:
            True si se pudo establecer la personalidad
        """
        if personality_name in self.personalities:
            self.current_personality = personality_name
            logger.info(f"Personalidad activa: {personality_name}")
            return True
        else:
            logger.warning(f"Personalidad no encontrada: {personality_name}")
            return False
    
    def get_current_personality(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de la personalidad actual
        """
        if self.current_personality and self.current_personality in self.personalities:
            return self.personalities[self.current_personality]
        return None
    
    def get_personality_names(self) -> List[str]:
        """
        Obtiene la lista de nombres de personalidades disponibles
        """
        return list(self.personalities.keys())
    
    def get_personality_characteristic(self, characteristic: str, default_value=None):
        """
        Obtiene una característica específica de la personalidad actual
        
        Args:
            characteristic: Nombre de la característica (ej: 'nivel_tecnico')
            default_value: Valor por defecto si no se encuentra
        """
        personality = self.get_current_personality()
        if not personality:
            return default_value
        
        # Buscar en diferentes niveles de anidamiento
        paths = [
            f"caracteristicas.{characteristic}",
            f"configuracion.{characteristic}",
            characteristic
        ]
        
        for path in paths:
            value = self._get_nested_value(personality, path)
            if value is not None:
                return value
        
        return default_value
    
    def _get_nested_value(self, data: Dict, path: str):
        """
        Obtiene un valor anidado usando notación de punto
        """
        keys = path.split('.')
        current = data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def get_response_style(self) -> Dict[str, Any]:
        """
        Obtiene el estilo de respuesta de la personalidad actual
        """
        personality = self.get_current_personality()
        if not personality:
            return {
                "estilo": "profesional",
                "longitud_maxima": 1000,
                "usar_emojis": False,
                "nivel_detalle": "medio"
            }
        
        return {
            "estilo": self.get_personality_characteristic("estilo_comunicacion", "profesional"),
            "longitud_maxima": self.get_personality_characteristic("respuesta_maxima_longitud", 1000),
            "usar_emojis": self.get_personality_characteristic("usar_emojis", False),
            "nivel_detalle": self.get_personality_characteristic("nivel_detalle_respuestas", "medio"),
            "idioma": self.get_personality_characteristic("idioma_preferido", "es")
        }
    
    def get_hemisphere_balance(self) -> Dict[str, float]:
        """
        Obtiene el balance de hemisferios de la personalidad actual
        """
        personality = self.get_current_personality()
        if not personality:
            return {"technical": 0.6, "emotional": 0.4}
        
        technical = self.get_personality_characteristic("nivel_tecnico", 0.6)
        emotional = self.get_personality_characteristic("nivel_emocional", 0.4)
        
        # Normalizar para que sumen 1.0
        total = technical + emotional
        if total > 0:
            technical = technical / total
            emotional = emotional / total
        
        return {"technical": technical, "emotional": emotional}
    
    def reload_personalities(self):
        """
        Recarga todas las personalidades desde disco
        """
        old_current = self.current_personality
        self.personalities.clear()
        self.load_personalities()
        
        # Intentar restaurar la personalidad anterior
        if old_current and old_current in self.personalities:
            self.set_personality(old_current)
        
        logger.info("Personalidades recargadas")
