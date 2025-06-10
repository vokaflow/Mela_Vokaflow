#!/usr/bin/env python3
"""
VokaFlow - Servicio de Text-to-Speech Real
Integración completa con XTTS-V2 para síntesis de voz de alta calidad
"""

import logging
import time
import asyncio
import torch
import numpy as np
import io
import tempfile
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
import librosa
import soundfile as sf

from .model_manager import model_manager, ModelInfo

logger = logging.getLogger("vokaflow.tts")

@dataclass
class TTSResult:
    """Resultado de una síntesis TTS"""
    audio_data: bytes
    duration: float
    sample_rate: int
    format: str
    file_size: int
    voice_used: str
    language: str
    processing_time: float
    model_used: str
    metadata: Dict[str, Any] = None

@dataclass
class VoiceProfile:
    """Perfil de una voz"""
    voice_id: str
    name: str
    language: str
    gender: str
    description: str
    sample_files: List[str]
    is_cloned: bool = False
    quality_score: float = 1.0

class TTSService:
    """Servicio de Text-to-Speech usando XTTS-V2"""
    
    def __init__(self):
        self.model_name = "xtts-v2"
        self.voices_dir = Path("/opt/vokaflow/voices")
        self.cloned_voices_dir = self.voices_dir / "cloned_voices"
        self.native_voices_dir = self.voices_dir / "native_speakers"
        
        # Configuración de audio
        self.supported_formats = ["wav", "mp3", "ogg", "flac"]
        self.default_sample_rate = 22050
        self.max_text_length = 5000
        self.min_clone_duration = 3.0  # Mínimo 3 segundos para clonar
        self.max_clone_samples = 10
        
        # Mapeo de idiomas XTTS (definir antes de _ensure_directories)
        self.xtts_languages = {
            "es": "spanish",
            "en": "english", 
            "fr": "french",
            "de": "german",
            "it": "italian",
            "pt": "portuguese",
            "ru": "russian",
            "zh": "chinese",
            "ja": "japanese",
            "ko": "korean",
            "ar": "arabic",
            "hi": "hindi",
            "tr": "turkish",
            "nl": "dutch",
            "sv": "swedish",
            "no": "norwegian",
            "da": "danish",
            "fi": "finnish",
            "pl": "polish",
            "cs": "czech",
            "hu": "hungarian",
            "ro": "romanian",
            "bg": "bulgarian",
            "hr": "croatian",
            "sk": "slovak",
            "sl": "slovenian",
            "et": "estonian",
            "lv": "latvian",
            "lt": "lithuanian",
            "mt": "maltese",
            "ga": "irish",
            "cy": "welsh",
            "eu": "basque",
            "ca": "catalan",
            "gl": "galician",
            "is": "icelandic",
            "mk": "macedonian",
            "sr": "serbian",
            "uk": "ukrainian",
            "be": "belarusian",
            "th": "thai",
            "vi": "vietnamese",
            "id": "indonesian",
            "ms": "malay",
            "tl": "tagalog",
            "sw": "swahili",
            "he": "hebrew",
            "fa": "persian",
            "ur": "urdu",
            "bn": "bengali",
            "gu": "gujarati",
            "kn": "kannada",
            "ml": "malayalam",
            "mr": "marathi",
            "ne": "nepali",
            "pa": "punjabi",
            "si": "sinhala",
            "ta": "tamil",
            "te": "telugu",
            "my": "burmese",
            "km": "khmer",
            "lo": "lao",
            "ka": "georgian",
            "hy": "armenian",
            "az": "azerbaijani",
            "kk": "kazakh",
            "ky": "kyrgyz",
            "tg": "tajik",
            "tk": "turkmen",
            "uz": "uzbek",
            "mn": "mongolian",
            "am": "amharic",
            "yo": "yoruba",
            "af": "afrikaans",
            "sq": "albanian"
        }
        
        # Crear directorios necesarios (después de definir xtts_languages)
        self._ensure_directories()
        
        logger.info("Servicio de TTS XTTS inicializado")
        
    def __post_init__(self):
        """Asegurar que todos los atributos estén inicializados"""
        if not hasattr(self, 'xtts_languages'):
            self.xtts_languages = {
                "es": "spanish",
                "en": "english", 
                "fr": "french",
                "de": "german",
                "it": "italian",
                "pt": "portuguese",
                "ru": "russian",
                "zh": "chinese",
                "ja": "japanese",
                "ko": "korean"
            }
    
    def _ensure_directories(self):
        """Crea los directorios necesarios para voces"""
        for dir_path in [self.voices_dir, self.cloned_voices_dir, self.native_voices_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Crear estructura por idiomas en native_speakers
        for lang_code in self.xtts_languages.keys():
            for gender in ["male", "female"]:
                gender_dir = self.native_voices_dir / lang_code / gender
                gender_dir.mkdir(parents=True, exist_ok=True)
    
    def get_xtts_language_code(self, lang_code: str) -> str:
        """Convierte código de idioma a formato XTTS"""
        # XTTS usa códigos de idioma cortos, no nombres largos
        return lang_code if lang_code in ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi"] else "es"
    
    def scan_native_voices(self) -> Dict[str, List[VoiceProfile]]:
        """Escanea voces nativas disponibles"""
        voices_by_language = {}
        
        for lang_dir in self.native_voices_dir.iterdir():
            if not lang_dir.is_dir():
                continue
                
            lang_code = lang_dir.name
            voices_by_language[lang_code] = []
            
            for gender_dir in lang_dir.iterdir():
                if not gender_dir.is_dir() or gender_dir.name not in ["male", "female"]:
                    continue
                    
                gender = gender_dir.name
                
                # Buscar subdirectorios de speakers (ej: speaker_es_f01)
                for speaker_dir in gender_dir.iterdir():
                    if not speaker_dir.is_dir():
                        continue
                    
                    speaker_id = speaker_dir.name
                    
                    # Buscar metadata file
                    metadata_file = speaker_dir / "voice_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r", encoding="utf-8") as f:
                                metadata = json.load(f)
                            
                            # Buscar archivos de audio en el directorio del speaker
                            audio_files = []
                            for ext in ['.wav', '.mp3', '.ogg', '.flac']:
                                audio_files.extend(speaker_dir.glob(f"*{ext}"))
                            
                            if audio_files:
                                voice_profile = VoiceProfile(
                                    voice_id=metadata.get("voice_id", speaker_id),
                                    name=metadata.get("name", speaker_id.replace('_', ' ').title()),
                                    language=metadata.get("language", lang_code),
                                    gender=metadata.get("gender", gender),
                                    description=metadata.get("description", f"Native {gender} voice for {lang_code}"),
                                    sample_files=[str(f) for f in audio_files],
                                    is_cloned=False,
                                    quality_score=metadata.get("quality_score", 1.0)
                                )
                                voices_by_language[lang_code].append(voice_profile)
                                logger.info(f"✅ Voz cargada: {voice_profile.voice_id} ({voice_profile.name})")
                        
                        except Exception as e:
                            logger.error(f"Error cargando metadata de {metadata_file}: {e}")
                    else:
                        # Fallback: crear perfil básico sin metadata
                        audio_files = []
                        for ext in ['.wav', '.mp3', '.ogg', '.flac']:
                            audio_files.extend(speaker_dir.glob(f"*{ext}"))
                        
                        if audio_files:
                            voice_profile = VoiceProfile(
                                voice_id=speaker_id,
                                name=speaker_id.replace('_', ' ').title(),
                                language=lang_code,
                                gender=gender,
                                description=f"Native {gender} voice for {lang_code}",
                                sample_files=[str(f) for f in audio_files],
                                is_cloned=False,
                                quality_score=1.0
                            )
                            voices_by_language[lang_code].append(voice_profile)
                            logger.warning(f"⚠️ Voz sin metadata: {voice_profile.voice_id}")
        
        return voices_by_language
    
    def scan_cloned_voices(self) -> List[VoiceProfile]:
        """Escanea voces clonadas disponibles"""
        cloned_voices = []
        
        for voice_dir in self.cloned_voices_dir.iterdir():
            if not voice_dir.is_dir():
                continue
            
            # Buscar archivo de configuración
            config_file = voice_dir / "voice_config.json"
            if not config_file.exists():
                continue
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Buscar archivos de muestra
                sample_files = []
                for ext in ['.wav', '.mp3', '.ogg', '.flac']:
                    sample_files.extend(voice_dir.glob(f"*{ext}"))
                
                voice_profile = VoiceProfile(
                    voice_id=config.get('voice_id', voice_dir.name),
                    name=config.get('name', voice_dir.name),
                    language=config.get('language', 'es'),
                    gender=config.get('gender', 'unknown'),
                    description=config.get('description', 'Cloned voice'),
                    sample_files=[str(f) for f in sample_files],
                    is_cloned=True,
                    quality_score=config.get('quality_score', 0.8)
                )
                cloned_voices.append(voice_profile)
                
            except Exception as e:
                logger.warning(f"Error loading cloned voice config {config_file}: {e}")
        
        return cloned_voices
    
    async def synthesize_speech(
        self,
        text: str,
        voice_id: str,
        language: str,
        speed: float = 1.0,
        temperature: float = 0.7,
        output_format: str = "wav"
    ) -> TTSResult:
        """Sintetiza voz usando XTTS-V2"""
        start_time = time.time()
        
        try:
            logger.info(f"🎙️ Iniciando síntesis XTTS: {text[:50]}... (voz: {voice_id})")
            
            # Validar parámetros
            if len(text) > self.max_text_length:
                raise ValueError(f"Texto muy largo. Máximo: {self.max_text_length} caracteres")
            
            # Obtener perfil de voz
            voice_profile = await self._get_voice_profile(voice_id, language)
            if not voice_profile:
                # Usar voz de fallback
                logger.warning(f"Voz {voice_id} no encontrada, usando fallback")
                return await self._fallback_synthesis(text, language, start_time)
            
            # Obtener modelo XTTS
            model_info = await asyncio.get_event_loop().run_in_executor(
                None, model_manager.get_model, self.model_name
            )
            
            if not model_info or not model_info.model:
                # Fallback a síntesis simulada
                logger.warning("Modelo XTTS no disponible, usando síntesis simulada")
                return await self._fallback_synthesis(text, language, start_time)
            
            # Realizar síntesis en hilo separado
            audio_data, sample_rate = await asyncio.get_event_loop().run_in_executor(
                None, self._synthesize_with_xtts,
                model_info, text, voice_profile, language, speed, temperature
            )
            
            # Convertir formato si es necesario
            if output_format != "wav":
                audio_data = await self._convert_audio_format(audio_data, sample_rate, output_format)
            
            processing_time = time.time() - start_time
            duration = len(audio_data) / (sample_rate * 2)  # 16-bit samples
            
            return TTSResult(
                audio_data=audio_data,
                duration=duration,
                sample_rate=sample_rate,
                format=output_format,
                file_size=len(audio_data),
                voice_used=voice_id,
                language=language,
                processing_time=processing_time,
                model_used="xtts-v2",
                metadata={
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "speed": speed,
                    "temperature": temperature,
                    "voice_profile": voice_profile.name,
                    "is_cloned": voice_profile.is_cloned
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error en síntesis XTTS: {e}")
            # Fallback en caso de error
            return await self._fallback_synthesis(text, language, start_time, error=str(e))
    
    async def _get_voice_profile(self, voice_id: str, language: str) -> Optional[VoiceProfile]:
        """Obtiene el perfil de una voz"""
        # Buscar en voces nativas
        native_voices = self.scan_native_voices()
        if language in native_voices:
            for voice in native_voices[language]:
                if voice.voice_id == voice_id:
                    return voice
        
        # Buscar en voces clonadas
        cloned_voices = self.scan_cloned_voices()
        for voice in cloned_voices:
            if voice.voice_id == voice_id and voice.language == language:
                return voice
        
        return None
    
    def _synthesize_with_xtts(
        self,
        model_info: ModelInfo,
        text: str,
        voice_profile: VoiceProfile,
        language: str,
        speed: float,
        temperature: float
    ) -> Tuple[bytes, int]:
        """Realiza la síntesis usando XTTS cargado"""
        try:
            model = model_info.model
            
            logger.info(f"🔄 Sintetizando con XTTS-V2")
            
            # Cargar samples de referencia de la voz
            reference_audio = self._load_reference_audio(voice_profile.sample_files)
            
            # Obtener idioma en formato XTTS
            xtts_language = self.get_xtts_language_code(language)
            
            # Crear archivo temporal para salida
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_output_path = temp_file.name
            
            try:
                # Usar la API correcta de TTS
                model.tts_to_file(
                    text=text,
                    speaker_wav=reference_audio,
                    language=xtts_language,
                    file_path=temp_output_path,
                    speed=speed
                )
                
                # Leer el archivo generado
                with open(temp_output_path, "rb") as f:
                    audio_data = f.read()
                
                logger.info(f"✅ XTTS síntesis completada: {len(audio_data)} bytes")
                
                return audio_data, self.default_sample_rate
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_output_path):
                    os.unlink(temp_output_path)
            
        except Exception as e:
            logger.error(f"❌ Error en _synthesize_with_xtts: {e}")
            raise
    
    def _load_reference_audio(self, sample_files: List[str]) -> str:
        """Carga audio de referencia para la voz"""
        if not sample_files:
            raise ValueError("No hay archivos de muestra para la voz")
        
        # Usar el primer archivo como referencia
        # En una implementación más avanzada, podríamos concatenar múltiples muestras
        return sample_files[0]
    
    async def _convert_audio_format(self, audio_data: bytes, sample_rate: int, target_format: str) -> bytes:
        """Convierte audio a formato específico"""
        # Implementación básica - en producción usar ffmpeg o librosa
        if target_format == "wav":
            return audio_data
        
        # Para otros formatos, por ahora devolver WAV
        logger.warning(f"Conversión a {target_format} no implementada, devolviendo WAV")
        return audio_data
    
    async def _fallback_synthesis(
        self,
        text: str,
        language: str,
        start_time: float,
        error: Optional[str] = None
    ) -> TTSResult:
        """Síntesis de respaldo cuando XTTS no está disponible"""
        
        # Simular tiempo de procesamiento
        await asyncio.sleep(1.0)
        
        # Crear audio silencioso de duración proporcional al texto
        duration = len(text.split()) * 0.5  # 0.5 segundos por palabra
        sample_rate = self.default_sample_rate
        num_samples = int(duration * sample_rate)
        
        # Generar silencio (en una implementación real, usar TTS básico)
        silence = np.zeros(num_samples, dtype=np.int16)
        
        # Convertir a bytes
        audio_data = silence.tobytes()
        
        processing_time = time.time() - start_time
        
        logger.warning(f"Usando síntesis de respaldo para: {text[:50]}...")
        
        return TTSResult(
            audio_data=audio_data,
            duration=duration,
            sample_rate=sample_rate,
            format="wav",
            file_size=len(audio_data),
            voice_used="fallback",
            language=language,
            processing_time=processing_time,
            model_used="fallback",
            metadata={
                "is_fallback": True,
                "fallback_reason": error or "Model not available",
                "text_length": len(text),
                "word_count": len(text.split())
            }
        )
    
    async def clone_voice(
        self,
        voice_name: str,
        audio_samples: List[bytes],
        language: str,
        gender: str,
        description: str = ""
    ) -> str:
        """Clona una voz a partir de muestras de audio"""
        try:
            logger.info(f"🎭 Clonando voz: {voice_name}")
            
            # Validar muestras
            if len(audio_samples) < 3:
                raise ValueError("Se requieren al menos 3 muestras de audio para clonar una voz")
            
            # Crear ID único para la voz
            voice_id = f"cloned_{hashlib.md5(f'{voice_name}{language}{datetime.now()}'.encode()).hexdigest()[:8]}"
            voice_dir = self.cloned_voices_dir / voice_id
            voice_dir.mkdir(exist_ok=True)
            
            # Guardar muestras de audio
            sample_files = []
            for i, audio_data in enumerate(audio_samples):
                sample_file = voice_dir / f"sample_{i+1}.wav"
                with open(sample_file, "wb") as f:
                    f.write(audio_data)
                sample_files.append(str(sample_file))
            
            # Crear configuración de voz
            config = {
                "voice_id": voice_id,
                "name": voice_name,
                "language": language,
                "gender": gender,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "sample_files": sample_files,
                "quality_score": 0.8  # Placeholder - calcular en implementación real
            }
            
            config_file = voice_dir / "voice_config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Voz clonada exitosamente: {voice_id}")
            return voice_id
            
        except Exception as e:
            logger.error(f"❌ Error clonando voz: {e}")
            raise
    
    def get_available_voices(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene todas las voces disponibles"""
        native_voices = self.scan_native_voices()
        cloned_voices = self.scan_cloned_voices()
        
        result = {
            "native_voices": {},
            "cloned_voices": [],
            "total_count": 0
        }
        
        # Filtrar por idioma si se especifica
        if language:
            if language in native_voices:
                result["native_voices"][language] = [
                    {
                        "voice_id": v.voice_id,
                        "name": v.name,
                        "gender": v.gender,
                        "description": v.description,
                        "sample_count": len(v.sample_files)
                    }
                    for v in native_voices[language]
                ]
            
            result["cloned_voices"] = [
                {
                    "voice_id": v.voice_id,
                    "name": v.name,
                    "gender": v.gender,
                    "description": v.description,
                    "quality_score": v.quality_score
                }
                for v in cloned_voices if v.language == language
            ]
        else:
            # Todas las voces
            for lang, voices in native_voices.items():
                result["native_voices"][lang] = [
                    {
                        "voice_id": v.voice_id,
                        "name": v.name,
                        "gender": v.gender,
                        "description": v.description,
                        "sample_count": len(v.sample_files)
                    }
                    for v in voices
                ]
            
            result["cloned_voices"] = [
                {
                    "voice_id": v.voice_id,
                    "name": v.name,
                    "language": v.language,
                    "gender": v.gender,
                    "description": v.description,
                    "quality_score": v.quality_score
                }
                for v in cloned_voices
            ]
        
        # Calcular total
        native_count = sum(len(voices) for voices in result["native_voices"].values())
        cloned_count = len(result["cloned_voices"])
        result["total_count"] = native_count + cloned_count
        
        return result
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Obtiene idiomas soportados para TTS"""
        return {
            "supported_languages": list(self.xtts_languages.keys()),
            "total_count": len(self.xtts_languages),
            "model": "xtts-v2",
            "supported_formats": self.supported_formats,
            "max_text_length": self.max_text_length,
            "default_sample_rate": self.default_sample_rate
        }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Obtiene estado del servicio TTS"""
        model_loaded = self.model_name in model_manager.loaded_models
        
        # Contar voces disponibles
        voices_info = self.get_available_voices()
        
        return {
            "status": "operational" if model_loaded else "ready",
            "model": self.model_name,
            "model_loaded": model_loaded,
            "supported_languages": len(self.xtts_languages),
            "supported_formats": len(self.supported_formats),
            "gpu_available": torch.cuda.is_available(),
            "memory_usage": model_manager.get_memory_usage(),
            "voices": {
                "total_voices": voices_info["total_count"],
                "native_voices": sum(len(v) for v in voices_info["native_voices"].values()),
                "cloned_voices": len(voices_info["cloned_voices"]),
                "languages_with_voices": len(voices_info["native_voices"])
            },
            "directories": {
                "voices_dir": str(self.voices_dir),
                "native_voices_dir": str(self.native_voices_dir),
                "cloned_voices_dir": str(self.cloned_voices_dir)
            }
        }

# Instancia global del servicio TTS
tts_service = TTSService()
