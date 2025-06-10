#!/usr/bin/env python3
"""
VokaFlow - Servicio de Selección Inteligente de Voces
Usa información de pyannote-audio para seleccionar la voz óptima
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

logger = logging.getLogger("vokaflow.voice_selector")

class VoiceSelector:
    """Selecciona la voz óptima basada en análisis de audio"""
    
    def __init__(self):
        self.voices_dir = Path("/opt/vokaflow/voices/native_speakers")
        self.voice_cache = {}
        self.load_voice_catalog()
        
    def load_voice_catalog(self):
        """Carga catálogo de voces disponibles"""
        try:
            logger.info("📋 Cargando catálogo de voces...")
            
            voice_count = 0
            for lang_dir in self.voices_dir.iterdir():
                if not lang_dir.is_dir():
                    continue
                    
                lang_code = lang_dir.name
                if lang_code not in self.voice_cache:
                    self.voice_cache[lang_code] = {"male": [], "female": []}
                
                for gender_dir in lang_dir.iterdir():
                    if not gender_dir.is_dir() or gender_dir.name not in ["male", "female"]:
                        continue
                        
                    gender = gender_dir.name
                    
                    for voice_dir in gender_dir.iterdir():
                        if not voice_dir.is_dir():
                            continue
                            
                        metadata_file = voice_dir / "voice_metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, "r", encoding="utf-8") as f:
                                    metadata = json.load(f)
                                
                                self.voice_cache[lang_code][gender].append({
                                    "voice_id": metadata["voice_id"],
                                    "name": metadata["name"],
                                    "description": metadata["description"],
                                    "quality_score": metadata.get("quality_score", 1.0),
                                    "accent": metadata.get("accent", lang_code),
                                    "sample_files": metadata.get("sample_files", [])
                                })
                                
                                voice_count += 1
                                
                            except Exception as e:
                                logger.error(f"Error cargando metadata de {voice_dir}: {e}")
            
            logger.info(f"✅ Catálogo cargado: {voice_count} voces en {len(self.voice_cache)} idiomas")
            
        except Exception as e:
            logger.error(f"Error cargando catálogo de voces: {e}")
    
    def select_best_voice(
        self,
        language: str,
        gender: Optional[str] = None,
        accent: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Selecciona la mejor voz basada en criterios
        
        Args:
            language: Idioma detectado ('es', 'en', 'gb', etc.)
            gender: Género detectado ('male', 'female')
            accent: Acento preferido ('american', 'british', etc.)
            user_preferences: Preferencias del usuario
            
        Returns:
            voice_id de la voz seleccionada o None
        """
        try:
            logger.info(f"🎯 Seleccionando voz: {language}/{gender}/{accent}")
            
            # Prioridad 1: Idioma exacto + género + acento
            if language in self.voice_cache and gender:
                voices = self.voice_cache[language].get(gender, [])
                
                if accent:
                    # Buscar por acento específico
                    for voice in voices:
                        if voice["accent"] == accent:
                            logger.info(f"✅ Voz exacta encontrada: {voice['voice_id']}")
                            return voice["voice_id"]
                
                # Prioridad 2: Idioma exacto + género (sin acento específico)
                if voices:
                    best_voice = max(voices, key=lambda v: v["quality_score"])
                    logger.info(f"✅ Voz por idioma/género: {best_voice['voice_id']}")
                    return best_voice["voice_id"]
            
            # Prioridad 3: Idioma exacto (cualquier género)
            if language in self.voice_cache:
                all_voices = []
                for gender_voices in self.voice_cache[language].values():
                    all_voices.extend(gender_voices)
                
                if all_voices:
                    # Preferir género solicitado si existe
                    if gender:
                        gender_voices = [v for v in all_voices if gender in v["voice_id"]]
                        if gender_voices:
                            best_voice = max(gender_voices, key=lambda v: v["quality_score"])
                            logger.info(f"✅ Voz por idioma (género preferido): {best_voice['voice_id']}")
                            return best_voice["voice_id"]
                    
                    # Cualquier voz del idioma
                    best_voice = max(all_voices, key=lambda v: v["quality_score"])
                    logger.info(f"✅ Voz por idioma: {best_voice['voice_id']}")
                    return best_voice["voice_id"]
            
            # Prioridad 4: Idiomas similares
            similar_languages = self._get_similar_languages(language)
            for similar_lang in similar_languages:
                if similar_lang in self.voice_cache:
                    all_voices = []
                    for gender_voices in self.voice_cache[similar_lang].values():
                        all_voices.extend(gender_voices)
                    
                    if all_voices:
                        best_voice = max(all_voices, key=lambda v: v["quality_score"])
                        logger.info(f"✅ Voz similar ({similar_lang}): {best_voice['voice_id']}")
                        return best_voice["voice_id"]
            
            # Prioridad 5: Voz por defecto (español)
            default_voice = self._get_default_voice(gender)
            if default_voice:
                logger.info(f"✅ Voz por defecto: {default_voice}")
                return default_voice
            
            logger.warning(f"❌ No se encontró voz para {language}/{gender}")
            return None
            
        except Exception as e:
            logger.error(f"Error seleccionando voz: {e}")
            return self._get_default_voice()
    
    def _get_similar_languages(self, language: str) -> List[str]:
        """Obtiene idiomas similares para fallback"""
        similar_map = {
            "en": ["gb"],
            "gb": ["en"],
            "es": ["pt", "ca", "gl"],
            "pt": ["es", "gl"],
            "fr": ["es", "it"],
            "it": ["es", "fr"],
            "de": ["nl"],
            "nl": ["de"],
            "hi": ["ur", "bn"],
            "ar": ["fa", "ur"],
            "zh": ["ja", "ko"],
            "ja": ["zh", "ko"],
            "ko": ["zh", "ja"]
        }
        
        return similar_map.get(language, [])
    
    def _get_default_voice(self, preferred_gender: Optional[str] = None) -> Optional[str]:
        """Obtiene voz por defecto (español)"""
        try:
            # Español como idioma por defecto
            if "es" in self.voice_cache:
                if preferred_gender and preferred_gender in self.voice_cache["es"]:
                    voices = self.voice_cache["es"][preferred_gender]
                    if voices:
                        return voices[0]["voice_id"]
                
                # Cualquier voz española
                for gender_voices in self.voice_cache["es"].values():
                    if gender_voices:
                        return gender_voices[0]["voice_id"]
            
            # Si no hay español, usar cualquier voz
            for lang_voices in self.voice_cache.values():
                for gender_voices in lang_voices.values():
                    if gender_voices:
                        return gender_voices[0]["voice_id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo voz por defecto: {e}")
            return None
    
    def get_voice_info(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una voz específica"""
        try:
            for lang_voices in self.voice_cache.values():
                for gender_voices in lang_voices.values():
                    for voice in gender_voices:
                        if voice["voice_id"] == voice_id:
                            return voice
            return None
        except Exception as e:
            logger.error(f"Error obteniendo info de voz {voice_id}: {e}")
            return None
    
    def list_available_voices(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Lista todas las voces disponibles"""
        try:
            if language:
                return {language: self.voice_cache.get(language, {"male": [], "female": []})}
            else:
                return self.voice_cache
        except Exception as e:
            logger.error(f"Error listando voces: {e}")
            return {}

# Instancia global del selector de voces
voice_selector = VoiceSelector()
