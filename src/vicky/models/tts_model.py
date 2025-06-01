"""
Módulo avanzado para síntesis de voz con soporte para voces organizadas.
Implementa tecnología de clonación de voz utilizando Coquis TTS.
"""
import os
import time
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
import yaml
import json
import glob
import random
from pathlib import Path
import soundfile as sf

logger = logging.getLogger("vicky.models.tts_model")

class VoiceNotFoundError(Exception):
    """Excepción para cuando no se encuentra una voz adecuada."""
    pass

class TTSModel:
    """
    Clase avanzada para interactuar con modelos de síntesis de voz como XTTS.
    Soporta selección de voces por idioma y género.
    """
    
    # Mapeo de códigos de idioma a nombres completos
    LANGUAGE_CODES = {
        "ar": "arabic",
        "de": "german",
        "en": "english",
        "es": "spanish",
        "fr": "french",
        "hi": "indian",
        "it": "italian",
        "pt": "portuguese",
        "zh": "chinese"
    }
    
    # Mapeo inverso de nombres de idioma a códigos
    LANGUAGE_NAMES = {v: k for k, v in LANGUAGE_CODES.items()}
    
    # Géneros disponibles
    GENDERS = ["male", "female"]
    
    def __init__(self, model_path: str = None, device: str = None, voice_dir: str = None,
                custom_voice_dir: str = None):
        """
        Inicializa el modelo de síntesis de voz con soporte para voces organizadas.
        
        Args:
            model_path: Ruta al modelo XTTS
            device: Dispositivo para inferencia (cuda, cpu)
            voice_dir: Directorio con voces organizadas
            custom_voice_dir: Directorio con voces personalizadas
        """
        # Cargar configuración
        config_path = os.environ.get("MODELS_CONFIG", "/opt/vokaflow/config/models.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Configurar modelo
        self.model_path = model_path or self.config["text_to_speech"]["models"]["xtts-v2"]["path"]
        self.device = device or self.config["text_to_speech"]["models"]["xtts-v2"]["device"]
        
        # Directorio de voces organizadas
        self.voice_dir = voice_dir or "/mnt/nvme_fast/vokaflow_models/tts/coquis_voices"
        
        # Directorio de voces personalizadas
        self.custom_voice_dir = custom_voice_dir or "/mnt/nvme_fast/vokaflow_models/tts/custom_voices"
        
        # Caché de voces y metadatos
        self.voice_cache = {}
        self.voice_metadata = {}
        self.voice_index = {}
        self.custom_voice_metadata = {}
        
        # Estado del modelo
        self.model = None
        self.synthesizer = None
        self.last_use_time = 0
        
        # Configuración de audio
        self.sample_rate = 24000
        self.preset = "high_quality"  # puede ser: fast, standard, high_quality
        
        # Preferencias de usuario
        self.user_preferences = {
            "language": "es",
            "gender": "female",
            "voice_id": None,
            "speed": 1.0,
            "pitch": 0.0,
            "energy": 1.0,
            "emotion": "neutral"
        }
        
        # Cargar índice de voces
        self._build_voice_index()
        
        # Cargar metadatos de voces personalizadas
        self._load_custom_voice_metadata()
        
        logger.info(f"Inicializando modelo avanzado de síntesis de voz desde {self.model_path}")
        logger.info(f"Voces disponibles en {self.voice_dir}")
        logger.info(f"Voces personalizadas en {self.custom_voice_dir}")
        logger.info(f"Total de voces indexadas: {sum(len(voices) for voices in self.voice_index.values())}")
        
    def _build_voice_index(self) -> None:
        """
        Construye un índice de todas las voces disponibles organizadas por idioma y género.
        """
        if not os.path.exists(self.voice_dir):
            logger.warning(f"Directorio de voces no encontrado: {self.voice_dir}")
            return
        
        self.voice_index = {}
        
        # Iterar por cada idioma
        for lang_dir in os.listdir(self.voice_dir):
            lang_path = os.path.join(self.voice_dir, lang_dir)
            if not os.path.isdir(lang_path):
                continue
            
            language = lang_dir.lower()
            self.voice_index[language] = {"male": [], "female": []}
            
            # Iterar por cada género dentro del idioma
            for gender_dir in os.listdir(lang_path):
                gender_path = os.path.join(lang_path, gender_dir)
                if not os.path.isdir(gender_path):
                    continue
                
                gender = gender_dir.lower()
                if gender not in self.GENDERS:
                    continue
                
                # Buscar archivos de audio para este idioma y género
                audio_files = []
                for ext in ["wav", "mp3", "flac", "ogg"]:
                    audio_files.extend(glob.glob(os.path.join(gender_path, f"*.{ext}")))
                
                # Analizar metadatos de cada archivo
                for audio_file in audio_files:
                    voice_id = os.path.basename(audio_file)
                    try:
                        # Obtener información básica del archivo de audio
                        metadata = self._analyze_voice_file(audio_file)
                        self.voice_metadata[voice_id] = metadata
                        self.voice_index[language][gender].append(voice_id)
                    except Exception as e:
                        logger.warning(f"Error al analizar archivo de voz {voice_id}: {e}")
        
        # Guardar caché de metadatos para futuras inicializaciones rápidas
        cache_path = os.path.join(self.voice_dir, "metadata_cache.json")
        try:
            with open(cache_path, "w") as f:
                json.dump({
                    "metadata": self.voice_metadata,
                    "index": self.voice_index
                }, f)
            logger.info(f"Caché de metadatos de voces guardada en {cache_path}")
        except Exception as e:
            logger.warning(f"No se pudo guardar caché de metadatos: {e}")
    
    def _load_custom_voice_metadata(self) -> None:
        """
        Carga los metadatos de voces personalizadas.
        """
        metadata_path = os.path.join(self.custom_voice_dir, "voice_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    self.custom_voice_metadata = json.load(f)
                logger.info(f"Metadatos de voces personalizadas cargados: {len(self.custom_voice_metadata)} voces")
            except Exception as e:
                logger.error(f"Error al cargar metadatos de voces personalizadas: {e}")
                self.custom_voice_metadata = {}
    
    def _analyze_voice_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analiza un archivo de voz para extraer metadatos.
        
        Args:
            file_path: Ruta al archivo de audio
            
        Returns:
            Diccionario con metadatos del archivo
        """
        try:
            # Obtener información básica
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            # Cargar audio para análisis
            info = sf.info(file_path)
            duration = info.duration
            
            # Clasificación de calidad basada en duración y tamaño
            quality = "medium"
            if duration > 30 and file_size > 5:
                quality = "high"
            elif duration < 10 or file_size < 1:
                quality = "low"
            
            # Obtener idioma y género de la estructura de directorios
            parts = Path(file_path).parts
            lang_idx = parts.index("coquis_voices") + 1 if "coquis_voices" in parts else -2
            gender_idx = lang_idx + 1
            
            language = parts[lang_idx] if lang_idx >= 0 and lang_idx < len(parts) else "unknown"
            gender = parts[gender_idx] if gender_idx >= 0 and gender_idx < len(parts) else "unknown"
            
            return {
                "path": file_path,
                "duration": duration,
                "file_size": file_size,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "quality": quality,
                "language": language,
                "gender": gender,
                "analyzed_at": time.time()
            }
        except Exception as e:
            logger.error(f"Error al analizar archivo de audio {file_path}: {e}")
            return {
                "path": file_path,
                "error": str(e),
                "quality": "unknown"
            }
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """
        Obtiene la lista de idiomas disponibles.
        
        Returns:
            Lista de diccionarios con información de idiomas disponibles
        """
        languages = []
        for code, name in self.LANGUAGE_CODES.items():
            if name in self.voice_index:
                voice_count = len(self.voice_index[name]["male"]) + len(self.voice_index[name]["female"])
                if voice_count > 0:
                    languages.append({
                        "code": code,
                        "name": name,
                        "voice_count": voice_count
                    })
        
        return sorted(languages, key=lambda x: x["name"])
    
    def get_voices_for_language(self, language: str) -> Dict[str, List[str]]:
        """
        Obtiene las voces disponibles para un idioma específico.
        
        Args:
            language: Código o nombre del idioma
            
        Returns:
            Diccionario con voces por género
        """
        # Normalizar idioma
        if language in self.LANGUAGE_CODES:
            language = self.LANGUAGE_CODES[language]
            
        if language not in self.voice_index:
            return {"male": [], "female": []}
            
        return self.voice_index[language]
    
    def find_voice(self, language: str, gender: str = None, quality: str = None) -> str:
        """
        Encuentra una voz adecuada según los criterios especificados.
        
        Args:
            language: Código o nombre del idioma
            gender: Género de la voz (male/female)
            quality: Calidad deseada (high/medium/low)
            
        Returns:
            Ruta al archivo de voz seleccionado
            
        Raises:
            VoiceNotFoundError: Si no se encuentra una voz adecuada
        """
        # Normalizar idioma
        if language in self.LANGUAGE_CODES:
            language = self.LANGUAGE_CODES[language]
        elif language in self.LANGUAGE_NAMES.values():
            pass  # Ya es el nombre completo
        else:
            # Intenta encontrar el más cercano
            for name in self.voice_index.keys():
                if language.lower() in name.lower() or name.lower() in language.lower():
                    language = name
                    break
        
        # Si no se encuentra el idioma, usar español (o el primero disponible)
        if language not in self.voice_index:
            language = "spanish" if "spanish" in self.voice_index else list(self.voice_index.keys())[0]
            logger.warning(f"Idioma {language} no encontrado, usando {language}")
        
        # Si no se especifica género, usar uno aleatorio
        if not gender or gender not in self.GENDERS:
            available_genders = [g for g in self.GENDERS if self.voice_index[language][g]]
            if not available_genders:
                raise VoiceNotFoundError(f"No hay voces disponibles para el idioma {language}")
            gender = random.choice(available_genders)
        
        # Obtener voces disponibles
        voices = self.voice_index[language][gender]
        if not voices:
            # Si no hay voces para el género especificado, intentar con el otro
            other_gender = "male" if gender == "female" else "female"
            voices = self.voice_index[language][other_gender]
            if voices:
                logger.warning(f"No hay voces {gender} para {language}, usando {other_gender}")
                gender = other_gender
            else:
                # Si tampoco hay voces del otro género, buscar en otro idioma
                raise VoiceNotFoundError(f"No hay voces disponibles para {language}/{gender}")
        
        # Filtrar por calidad si se especifica
        if quality:
            quality_voices = [v for v in voices if self.voice_metadata.get(v, {}).get("quality") == quality]
            if quality_voices:
                voices = quality_voices
        
        # Seleccionar una voz aleatoria de las disponibles
        voice_id = random.choice(voices)
        voice_path = self.voice_metadata[voice_id]["path"]
        
        logger.info(f"Voz seleccionada: {voice_id} ({language}/{gender})")
        return voice_path
    
    def get_custom_voice(self, voice_id: str) -> Optional[str]:
        """
        Obtiene la ruta a una voz personalizada.
        
        Args:
            voice_id: ID de la voz personalizada
            
        Returns:
            Ruta al archivo de voz, o None si no existe
        """
        if voice_id not in self.custom_voice_metadata:
            return None
        
        voice_path = self.custom_voice_metadata[voice_id].get("sample_path")
        
        if voice_path and os.path.exists(voice_path):
            logger.info(f"Voz personalizada seleccionada: {voice_id}")
            return voice_path
        
        logger.warning(f"Voz personalizada no encontrada: {voice_id}")
        return None
    
    def load(self):
        """
        Carga el modelo en memoria.
        """
        try:
            logger.info(f"Cargando modelo de síntesis de voz desde {self.model_path}")
            
            # Importar las bibliotecas necesarias
            import TTS
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.tts.models.xtts import Xtts
            
            # Cargar configuración y modelo
            config_path = os.path.join(self.model_path, "config.json")
            config = XttsConfig()
            config.load_json(config_path)
            
            self.model = Xtts.init_from_config(config)
            self.model.load_checkpoint(config, checkpoint_dir=self.model_path)
            
            if self.device == "cuda" and torch.cuda.is_available():
                self.model.cuda()
            
            logger.info("Modelo de síntesis de voz cargado correctamente")
            
            # Mostrar información de memoria si se usa GPU
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"Memoria GPU reservada: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
                logger.info(f"Memoria GPU en uso: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            self.last_use_time = time.time()
            return True
        except Exception as e:
            logger.error(f"Error al cargar el modelo de síntesis de voz: {e}")
            return False
    
    def synthesize(self, text: str, language: str = None, gender: str = None, 
                  speaker_wav: str = None, custom_voice_id: str = None, emotion: str = None,
                  speed: float = None, pitch_shift: float = None) -> np.ndarray:
        """
        Sintetiza voz a partir de texto con opciones avanzadas.
        
        Args:
            text: Texto a sintetizar
            language: Código de idioma
            gender: Género de la voz (male/female)
            speaker_wav: Ruta específica a un archivo de audio para clonar
            custom_voice_id: ID de una voz personalizada
            emotion: Emoción a transmitir (neutral, happy, sad, angry)
            speed: Factor de velocidad (0.5-1.5)
            pitch_shift: Cambio de tono (-0.5 a 0.5)
            
        Returns:
            Array de audio sintetizado
        """
        if self.model is None:
            logger.warning("El modelo no está cargado. Cargando...")
            if not self.load():
                return np.array([])
        
        try:
            # Usar valores por defecto de las preferencias si no se especifican
            language = language or self.user_preferences["language"]
            gender = gender or self.user_preferences["gender"]
            speed = speed or self.user_preferences["speed"]
            pitch_shift = pitch_shift or self.user_preferences["pitch"]
            emotion = emotion or self.user_preferences["emotion"]
            
            # Normalizar código de idioma para XTTS (solo usa códigos, no nombres completos)
            if language in self.LANGUAGE_CODES:
                tts_language = language
            elif language in self.LANGUAGE_NAMES:
                tts_language = self.LANGUAGE_NAMES[language]
            else:
                tts_language = "es"  # Valor por defecto
                
            logger.info(f"Sintetizando voz para texto: {text[:50]}... [Idioma: {tts_language}, Género: {gender}]")
            
            # Determinar el archivo de referencia para la voz
            if custom_voice_id:
                # Usar voz personalizada
                speaker_wav = self.get_custom_voice(custom_voice_id)
                if not speaker_wav:
                    logger.warning(f"Voz personalizada {custom_voice_id} no encontrada, usando voz estándar")
                    speaker_wav = None
            
            # Si no se proporciona un archivo de referencia, buscar uno según idioma y género
            if speaker_wav is None:
                try:
                    speaker_wav = self.find_voice(language, gender)
                except VoiceNotFoundError as e:
                    logger.warning(f"No se encontró una voz adecuada: {e}")
                    # Intentar usar una voz predeterminada del modelo
                    import glob
                    sample_files = glob.glob(os.path.join(self.model_path, "samples/*.wav"))
                    if sample_files:
                        speaker_wav = sample_files[0]
                        logger.info(f"Usando voz predeterminada del modelo: {speaker_wav}")
                    else:
                        raise ValueError("No se encontró ninguna voz de referencia")
            
            # Generar voz
            gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(
                audio_path=speaker_wav, 
                gpt_cond_len=30, 
                max_ref_length=15  # Aumentado para capturar más características de la voz
            )
            
            # Configuración basada en emociones
            temperature = 0.7
            if emotion == "happy":
                temperature = 0.8  # Más variación para emociones alegres
            elif emotion == "sad":
                temperature = 0.6  # Menos variación para tristeza
            elif emotion == "angry":
                temperature = 0.85  # Alta variación para enfado
                
            # Dividir texto largo en segmentos para mejor procesamiento
            max_length = 250
            segments = self._split_text(text, max_length)
            audio_segments = []
            
            for segment in segments:
                out = self.model.inference(
                    text=segment,
                    language=tts_language,
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    temperature=temperature,
                    # Para calidad óptima, usamos estos parámetros en high_quality
                    length_penalty=1.0,
                    repetition_penalty=2.0,
                    top_k=50,
                    top_p=0.85
                )
                
                # Convertir a numpy array
                segment_audio = out["wav"].squeeze().cpu().numpy()
                audio_segments.append(segment_audio)
            
            # Unir todos los segmentos
            if len(audio_segments) > 1:
                # Añadir pequeñas pausas entre segmentos
                pause = np.zeros(int(0.2 * self.sample_rate))
                final_audio = np.concatenate([seg for pair in zip(audio_segments, [pause] * len(audio_segments)) for seg in pair][:-1])
            else:
                final_audio = audio_segments[0]
                
            # Aplicar procesamiento post-síntesis
            final_audio = self._apply_post_processing(final_audio, speed, pitch_shift, emotion)
            
            # Actualizar tiempo de último uso
            self.last_use_time = time.time()
            
            logger.info(f"Voz sintetizada con {len(final_audio)} muestras")
            return final_audio
            
        except Exception as e:
            logger.error(f"Error al sintetizar voz: {e}")
            return np.array([])
    
    def _split_text(self, text: str, max_length: int = 250) -> List[str]:
        """
        Divide un texto largo en segmentos más pequeños para mejor procesamiento.
        
        Args:
            text: Texto a dividir
            max_length: Longitud máxima de cada segmento
            
        Returns:
            Lista de segmentos de texto
        """
        # Si el texto es corto, devolverlo tal cual
        if len(text) <= max_length:
            return [text]
        
        # Dividir por signos de puntuación
        segments = []
        separators = [".", ";", "!", "?", ":", "\n"]
        
        current_segment = ""
        for char in text:
            current_segment += char
            
            # Si llegamos a un separador y el segmento es suficientemente largo, cortar
            if char in separators and len(current_segment) > 20:
                segments.append(current_segment)
                current_segment = ""
                
            # Si el segmento es muy largo sin separadores, forzar corte
            if len(current_segment) >= max_length:
                if " " in current_segment:
                    # Cortar por el último espacio
                    last_space = current_segment.rfind(" ")
                    segments.append(current_segment[:last_space])
                    current_segment = current_segment[last_space+1:]
                else:
                    # Si no hay espacios, cortar tal cual
                    segments.append(current_segment)
                    current_segment = ""
        
        # Añadir el último segmento si queda algo
        if current_segment:
            segments.append(current_segment)
            
        return segments
    
    def _apply_post_processing(self, audio: np.ndarray, speed: float = None, 
                              pitch_shift: float = None, emotion: str = None) -> np.ndarray:
        """
        Aplica procesamiento avanzado al audio sintetizado.
        
        Args:
            audio: Array de audio a procesar
            speed: Factor de velocidad (0.5-1.5)
            pitch_shift: Cambio de tono (-0.5 a 0.5)
            emotion: Emoción a reforzar
            
        Returns:
            Audio procesado
        """
        try:
            processed_audio = audio.copy()
            
            # Ajustar velocidad si se especifica
            if speed is not None and speed != 1.0:
                from librosa.effects import time_stretch
                processed_audio = time_stretch(y=processed_audio, rate=speed)
            
            # Ajustar tono si se especifica
            if pitch_shift is not None and pitch_shift != 0.0:
                from librosa.effects import pitch_shift as librosa_pitch_shift
                # Convertir el rango -0.5 a 0.5 a -5 a 5 semitonos
                semitones = pitch_shift * 10
                processed_audio = librosa_pitch_shift(y=processed_audio, sr=self.sample_rate, 
                                                    n_steps=semitones)
            
            # Aplicar efectos según la emoción
            if emotion:
                if emotion == "happy":
                    # Aumentar ligeramente el tono y velocidad
                    from librosa.effects import pitch_shift as librosa_pitch_shift
                    if pitch_shift is None:  # Solo si no se especificó manualmente
                        processed_audio = librosa_pitch_shift(y=processed_audio, sr=self.sample_rate, 
                                                           n_steps=1.0)
                
                elif emotion == "sad":
                    # Reducir ligeramente el tono y velocidad
                    from librosa.effects import pitch_shift as librosa_pitch_shift
                    if pitch_shift is None:  # Solo si no se especificó manualmente
                        processed_audio = librosa_pitch_shift(y=processed_audio, sr=self.sample_rate, 
                                                           n_steps=-1.5)
                
                elif emotion == "angry":
                    # Aumentar energía en frecuencias medias
                    from scipy import signal
                    b, a = signal.butter(4, [500/(self.sample_rate/2), 2000/(self.sample_rate/2)], 'bandpass')
                    boosted = signal.lfilter(b, a, processed_audio)
                    processed_audio = processed_audio + 0.3 * boosted
            
            # Normalización final para evitar clipping
            max_val = np.max(np.abs(processed_audio))
            if max_val > 0:
                processed_audio = processed_audio / max_val * 0.95
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en post-procesamiento de audio: {e}. Devolviendo audio original.")
            return audio
    
    def save_audio(self, audio: np.ndarray, output_path: str, sample_rate: int = None) -> bool:
        """
        Guarda el audio sintetizado en un archivo.
        
        Args:
            audio: Array de audio
            output_path: Ruta de salida
            sample_rate: Tasa de muestreo
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            sr = sample_rate or self.sample_rate
            sf.write(output_path, audio, sr)
            logger.info(f"Audio guardado en {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar audio: {e}")
            return False
    
    def set_preference(self, key: str, value: Any) -> bool:
        """
        Establece una preferencia de usuario.
        
        Args:
            key: Clave de preferencia
            value: Valor a establecer
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        if key not in self.user_preferences:
            logger.warning(f"Preferencia desconocida: {key}")
            return False
            
        self.user_preferences[key] = value
        logger.info(f"Preferencia establecida: {key} = {value}")
        return True
    
    def unload(self, timeout: int = 300):
        """
        Libera la memoria del modelo si ha pasado cierto tiempo desde el último uso.
        
        Args:
            timeout: Tiempo en segundos desde el último uso para liberar memoria
        """
        if self.model is None:
            return
            
        # Si ha pasado suficiente tiempo desde el último uso, liberar memoria
        if time.time() - self.last_use_time > timeout:
            del self.model
            self.model = None
            
            # Limpiar caché de CUDA si está disponible
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info(f"Modelo de síntesis de voz descargado de memoria por inactividad ({timeout}s)")
    
    def get_custom_voices(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de voces personalizadas.
        
        Args:
            user_id: ID del usuario (opcional, para filtrar por usuario)
            
        Returns:
            Lista de diccionarios con información de voces personalizadas
        """
        voices = []
        
        for voice_id, metadata in self.custom_voice_metadata.items():
            # Filtrar por usuario si se especifica
            if user_id and metadata.get("user_id") != user_id:
                continue
                
            # Verificar que el archivo existe
            sample_path = metadata.get("sample_path")
            if sample_path and os.path.exists(sample_path):
                voices.append({
                    "voice_id": voice_id,
                    "name": metadata.get("name", "Voz sin nombre"),
                    "language": metadata.get("language", "unknown"),
                    "gender": metadata.get("gender", "unknown"),
                    "duration": metadata.get("duration", 0),
                    "user_id": metadata.get("user_id", "unknown"),
                    "created_at": metadata.get("created_at", 0)
                })
        
        return voices
