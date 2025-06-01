"""
Cargador de Personalidades JSON para Vicky
Lee todos los archivos JSON de personalidades y los integra en el sistema
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("vicky.personality_loader")

@dataclass
class PersonalityConfig:
    """Configuración de una personalidad de Vicky"""
    name: str
    display_name: str
    description: str
    technical_ratio: float
    emotional_ratio: float
    specialization: str
    characteristics: List[str]
    use_cases: List[str]
    model_preferences: Dict[str, str]
    response_style: Dict[str, Any]
    json_source: str

class VickyPersonalityLoader:
    """
    Carga y gestiona todas las personalidades de Vicky desde archivos JSON
    """
    
    def __init__(self, personalities_dir: str = "data/personality"):
        self.personalities_dir = Path(personalities_dir)
        self.personalities: Dict[str, PersonalityConfig] = {}
        self.raw_personalities: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"🎭 Inicializando cargador de personalidades desde: {personalities_dir}")
        
        # Cargar todas las personalidades
        self._load_all_personalities()
        
    def _load_all_personalities(self):
        """Carga todas las personalidades JSON disponibles"""
        try:
            if not self.personalities_dir.exists():
                logger.error(f"❌ Directorio de personalidades no encontrado: {self.personalities_dir}")
                return
            
            json_files = list(self.personalities_dir.glob("*.json"))
            logger.info(f"📁 Encontrados {len(json_files)} archivos de personalidades")
            
            for json_file in json_files:
                try:
                    self._load_personality_from_file(json_file)
                except Exception as e:
                    logger.error(f"❌ Error cargando {json_file.name}: {e}")
            
            logger.info(f"✅ Cargadas {len(self.personalities)} personalidades exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error general cargando personalidades: {e}")
    
    def _load_personality_from_file(self, json_file: Path):
        """Carga una personalidad específica desde archivo JSON"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Guardar datos raw para acceso completo
            file_key = json_file.stem
            self.raw_personalities[file_key] = data
            
            # Crear configuración de personalidad
            personality_config = self._parse_personality_json(data, json_file.name)
            
            if personality_config:
                self.personalities[file_key] = personality_config
                logger.info(f"✅ Personalidad cargada: {personality_config.display_name}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando {json_file.name}: {e}")
    
    def _parse_personality_json(self, data: Dict[str, Any], filename: str) -> Optional[PersonalityConfig]:
        """Convierte datos JSON en configuración de personalidad"""
        try:
            # Extraer información básica
            name = data.get("nombre", filename.replace(".json", ""))
            display_name = name
            description = data.get("objetivo", "Personalidad especializada de Vicky")
            
            # Determinar ratios técnico/emocional basado en el contenido
            technical_ratio, emotional_ratio = self._analyze_personality_balance(data, filename)
            
            # Determinar especialización
            specialization = self._determine_specialization(data, filename)
            
            # Extraer características
            characteristics = self._extract_characteristics(data)
            
            # Casos de uso
            use_cases = self._extract_use_cases(data)
            
            # Preferencias de modelo
            model_preferences = self._determine_model_preferences(data, specialization)
            
            # Estilo de respuesta
            response_style = self._extract_response_style(data)
            
            return PersonalityConfig(
                name=filename.replace(".json", "").lower(),
                display_name=display_name,
                description=description,
                technical_ratio=technical_ratio,
                emotional_ratio=emotional_ratio,
                specialization=specialization,
                characteristics=characteristics,
                use_cases=use_cases,
                model_preferences=model_preferences,
                response_style=response_style,
                json_source=filename
            )
            
        except Exception as e:
            logger.error(f"❌ Error analizando personalidad {filename}: {e}")
            return None
    
    def _analyze_personality_balance(self, data: Dict[str, Any], filename: str) -> tuple[float, float]:
        """Analiza el contenido para determinar balance técnico/emocional"""
        
        # Indicadores técnicos en el contenido
        technical_indicators = [
            "sistema", "arquitectura", "optimización", "rendimiento", "latencia",
            "infraestructura", "monitoreo", "análisis", "algoritmo", "eficiencia",
            "escalabilidad", "código", "desarrollo", "backend", "api", "database",
            "security", "devops", "machine learning", "ai", "neural"
        ]
        
        # Indicadores emocionales
        emotional_indicators = [
            "emocional", "conversacional", "empático", "humano", "interacción",
            "usuario", "experiencia", "comunicación", "social", "personal",
            "creatividad", "arte", "expresión", "sentimiento", "comprensión"
        ]
        
        # Analizar por nombre de archivo
        filename_lower = filename.lower()
        
        if "autosupervision" in filename_lower or "backend" in filename_lower:
            return 0.95, 0.05  # Supervisor extremo
        elif "emocional" in filename_lower or "conversacional" in filename_lower:
            return 0.3, 0.7   # Más emocional
        elif "visualization" in filename_lower or "advanced" in filename_lower:
            return 0.8, 0.2   # Técnico avanzado
        elif "cognitive" in filename_lower or "mirroring" in filename_lower:
            return 0.6, 0.4   # Balanceado
        elif "self_healing" in filename_lower or "autonomous" in filename_lower:
            return 0.9, 0.1   # Muy técnico
        elif "knowledge" in filename_lower or "retrieval" in filename_lower:
            return 0.7, 0.3   # Técnico moderado
        elif "proactive" in filename_lower or "interaction" in filename_lower:
            return 0.4, 0.6   # Más interactivo
        elif "entrenamiento" in filename_lower:
            return 0.5, 0.5   # Equilibrado para aprendizaje
        else:
            # Análisis del contenido
            content_str = json.dumps(data, ensure_ascii=False).lower()
            
            tech_score = sum(1 for indicator in technical_indicators if indicator in content_str)
            emot_score = sum(1 for indicator in emotional_indicators if indicator in content_str)
            
            if tech_score > emot_score * 2:
                return 0.8, 0.2
            elif emot_score > tech_score * 2:
                return 0.3, 0.7
            else:
                return 0.6, 0.4  # Por defecto balanceado
    
    def _determine_specialization(self, data: Dict[str, Any], filename: str) -> str:
        """Determina la especialización de la personalidad"""
        filename_lower = filename.lower()
        
        specializations = {
            "autosupervision": "system_supervision",
            "backend": "backend_management", 
            "emocional": "emotional_intelligence",
            "conversacional": "conversation_management",
            "visualization": "data_visualization",
            "cognitive": "cognitive_processing",
            "self_healing": "autonomous_systems",
            "knowledge": "knowledge_management",
            "proactive": "proactive_assistance",
            "entrenamiento": "learning_optimization",
            "external": "external_integration"
        }
        
        for key, spec in specializations.items():
            if key in filename_lower:
                return spec
        
        return "general_purpose"
    
    def _extract_characteristics(self, data: Dict[str, Any]) -> List[str]:
        """Extrae características principales de la personalidad"""
        characteristics = []
        
        # Principios de diseño
        if "principios_diseno" in data:
            characteristics.extend(data["principios_diseno"][:3])  # Primeros 3
        
        # Objetivos
        if "objetivo" in data:
            characteristics.append(f"Objetivo: {data['objetivo'][:100]}...")
        
        # Capacidades principales
        if "modulos" in data and isinstance(data["modulos"], list):
            for module in data["modulos"][:2]:  # Primeros 2 módulos
                if "nombre" in module:
                    characteristics.append(f"Módulo: {module['nombre']}")
        
        return characteristics[:5]  # Máximo 5 características
    
    def _extract_use_cases(self, data: Dict[str, Any]) -> List[str]:
        """Extrae casos de uso de la personalidad"""
        use_cases = []
        
        # Buscar casos de uso explícitos
        content_str = json.dumps(data, ensure_ascii=False).lower()
        
        if "monitoreo" in content_str or "supervision" in content_str:
            use_cases.append("Monitoreo y supervisión de sistemas")
        
        if "optimización" in content_str:
            use_cases.append("Optimización de rendimiento")
        
        if "conversacional" in content_str or "chat" in content_str:
            use_cases.append("Interacciones conversacionales")
        
        if "análisis" in content_str:
            use_cases.append("Análisis de datos y patrones")
        
        if "seguridad" in content_str or "security" in content_str:
            use_cases.append("Gestión de seguridad")
        
        return use_cases[:4]  # Máximo 4 casos de uso
    
    def _determine_model_preferences(self, data: Dict[str, Any], specialization: str) -> Dict[str, str]:
        """Determina qué modelos prefiere usar esta personalidad"""
        preferences = {}
        
        if specialization in ["system_supervision", "backend_management"]:
            preferences = {
                "primary": "deepseek_coder",
                "fallback": "fast_response",
                "embedding": "embeddings"
            }
        elif specialization in ["emotional_intelligence", "conversation_management"]:
            preferences = {
                "primary": "qwen_7b",
                "fallback": "fast_response", 
                "embedding": "embeddings"
            }
        elif specialization in ["data_visualization", "knowledge_management"]:
            preferences = {
                "primary": "qwen_7b",
                "secondary": "deepseek_coder",
                "fallback": "fast_response",
                "embedding": "embeddings"
            }
        else:
            preferences = {
                "primary": "qwen_7b",
                "fallback": "fast_response",
                "embedding": "embeddings"
            }
        
        return preferences
    
    def _extract_response_style(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae el estilo de respuesta de la personalidad"""
        style = {
            "verbosity": "medium",
            "technical_depth": "moderate",
            "examples": True,
            "emojis": True,
            "code_snippets": False
        }
        
        # Ajustar basado en el contenido
        content_str = json.dumps(data, ensure_ascii=False).lower()
        
        if "arquitectura" in content_str or "sistema" in content_str:
            style.update({
                "verbosity": "high",
                "technical_depth": "deep",
                "code_snippets": True,
                "examples": True
            })
        
        if "emocional" in content_str or "conversacional" in content_str:
            style.update({
                "verbosity": "medium",
                "technical_depth": "light",
                "emojis": True,
                "personal_touch": True
            })
        
        return style
    
    def get_personality(self, name: str) -> Optional[PersonalityConfig]:
        """Obtiene una personalidad específica"""
        return self.personalities.get(name.lower())
    
    def get_all_personalities(self) -> Dict[str, PersonalityConfig]:
        """Obtiene todas las personalidades cargadas"""
        return self.personalities.copy()
    
    def get_personality_names(self) -> List[str]:
        """Obtiene lista de nombres de personalidades disponibles"""
        return list(self.personalities.keys())
    
    def get_raw_personality_data(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtiene los datos JSON raw de una personalidad"""
        return self.raw_personalities.get(name.lower())
    
    def get_personalities_by_specialization(self, specialization: str) -> List[PersonalityConfig]:
        """Obtiene personalidades por especialización"""
        return [
            p for p in self.personalities.values() 
            if p.specialization == specialization
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de personalidades cargadas"""
        specializations = {}
        for personality in self.personalities.values():
            spec = personality.specialization
            if spec not in specializations:
                specializations[spec] = []
            specializations[spec].append(personality.display_name)
        
        return {
            "total_personalities": len(self.personalities),
            "specializations": specializations,
            "technical_range": {
                "min": min(p.technical_ratio for p in self.personalities.values()) if self.personalities else 0,
                "max": max(p.technical_ratio for p in self.personalities.values()) if self.personalities else 1
            },
            "loaded_from": str(self.personalities_dir)
        } 