"""
Módulo para la clonación de voz personalizada en VokaFlow.
Permite a los usuarios clonar su propia voz para utilizarla en el sistema TTS.
"""
import os
import time
import logging
import json
import uuid
import shutil
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import soundfile as sf

logger = logging.getLogger("vicky.core.voice_cloning")

class VoiceCloner:
    """
    Clase para gestionar la clonación de voces de usuarios.
    Permite procesar, analizar y almacenar muestras de voz para su uso
    en la síntesis de voz personalizada.
    """
    
    def __init__(self, base_dir: str = None, min_sample_duration: float = 10.0):
        """
        Inicializa el sistema de clonación de voz.
        
        Args:
            base_dir: Directorio base para almacenar las voces clonadas
            min_sample_duration: Duración mínima (en segundos) para muestras de voz
        """
        # Configurar directorio base
        self.base_dir = base_dir or "/mnt/nvme_fast/vokaflow_models/tts/custom_voices"
        self.users_dir = os.path.join(self.base_dir, "users")
        self.temp_dir = os.path.join(self.base_dir, "temp")
        
        # Asegurar que existan los directorios
        os.makedirs(self.users_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configuración
        self.min_sample_duration = min_sample_duration
        self.supported_formats = [".wav", ".mp3", ".ogg", ".flac"]
        self.sample_rate = 24000  # Tasa de muestreo para XTTS
        
        # Metadatos de voces
        self.voice_metadata = {}
        self._load_metadata()
        
        logger.info(f"Sistema de clonación de voz inicializado en {self.base_dir}")
        logger.info(f"Formatos soportados: {', '.join(self.supported_formats)}")
    
    def _load_metadata(self) -> None:
        """
        Carga los metadatos de voces personalizadas.
        """
        metadata_path = os.path.join(self.base_dir, "voice_metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    self.voice_metadata = json.load(f)
                logger.info(f"Metadatos de voces cargados: {len(self.voice_metadata)} voces")
            except Exception as e:
                logger.error(f"Error al cargar metadatos de voces: {e}")
                self.voice_metadata = {}
    
    def _save_metadata(self) -> None:
        """
        Guarda los metadatos de voces personalizadas.
        """
        metadata_path = os.path.join(self.base_dir, "voice_metadata.json")
        try:
            with open(metadata_path, "w") as f:
                json.dump(self.voice_metadata, f, indent=2)
            logger.info(f"Metadatos de voces guardados: {len(self.voice_metadata)} voces")
        except Exception as e:
            logger.error(f"Error al guardar metadatos de voces: {e}")
    
    def process_voice_sample(self, sample_path: str, user_id: str, 
                            voice_name: str, language: str, gender: str,
                            description: str = None) -> Dict[str, Any]:
        """
        Procesa una muestra de voz para su uso en clonación.
        
        Args:
            sample_path: Ruta al archivo de audio de muestra
            user_id: ID del usuario
            voice_name: Nombre asignado a la voz
            language: Idioma principal de la voz
            gender: Género de la voz (male/female)
            description: Descripción opcional
            
        Returns:
            Diccionario con información de la voz procesada
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(sample_path):
                return {"success": False, "error": "Archivo no encontrado"}
            
            # Verificar formato
            file_ext = os.path.splitext(sample_path)[1].lower()
            if file_ext not in self.supported_formats:
                return {
                    "success": False, 
                    "error": f"Formato no soportado. Formatos válidos: {', '.join(self.supported_formats)}"
                }
            
            # Analizar audio
            try:
                info = sf.info(sample_path)
                duration = info.duration
                sample_rate = info.samplerate
                channels = info.channels
            except Exception as e:
                return {"success": False, "error": f"Error al analizar audio: {e}"}
            
            # Verificar duración mínima
            if duration < self.min_sample_duration:
                return {
                    "success": False, 
                    "error": f"La muestra es demasiado corta. Se requieren al menos {self.min_sample_duration} segundos."
                }
            
            # Crear ID único para la voz
            voice_id = f"custom_{uuid.uuid4().hex[:8]}"
            
            # Crear directorio para el usuario si no existe
            user_dir = os.path.join(self.users_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Crear directorio para la voz
            voice_dir = os.path.join(user_dir, voice_id)
            os.makedirs(voice_dir, exist_ok=True)
            
            # Procesar y optimizar el audio
            processed_path = os.path.join(voice_dir, "voice_sample.wav")
            success, processing_info = self._optimize_audio(sample_path, processed_path)
            
            if not success:
                return {"success": False, "error": f"Error al procesar audio: {processing_info}"}
            
            # Crear metadatos
            metadata = {
                "voice_id": voice_id,
                "user_id": user_id,
                "name": voice_name,
                "language": language,
                "gender": gender,
                "description": description or "",
                "sample_path": processed_path,
                "original_filename": os.path.basename(sample_path),
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "created_at": time.time(),
                "processing_info": processing_info
            }
            
            # Guardar metadatos
            self.voice_metadata[voice_id] = metadata
            self._save_metadata()
            
            # Crear archivo de metadatos local
            with open(os.path.join(voice_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Voz personalizada creada: {voice_id} para usuario {user_id}")
            
            return {
                "success": True,
                "voice_id": voice_id,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error al procesar muestra de voz: {e}")
            return {"success": False, "error": str(e)}
    
    def _optimize_audio(self, input_path: str, output_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Optimiza una muestra de audio para su uso en clonación de voz.
        
        Args:
            input_path: Ruta al archivo de audio original
            output_path: Ruta donde guardar el audio optimizado
            
        Returns:
            Tupla (éxito, información de procesamiento)
        """
        processing_info = {}
        
        try:
            # Cargar audio
            data, sample_rate = sf.read(input_path)
            processing_info["original_sample_rate"] = sample_rate
            processing_info["original_duration"] = len(data) / sample_rate
            
            # Convertir a mono si es estéreo
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = np.mean(data, axis=1)
                processing_info["channels_converted"] = True
            
            # Normalizar volumen
            max_val = np.max(np.abs(data))
            if max_val > 0:
                data = data / max_val * 0.9
                processing_info["normalized"] = True
            
            # Recortar silencios al inicio y final
            data = self._trim_silence(data, sample_rate)
            processing_info["trimmed"] = True
            
            # Resamplear a la tasa requerida por XTTS si es necesario
            if sample_rate != self.sample_rate:
                try:
                    import librosa
                    data = librosa.resample(data, orig_sr=sample_rate, target_sr=self.sample_rate)
                    processing_info["resampled"] = True
                    processing_info["target_sample_rate"] = self.sample_rate
                except Exception as e:
                    logger.warning(f"Error al resamplear audio: {e}. Continuando con la tasa original.")
                    processing_info["resampling_error"] = str(e)
            
            # Guardar audio procesado
            sf.write(output_path, data, self.sample_rate if processing_info.get("resampled") else sample_rate)
            
            # Actualizar información de procesamiento
            processing_info["final_duration"] = len(data) / (self.sample_rate if processing_info.get("resampled") else sample_rate)
            processing_info["output_path"] = output_path
            
            return True, processing_info
            
        except Exception as e:
            logger.error(f"Error al optimizar audio: {e}")
            return False, {"error": str(e)}
    
    def _trim_silence(self, audio: np.ndarray, sample_rate: int, 
                     threshold: float = 0.02, min_silence_duration: float = 0.3) -> np.ndarray:
        """
        Recorta silencios al inicio y final del audio.
        
        Args:
            audio: Array de audio
            sample_rate: Tasa de muestreo
            threshold: Umbral para considerar silencio
            min_silence_duration: Duración mínima de silencio a recortar
            
        Returns:
            Audio recortado
        """
        # Calcular energía
        energy = np.abs(audio)
        
        # Encontrar índices donde la energía supera el umbral
        mask = energy > threshold
        
        if not np.any(mask):
            # Si todo es silencio, devolver el audio original
            return audio
        
        # Encontrar el primer y último índice no silencioso
        nonzero = np.where(mask)[0]
        start = nonzero[0]
        end = nonzero[-1] + 1
        
        # Ajustar para no cortar demasiado
        min_samples = int(min_silence_duration * sample_rate)
        start = max(0, start - min_samples)
        end = min(len(audio), end + min_samples)
        
        return audio[start:end]
    
    def get_user_voices(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las voces personalizadas de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de diccionarios con información de las voces
        """
        user_voices = []
        
        for voice_id, metadata in self.voice_metadata.items():
            if metadata.get("user_id") == user_id:
                # Verificar que el archivo de audio existe
                sample_path = metadata.get("sample_path")
                if sample_path and os.path.exists(sample_path):
                    user_voices.append(metadata)
                else:
                    logger.warning(f"Archivo de voz no encontrado para {voice_id}: {sample_path}")
        
        return user_voices
    
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una voz específica.
        
        Args:
            voice_id: ID de la voz
            
        Returns:
            Diccionario con información de la voz, o None si no existe
        """
        return self.voice_metadata.get(voice_id)
    
    def delete_voice(self, voice_id: str, user_id: str = None) -> bool:
        """
        Elimina una voz personalizada.
        
        Args:
            voice_id: ID de la voz a eliminar
            user_id: ID del usuario (para verificación)
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if voice_id not in self.voice_metadata:
            return False
        
        # Verificar que el usuario es el propietario
        if user_id and self.voice_metadata[voice_id].get("user_id") != user_id:
            logger.warning(f"Intento de eliminar voz {voice_id} por usuario no autorizado {user_id}")
            return False
        
        try:
            # Obtener ruta del directorio de la voz
            voice_metadata = self.voice_metadata[voice_id]
            sample_path = voice_metadata.get("sample_path")
            
            if sample_path:
                voice_dir = os.path.dirname(sample_path)
                
                # Eliminar directorio de la voz
                if os.path.exists(voice_dir):
                    shutil.rmtree(voice_dir)
            
            # Eliminar de los metadatos
            del self.voice_metadata[voice_id]
            self._save_metadata()
            
            logger.info(f"Voz personalizada eliminada: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar voz {voice_id}: {e}")
            return False
    
    def update_voice_metadata(self, voice_id: str, updates: Dict[str, Any], 
                             user_id: str = None) -> bool:
        """
        Actualiza los metadatos de una voz personalizada.
        
        Args:
            voice_id: ID de la voz
            updates: Diccionario con los campos a actualizar
            user_id: ID del usuario (para verificación)
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if voice_id not in self.voice_metadata:
            return False
        
        # Verificar que el usuario es el propietario
        if user_id and self.voice_metadata[voice_id].get("user_id") != user_id:
            logger.warning(f"Intento de actualizar voz {voice_id} por usuario no autorizado {user_id}")
            return False
        
        try:
            # Campos que no se pueden actualizar
            protected_fields = ["voice_id", "user_id", "sample_path", "created_at"]
            
            # Actualizar metadatos
            for key, value in updates.items():
                if key not in protected_fields:
                    self.voice_metadata[voice_id][key] = value
            
            # Guardar metadatos
            self._save_metadata()
            
            # Actualizar archivo de metadatos local
            sample_path = self.voice_metadata[voice_id].get("sample_path")
            if sample_path:
                voice_dir = os.path.dirname(sample_path)
                metadata_path = os.path.join(voice_dir, "metadata.json")
                
                with open(metadata_path, "w") as f:
                    json.dump(self.voice_metadata[voice_id], f, indent=2)
            
            logger.info(f"Metadatos de voz actualizados: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar metadatos de voz {voice_id}: {e}")
            return False
    
    def get_voice_sample_path(self, voice_id: str) -> Optional[str]:
        """
        Obtiene la ruta al archivo de muestra de una voz.
        
        Args:
            voice_id: ID de la voz
            
        Returns:
            Ruta al archivo de muestra, o None si no existe
        """
        if voice_id not in self.voice_metadata:
            return None
        
        sample_path = self.voice_metadata[voice_id].get("sample_path")
        
        if sample_path and os.path.exists(sample_path):
            return sample_path
        
        return None
    
    def import_voice_sample(self, file_path: str, temp_id: str = None) -> Dict[str, Any]:
        """
        Importa una muestra de voz al directorio temporal para su procesamiento.
        
        Args:
            file_path: Ruta al archivo de audio
            temp_id: ID temporal (opcional)
            
        Returns:
            Diccionario con información de la importación
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return {"success": False, "error": "Archivo no encontrado"}
            
            # Verificar formato
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_formats:
                return {
                    "success": False, 
                    "error": f"Formato no soportado. Formatos válidos: {', '.join(self.supported_formats)}"
                }
            
            # Generar ID temporal si no se proporciona
            if not temp_id:
                temp_id = f"temp_{uuid.uuid4().hex[:8]}"
            
            # Crear directorio temporal
            temp_dir = os.path.join(self.temp_dir, temp_id)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Copiar archivo
            temp_path = os.path.join(temp_dir, f"sample{file_ext}")
            shutil.copy2(file_path, temp_path)
            
            # Analizar audio
            try:
                info = sf.info(temp_path)
                duration = info.duration
                sample_rate = info.samplerate
                channels = info.channels
            except Exception as e:
                return {"success": False, "error": f"Error al analizar audio: {e}"}
            
            return {
                "success": True,
                "temp_id": temp_id,
                "temp_path": temp_path,
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "original_filename": os.path.basename(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error al importar muestra de voz: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_temp_files(self, temp_id: str = None, older_than: int = 86400) -> int:
        """
        Limpia archivos temporales.
        
        Args:
            temp_id: ID temporal específico a limpiar
            older_than: Eliminar archivos más antiguos que este tiempo (en segundos)
            
        Returns:
            Número de archivos eliminados
        """
        count = 0
        
        try:
            if temp_id:
                # Eliminar directorio temporal específico
                temp_dir = os.path.join(self.temp_dir, temp_id)
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    count = 1
            else:
                # Eliminar directorios temporales antiguos
                now = time.time()
                for item in os.listdir(self.temp_dir):
                    item_path = os.path.join(self.temp_dir, item)
                    if os.path.isdir(item_path):
                        # Verificar tiempo de modificación
                        mtime = os.path.getmtime(item_path)
                        if now - mtime > older_than:
                            shutil.rmtree(item_path)
                            count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error al limpiar archivos temporales: {e}")
            return count
