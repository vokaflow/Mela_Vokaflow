"""
Gestor avanzado de voces para VokaFlow.
Gestiona la indexación, selección y optimización de voces.
"""
import os
import json
import glob
import time
import random
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from pathlib import Path

logger = logging.getLogger("vicky.utils.voice_manager")

class VoiceManager:
    """
    Gestor avanzado para voces de síntesis.
    """
    
    def __init__(self, voice_dir: str = "/mnt/nvme_fast/vokaflow_models/tts/coquis_voices",
                cache_dir: str = "/mnt/nvme_fast/vokaflow_data/voice_cache"):
        """
        Inicializa el gestor de voces.
        
        Args:
            voice_dir: Directorio con voces organizadas
            cache_dir: Directorio para caché de voces
        """
        self.voice_dir = voice_dir
        self.cache_dir = cache_dir
        
        # Información de voces
        self.voice_index = {}
        self.voice_metadata = {}
        self.stats = {}
        
        # Preferencias de usuario y cache de uso
        self.user_preferences = {}
        self.usage_history = {}
        self.feature_vectors = {}
        
        # Asegurar que existan los directorios
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cargar índice de voces
        self._load_or_create_index()
        
        logger.info(f"Gestor de voces inicializado con {self._count_total_voices()} voces")
        
    def _count_total_voices(self) -> int:
        """
        Cuenta el número total de voces indexadas.
        
        Returns:
            Número total de voces
        """
        total = 0
        for lang, genders in self.voice_index.items():
            for gender, voices in genders.items():
                total += len(voices)
        return total
        
    def _load_or_create_index(self) -> None:
        """
        Carga o crea el índice de voces.
        """
        # Comprobar si existe un índice previo
        index_path = os.path.join(self.cache_dir, "voice_index.json")
        metadata_path = os.path.join(self.cache_dir, "voice_metadata.json")
        
        # Intentar cargar índice existente
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                with open(index_path, "r") as f:
                    self.voice_index = json.load(f)
                    
                with open(metadata_path, "r") as f:
                    self.voice_metadata = json.load(f)
                    
                # Verificar que el índice no está desactualizado
                if self._validate_index():
                    logger.info(f"Índice de voces cargado desde caché: {self._count_total_voices()} voces")
                    self._calculate_stats()
                    return
                else:
                    logger.warning("Índice de voces desactualizado, creando uno nuevo")
            except Exception as e:
                logger.error(f"Error al cargar índice de voces: {e}")
        
        # Crear nuevo índice
        self._create_index()
        self._calculate_stats()
        self._save_index()
        
    def _validate_index(self) -> bool:
        """
        Valida que el índice cargado corresponde con los archivos disponibles.
        
        Returns:
            True si es válido, False si no
        """
        # Verificar que las carpetas de idioma existen
        for language in self.voice_index.keys():
            lang_path = os.path.join(self.voice_dir, language)
            if not os.path.exists(lang_path):
                return False
        
        # Verificar algunos archivos al azar
        sample_count = min(10, self._count_total_voices())
        checked = 0
        
        for language, genders in self.voice_index.items():
            for gender, voices in genders.items():
                for voice_id in voices:
                    if voice_id in self.voice_metadata:
                        path = self.voice_metadata[voice_id]["path"]
                        if not os.path.exists(path):
                            return False
                        checked += 1
                        if checked >= sample_count:
                            return True
        
        return True
        
    def _create_index(self) -> None:
        """
        Crea un nuevo índice de voces.
        """
        self.voice_index = {}
        self.voice_metadata = {}
        
        if not os.path.exists(self.voice_dir):
            logger.warning(f"Directorio de voces no encontrado: {self.voice_dir}")
            return
            
        # Iterar por cada idioma
        for lang_dir in os.listdir(self.voice_dir):
            lang_path = os.path.join(self.voice_dir, lang_dir)
            if not os.path.isdir(lang_path):
                continue
                
            language = lang_dir.lower()
            self.voice_index[language] = {}
            
            # Iterar por cada género dentro del idioma
            for gender_dir in os.listdir(lang_path):
                gender_path = os.path.join(lang_path, gender_dir)
                if not os.path.isdir(gender_path):
                    continue
                    
                gender = gender_dir.lower()
                self.voice_index[language][gender] = []
                
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
                        logger.debug(f"Voz indexada: {voice_id} ({language}/{gender})")
                    except Exception as e:
                        logger.warning(f"Error al analizar archivo de voz {voice_id}: {e}")
        
        logger.info(f"Índice de voces creado: {self._count_total_voices()} voces en {len(self.voice_index)} idiomas")
                
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
            creation_time = os.path.getctime(file_path)
            
            # Cargar audio para análisis
            import soundfile as sf
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
                "creation_time": creation_time,
                "analyzed_at": time.time()
            }
        except Exception as e:
            logger.error(f"Error al analizar archivo de audio {file_path}: {e}")
            return {
                "path": file_path,
                "error": str(e),
                "quality": "unknown"
            }
            
    def _calculate_stats(self) -> None:
        """
        Calcula estadísticas del conjunto de voces.
        """
        stats = {
            "total_voices": self._count_total_voices(),
            "languages": {},
            "genders": {"male": 0, "female": 0},
            "quality": {"high": 0, "medium": 0, "low": 0, "unknown": 0},
            "total_duration": 0,
            "avg_duration": 0
        }
        
        # Contar por idioma y género
        for language, genders in self.voice_index.items():
            stats["languages"][language] = sum(len(voices) for voices in genders.values())
            
            for gender, voices in genders.items():
                if gender in stats["genders"]:
                    stats["genders"][gender] += len(voices)
        
        # Contar por calidad y calcular duración
        total_duration = 0
        count_with_duration = 0
        
        for voice_id, metadata in self.voice_metadata.items():
            quality = metadata.get("quality", "unknown")
            if quality in stats["quality"]:
                stats["quality"][quality] += 1
                
            duration = metadata.get("duration")
            if duration:
                total_duration += duration
                count_with_duration += 1
        
        stats["total_duration"] = total_duration
        stats["avg_duration"] = total_duration / count_with_duration if count_with_duration > 0 else 0
        
        self.stats = stats
        logger.info(f"Estadísticas de voces calculadas: {stats['total_voices']} voces, {len(stats['languages'])} idiomas")
        
    def _save_index(self) -> None:
        """
        Guarda el índice de voces en el caché.
        """
        try:
            index_path = os.path.join(self.cache_dir, "voice_index.json")
            metadata_path = os.path.join(self.cache_dir, "voice_metadata.json")
            stats_path = os.path.join(self.cache_dir, "voice_stats.json")
            
            with open(index_path, "w") as f:
                json.dump(self.voice_index, f, indent=2)
                
            with open(metadata_path, "w") as f:
                json.dump(self.voice_metadata, f, indent=2)
                
            with open(stats_path, "w") as f:
                json.dump(self.stats, f, indent=2)
                
            logger.info(f"Índice de voces guardado en {self.cache_dir}")
        except Exception as e:
            logger.error(f"Error al guardar índice de voces: {e}")
            
    def get_available_languages(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de idiomas disponibles.
        
        Returns:
            Lista de diccionarios con información de idiomas disponibles
        """
        languages = []
        for language, genders in self.voice_index.items():
            voice_count = sum(len(voices) for voices in genders.values())
            if voice_count > 0:
                languages.append({
                    "name": language,
                    "voice_count": voice_count,
                    "has_male": "male" in genders and len(genders["male"]) > 0,
                    "has_female": "female" in genders and len(genders["female"]) > 0
                })
                
        return sorted(languages, key=lambda x: x["name"])
        
    def get_voices(self, language: str = None, gender: str = None, 
                  quality: str = None, min_duration: float = None) -> List[Dict[str, Any]]:
        """
        Obtiene las voces disponibles según los criterios especificados.
        
        Args:
            language: Idioma deseado
            gender: Género deseado ("male" o "female")
            quality: Calidad mínima ("low", "medium", "high")
            min_duration: Duración mínima en segundos
            
        Returns:
            Lista de diccionarios con información de voces
        """
        voices = []
        
        # Si no se especifica idioma, buscar en todos
        languages_to_search = [language] if language else self.voice_index.keys()
        
        for lang in languages_to_search:
            if lang not in self.voice_index:
                continue
                
            # Si no se especifica género, buscar en todos
            genders_to_search = [gender] if gender else self.voice_index[lang].keys()
            
            for gen in genders_to_search:
                if gen not in self.voice_index[lang]:
                    continue
                    
                # Obtener todas las voces para este idioma y género
                for voice_id in self.voice_index[lang][gen]:
                    if voice_id not in self.voice_metadata:
                        continue
                        
                    metadata = self.voice_metadata[voice_id]
                    
                    # Filtrar por calidad
                    if quality and metadata.get("quality") != quality:
                        continue
                        
                    # Filtrar por duración mínima
                    if min_duration and metadata.get("duration", 0) < min_duration:
                        continue
                        
                    # Añadir a la lista
                    voices.append({
                        "id": voice_id,
                        "path": metadata["path"],
                        "language": lang,
                        "gender": gen,
                        "quality": metadata.get("quality", "unknown"),
                        "duration": metadata.get("duration", 0),
                        "file_size": metadata.get("file_size", 0)
                    })
        
        return voices
        
    def find_best_voice(self, language: str = None, gender: str = None, text_context: str = None) -> Optional[str]:
        """
        Encuentra la mejor voz según los criterios especificados.
        
        Args:
            language: Idioma deseado
            gender: Género deseado
            text_context: Texto para contexto (para seleccionar voz adecuada)
            
        Returns:
            Ruta a la mejor voz, o None si no se encuentra ninguna
        """
        # Obtener voces disponibles con estos criterios
        voices = self.get_voices(language=language, gender=gender, quality="high")
        
        # Si no hay voces de alta calidad, intentar con calidad media
        if not voices:
            voices = self.get_voices(language=language, gender=gender, quality="medium")
            
        # Si aún no hay voces, intentar con cualquier calidad
        if not voices:
            voices = self.get_voices(language=language, gender=gender)
            
        # Si no se encuentra ninguna voz con estos criterios, ampliar búsqueda
        if not voices:
            # Intentar cualquier género para este idioma
            voices = self.get_voices(language=language)
            
            # Si aún así no hay voces, usar cualquier idioma con el género especificado
            if not voices and gender:
                voices = self.get_voices(gender=gender, quality="high")
                
            # Como último recurso, usar cualquier voz disponible de alta calidad
            if not voices:
                voices = self.get_voices(quality="high")
                
            # Si definitivamente no hay voces, devolver None
            if not voices:
                return None
        
        # Entre las voces disponibles, seleccionar la mejor
        if len(voices) == 1:
            best_voice = voices[0]
        else:
            # Ordenar por calidad y duración
            voices_sorted = sorted(
                voices, 
                key=lambda x: (
                    {"high": 3, "medium": 2, "low": 1, "unknown": 0}.get(x["quality"], 0),
                    x["duration"]
                ),
                reverse=True
            )
            
            # Si hay varias voces de la mejor calidad, alternar entre ellas
            best_voices = [v for v in voices_sorted if v["quality"] == voices_sorted[0]["quality"]]
            best_voice = random.choice(best_voices)
        
        # Registrar uso de esta voz
        voice_id = best_voice["id"]
        self._register_voice_usage(voice_id)
        
        logger.info(f"Mejor voz seleccionada: {voice_id} ({best_voice['language']}/{best_voice['gender']})")
        return best_voice["path"]
        
    def _register_voice_usage(self, voice_id: str) -> None:
        """
        Registra el uso de una voz para análisis y rotación.
        
        Args:
            voice_id: Identificador de la voz
        """
        if voice_id not in self.usage_history:
            self.usage_history[voice_id] = []
            
        self.usage_history[voice_id].append(time.time())
        
        # Limitar el historial a los últimos 100 usos
        if len(self.usage_history[voice_id]) > 100:
            self.usage_history[voice_id] = self.usage_history[voice_id][-100:]
    
    def get_voice_usage_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de voces.
        
        Returns:
            Diccionario con estadísticas de uso
        """
        stats = {
            "total_usages": sum(len(history) for history in self.usage_history.values()),
            "unique_voices_used": len(self.usage_history),
            "most_used_voice": None,
            "most_used_count": 0,
            "usage_by_language": {},
            "usage_by_gender": {"male": 0, "female": 0}
        }
        
        # Encontrar la voz más usada
        for voice_id, history in self.usage_history.items():
            if len(history) > stats["most_used_count"]:
                stats["most_used_count"] = len(history)
                stats["most_used_voice"] = voice_id
                
            # Contabilizar por idioma y género
            if voice_id in self.voice_metadata:
                metadata = self.voice_metadata[voice_id]
                language = metadata.get("language", "unknown")
                gender = metadata.get("gender", "unknown")
                
                if language not in stats["usage_by_language"]:
                    stats["usage_by_language"][language] = 0
                stats["usage_by_language"][language] += len(history)
                
                if gender in stats["usage_by_gender"]:
                    stats["usage_by_gender"][gender] += len(history)
        
        return stats
        
    def set_user_preference(self, user_id: str, key: str, value: Any) -> None:
        """
        Establece una preferencia de usuario para voces.
        
        Args:
            user_id: Identificador del usuario
            key: Clave de preferencia
            value: Valor a establecer
        """
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
            
        self.user_preferences[user_id][key] = value
        logger.info(f"Preferencia establecida para usuario {user_id}: {key}={value}")
        
        # Guardar preferencias
        self._save_user_preferences()
        
    def get_user_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """
        Obtiene una preferencia de usuario.
        
        Args:
            user_id: Identificador del usuario
            key: Clave de preferencia
            default: Valor por defecto
            
        Returns:
            Valor de la preferencia
        """
        if user_id not in self.user_preferences:
            return default
            
        return self.user_preferences[user_id].get(key, default)
        
    def _save_user_preferences(self) -> None:
        """
        Guarda las preferencias de usuario.
        """
        try:
            prefs_path = os.path.join(self.cache_dir, "user_preferences.json")
            with open(prefs_path, "w") as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar preferencias de usuario: {e}")
            
    def _load_user_preferences(self) -> None:
        """
        Carga las preferencias de usuario.
        """
        prefs_path = os.path.join(self.cache_dir, "user_preferences.json")
        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, "r") as f:
                    self.user_preferences = json.load(f)
                logger.info(f"Preferencias cargadas para {len(self.user_preferences)} usuarios")
            except Exception as e:
                logger.error(f"Error al cargar preferencias de usuario: {e}")
                
    def generate_voice_samples(self, output_dir: str, text: str = "Este es un ejemplo de síntesis de voz.") -> Dict[str, str]:
        """
        Genera muestras de audio para cada idioma y género.
        
        Args:
            output_dir: Directorio de salida para las muestras
            text: Texto a sintetizar
            
        Returns:
            Diccionario con rutas a las muestras generadas
        """
        os.makedirs(output_dir, exist_ok=True)
        samples = {}
        
        # Importar el modelo TTS
        from ..models.tts_model import TTSModel
        tts = TTSModel()
        
        # Textos por idioma
        texts = {
            "english": "This is a sample of voice synthesis.",
            "spanish": "Este es un ejemplo de síntesis de voz.",
            "french": "Voici un exemple de synthèse vocale.",
            "german": "Dies ist ein Beispiel für Sprachsynthese.",
            "italian": "Questo è un esempio di sintesi vocale.",
            "portuguese": "Este é um exemplo de síntese de voz.",
            "chinese": "这是一个语音合成的例子。",
            "arabic": "هذا مثال على تخليق الصوت.",
            "indian": "यह वॉयस सिंथेसिस का एक उदाहरण है।"
        }
        
        # Verificar que el modelo está cargado
        if not tts.load():
            logger.error("No se pudo cargar el modelo TTS")
            return samples
        
        # Para cada idioma y género, generar una muestra
        for language in self.voice_index.keys():
            sample_text = texts.get(language, text)
            
            for gender in self.voice_index[language].keys():
                if self.voice_index[language][gender]:
                    try:
                        # Encontrar una voz adecuada
                        voice_path = self.find_best_voice(language, gender)
                        
                        if voice_path:
                            # Determinar el código de idioma
                            lang_code = "en" if language == "english" else "es"  # Simplificado
                            
                            # Sintetizar voz
                            audio = tts.synthesize(
                                text=sample_text,
