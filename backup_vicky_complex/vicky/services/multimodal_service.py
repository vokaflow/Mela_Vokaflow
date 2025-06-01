"""
Servicio de integración multimodal que conecta los sistemas de voz y traducción.
Permite flujos de trabajo avanzados como traducir-y-hablar o transcribir-traducir-hablar.
"""
import os
import logging
import time
import tempfile
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np

from ..core.model_manager import ModelManager
from ..models.translation_model import TranslationModel
from ..models.tts_model import TTSModel
from ..models.speech_model import SpeechModel

logger = logging.getLogger("vicky.services.multimodal_service")

class MultimodalService:
    """
    Servicio que integra múltiples modalidades (texto, voz, traducción) para
    proporcionar experiencias de usuario avanzadas.
    """
    
    def __init__(self):
        """
        Inicializa el servicio multimodal.
        """
        self.model_manager = ModelManager()
        self.temp_dir = tempfile.gettempdir()
        
        # Caché para evitar recargar modelos frecuentemente
        self._translation_model = None
        self._tts_model = None
        self._speech_model = None
        
        logger.info("Servicio multimodal inicializado")
    
    def _get_translation_model(self) -> TranslationModel:
        """
        Obtiene el modelo de traducción, cargándolo si es necesario.
        
        Returns:
            Modelo de traducción
        """
        if self._translation_model is None:
            self._translation_model = self.model_manager.get_model("translation")
            if self._translation_model is None:
                logger.error("No se pudo cargar el modelo de traducción")
                raise RuntimeError("No se pudo cargar el modelo de traducción")
        return self._translation_model
    
    def _get_tts_model(self) -> TTSModel:
        """
        Obtiene el modelo de síntesis de voz, cargándolo si es necesario.
        
        Returns:
            Modelo de síntesis de voz
        """
        if self._tts_model is None:
            self._tts_model = self.model_manager.get_model("tts")
            if self._tts_model is None:
                logger.error("No se pudo cargar el modelo de síntesis de voz")
                raise RuntimeError("No se pudo cargar el modelo de síntesis de voz")
        return self._tts_model
    
    def _get_speech_model(self) -> SpeechModel:
        """
        Obtiene el modelo de reconocimiento de voz, cargándolo si es necesario.
        
        Returns:
            Modelo de reconocimiento de voz
        """
        if self._speech_model is None:
            self._speech_model = self.model_manager.get_model("speech")
            if self._speech_model is None:
                logger.error("No se pudo cargar el modelo de reconocimiento de voz")
                raise RuntimeError("No se pudo cargar el modelo de reconocimiento de voz")
        return self._speech_model
    
    def translate_and_speak(self, text: str, source_lang: str = None, target_lang: str = "es", 
                           gender: str = None, emotion: str = None, output_path: str = None) -> Dict[str, Any]:
        """
        Traduce un texto y lo convierte a voz.
        
        Args:
            text: Texto a traducir y convertir a voz
            source_lang: Idioma de origen (auto-detectado si es None)
            target_lang: Idioma de destino
            gender: Género de la voz (male/female)
            emotion: Emoción a transmitir (neutral, happy, sad, angry)
            output_path: Ruta donde guardar el archivo de audio (opcional)
            
        Returns:
            Diccionario con información del proceso y resultados
        """
        start_time = time.time()
        result = {
            "success": False,
            "translated_text": None,
            "audio_path": None,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "processing_time": 0
        }
        
        try:
            logger.info(f"Iniciando proceso de traducción y síntesis de voz para: {text[:50]}...")
            
            # 1. Traducir el texto
            translation_model = self._get_translation_model()
            translated_text = translation_model.translate(text, source_lang, target_lang)
            
            # Detectar el idioma de origen si no se especificó
            if source_lang is None:
                source_lang = translation_model.detect_language(text)
            
            result["translated_text"] = translated_text
            result["source_lang"] = source_lang
            
            logger.info(f"Texto traducido de {source_lang} a {target_lang}: {translated_text[:50]}...")
            
            # 2. Convertir a voz
            tts_model = self._get_tts_model()
            audio = tts_model.synthesize(
                text=translated_text,
                language=target_lang,
                gender=gender,
                emotion=emotion
            )
            
            # 3. Guardar el audio si se especificó una ruta
            if output_path:
                audio_path = output_path
            else:
                # Generar una ruta temporal
                audio_path = os.path.join(self.temp_dir, f"vicky_translated_{int(time.time())}.wav")
            
            if tts_model.save_audio(audio, audio_path):
                result["audio_path"] = audio_path
                result["success"] = True
            
            # Calcular tiempo de procesamiento
            result["processing_time"] = time.time() - start_time
            
            logger.info(f"Proceso completado en {result['processing_time']:.2f} segundos")
            return result
            
        except Exception as e:
            logger.error(f"Error en el proceso de traducción y síntesis: {e}")
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result
    
    def transcribe_translate_speak(self, audio_path: str, source_lang: str = None, 
                                  target_lang: str = "es", gender: str = None,
                                  emotion: str = None, output_path: str = None) -> Dict[str, Any]:
        """
        Transcribe un audio, traduce el texto y lo convierte a voz en otro idioma.
        
        Args:
            audio_path: Ruta al archivo de audio a transcribir
            source_lang: Idioma de origen del audio (auto-detectado si es None)
            target_lang: Idioma de destino para la traducción y síntesis
            gender: Género de la voz (male/female)
            emotion: Emoción a transmitir (neutral, happy, sad, angry)
            output_path: Ruta donde guardar el archivo de audio resultante
            
        Returns:
            Diccionario con información del proceso y resultados
        """
        start_time = time.time()
        result = {
            "success": False,
            "transcribed_text": None,
            "translated_text": None,
            "original_audio": audio_path,
            "output_audio": None,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "processing_time": 0
        }
        
        try:
            logger.info(f"Iniciando proceso de transcripción, traducción y síntesis para: {audio_path}")
            
            # 1. Transcribir el audio
            speech_model = self._get_speech_model()
            transcribed_text = speech_model.transcribe(audio_path, language=source_lang)
            
            # Detectar el idioma si no se especificó
            if source_lang is None:
                source_lang = speech_model.detect_language(audio_path)
            
            result["transcribed_text"] = transcribed_text
            result["source_lang"] = source_lang
            
            logger.info(f"Audio transcrito: {transcribed_text[:50]}...")
            
            # 2. Traducir el texto
            translation_model = self._get_translation_model()
            translated_text = translation_model.translate(transcribed_text, source_lang, target_lang)
            
            result["translated_text"] = translated_text
            
            logger.info(f"Texto traducido de {source_lang} a {target_lang}: {translated_text[:50]}...")
            
            # 3. Convertir a voz
            tts_model = self._get_tts_model()
            audio = tts_model.synthesize(
                text=translated_text,
                language=target_lang,
                gender=gender,
                emotion=emotion
            )
            
            # 4. Guardar el audio
            if output_path:
                audio_path = output_path
            else:
                # Generar una ruta temporal
                audio_path = os.path.join(self.temp_dir, f"vicky_transcribed_translated_{int(time.time())}.wav")
            
            if tts_model.save_audio(audio, audio_path):
                result["output_audio"] = audio_path
                result["success"] = True
            
            # Calcular tiempo de procesamiento
            result["processing_time"] = time.time() - start_time
            
            logger.info(f"Proceso completado en {result['processing_time']:.2f} segundos")
            return result
            
        except Exception as e:
            logger.error(f"Error en el proceso de transcripción, traducción y síntesis: {e}")
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result
    
    def batch_translate_speak(self, texts: List[str], source_lang: str = None, 
                             target_lang: str = "es", gender: str = None,
                             emotion: str = None) -> List[Dict[str, Any]]:
        """
        Procesa un lote de textos para traducirlos y convertirlos a voz.
        
        Args:
            texts: Lista de textos a procesar
            source_lang: Idioma de origen (auto-detectado si es None)
            target_lang: Idioma de destino
            gender: Género de la voz (male/female)
            emotion: Emoción a transmitir (neutral, happy, sad, angry)
            
        Returns:
            Lista de diccionarios con resultados para cada texto
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Procesando texto {i+1}/{len(texts)}")
            result = self.translate_and_speak(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                gender=gender,
                emotion=emotion
            )
            results.append(result)
        
        return results
    
    def create_multilingual_audio(self, text: str, languages: List[str], 
                                 gender: str = None, output_dir: str = None) -> Dict[str, Any]:
        """
        Crea versiones de audio del mismo texto en múltiples idiomas.
        
        Args:
            text: Texto a traducir y convertir a voz
            languages: Lista de códigos de idioma
            gender: Género de la voz (male/female)
            output_dir: Directorio donde guardar los archivos de audio
            
        Returns:
            Diccionario con rutas de audio por idioma
        """
        if output_dir is None:
            output_dir = self.temp_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        result = {
            "success": True,
            "original_text": text,
            "audio_files": {},
            "errors": {}
        }
        
        # Detectar idioma del texto original
        translation_model = self._get_translation_model()
        source_lang = translation_model.detect_language(text)
        result["source_language"] = source_lang
        
        for lang in languages:
            try:
                # Traducir y sintetizar
                lang_result = self.translate_and_speak(
                    text=text,
                    source_lang=source_lang,
                    target_lang=lang,
                    gender=gender,
                    output_path=os.path.join(output_dir, f"audio_{lang}.wav")
                )
                
                if lang_result["success"]:
                    result["audio_files"][lang] = lang_result["audio_path"]
                    result["translated_text"] = lang_result["translated_text"]
                else:
                    result["errors"][lang] = lang_result.get("error", "Error desconocido")
                    result["success"] = False
                    
            except Exception as e:
                logger.error(f"Error al procesar idioma {lang}: {e}")
                result["errors"][lang] = str(e)
                result["success"] = False
        
        return result
    
    def translate_with_voice_preservation(self, audio_path: str, target_lang: str = "es", 
                                         output_path: str = None) -> Dict[str, Any]:
        """
        Traduce un audio manteniendo características de la voz original.
        
        Args:
            audio_path: Ruta al archivo de audio a traducir
            target_lang: Idioma de destino
            output_path: Ruta donde guardar el archivo de audio resultante
            
        Returns:
            Diccionario con información del proceso y resultados
        """
        start_time = time.time()
        result = {
            "success": False,
            "transcribed_text": None,
            "translated_text": None,
            "original_audio": audio_path,
            "output_audio": None,
            "target_lang": target_lang,
            "processing_time": 0
        }
        
        try:
            logger.info(f"Iniciando traducción con preservación de voz para: {audio_path}")
            
            # 1. Transcribir el audio
            speech_model = self._get_speech_model()
            transcribed_text = speech_model.transcribe(audio_path)
            source_lang = speech_model.detect_language(audio_path)
            
            result["transcribed_text"] = transcribed_text
            result["source_lang"] = source_lang
            
            # 2. Traducir el texto
            translation_model = self._get_translation_model()
            translated_text = translation_model.translate(transcribed_text, source_lang, target_lang)
            
            result["translated_text"] = translated_text
            
            # 3. Sintetizar voz usando el audio original como referencia
            tts_model = self._get_tts_model()
            audio = tts_model.synthesize(
                text=translated_text,
                language=target_lang,
                speaker_wav=audio_path  # Usar el audio original como referencia para clonar la voz
            )
            
            # 4. Guardar el audio
            if output_path:
                audio_path = output_path
            else:
                audio_path = os.path.join(self.temp_dir, f"vicky_voice_preserved_{int(time.time())}.wav")
            
            if tts_model.save_audio(audio, audio_path):
                result["output_audio"] = audio_path
                result["success"] = True
            
            # Calcular tiempo de procesamiento
            result["processing_time"] = time.time() - start_time
            
            logger.info(f"Proceso completado en {result['processing_time']:.2f} segundos")
            return result
            
        except Exception as e:
            logger.error(f"Error en la traducción con preservación de voz: {e}")
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result
    
    def unload_models(self):
        """
        Libera la memoria de todos los modelos cargados.
        """
        if self._translation_model:
            self.model_manager.unload_model("translation")
            self._translation_model = None
            
        if self._tts_model:
            self.model_manager.unload_model("tts")
            self._tts_model = None
            
        if self._speech_model:
            self.model_manager.unload_model("speech")
            self._speech_model = None
            
        logger.info("Modelos descargados de memoria")
