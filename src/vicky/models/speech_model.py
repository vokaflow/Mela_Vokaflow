"""
Módulo para interactuar con modelos de reconocimiento de voz
"""
import os
import logging
import torch
from typing import List, Dict, Any, Optional, Union
import yaml
import numpy as np

logger = logging.getLogger("vicky.models.speech_model")

class SpeechModel:
    """
    Clase para interactuar con modelos de reconocimiento de voz como Whisper
    """
    
    def __init__(self, model_path: str = None, device: str = None):
        """
        Inicializa el modelo de reconocimiento de voz.
        
        Args:
            model_path: Ruta al modelo
            device: Dispositivo para inferencia (cuda, cpu)
        """
        # Cargar configuración
        config_path = os.environ.get("MODELS_CONFIG", "/opt/vokaflow/config/models.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Configurar modelo
        self.model_path = model_path or self.config["speech_recognition"]["models"]["whisper"]["path"]
        self.device = device or self.config["speech_recognition"]["models"]["whisper"]["device"]
        
        self.model = None
        self.processor = None
        
        logger.info(f"Inicializando modelo de reconocimiento de voz desde {self.model_path}")
    
    def load(self):
        """Carga el modelo en memoria."""
        try:
            logger.info(f"Cargando modelo de reconocimiento de voz desde {self.model_path}")
            
            # Importar las bibliotecas necesarias
            from transformers import WhisperForConditionalGeneration, WhisperProcessor
            
            # Cargar modelo y procesador
            self.model = WhisperForConditionalGeneration.from_pretrained(
                self.model_path,
                device_map=self.device
            )
            
            self.processor = WhisperProcessor.from_pretrained(
                self.model_path
            )
            
            logger.info("Modelo de reconocimiento de voz cargado correctamente")
            
            # Mostrar información de memoria si se usa GPU
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"Memoria GPU reservada: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
                logger.info(f"Memoria GPU en uso: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            return True
        except Exception as e:
            logger.error(f"Error al cargar el modelo de reconocimiento de voz: {e}")
            return False
    
    def transcribe(self, audio: Union[str, np.ndarray], language: str = None) -> str:
        """
        Transcribe audio a texto.
        
        Args:
            audio: Ruta al archivo de audio o array de audio
            language: Código de idioma (auto-detectado si es None)
            
        Returns:
            Texto transcrito
        """
        if self.model is None or self.processor is None:
            logger.warning("El modelo no está cargado. Cargando...")
            if not self.load():
                return "Error: No se pudo cargar el modelo de reconocimiento de voz."
        
        try:
            logger.info(f"Transcribiendo audio...")
            
            # Cargar audio si es una ruta
            if isinstance(audio, str):
                import librosa
                audio_array, _ = librosa.load(audio, sr=16000)
            else:
                audio_array = audio
            
            # Procesar audio
            inputs = self.processor(audio_array, sampling_rate=16000, return_tensors="pt").to(self.device)
            
            # Configurar idioma si se especifica
            generate_kwargs = {}
            if language:
                generate_kwargs["language"] = language
            
            # Generar transcripción
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_features"],
                    **generate_kwargs
                )
            
            # Decodificar transcripción
            transcription = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.info(f"Texto transcrito: {transcription[:50]}...")
            return transcription
        except Exception as e:
            logger.error(f"Error al transcribir audio: {e}")
            return f"Error: {str(e)}"
    
    def unload(self):
        """Libera la memoria del modelo."""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.processor is not None:
            del self.processor
            self.processor = None
        
        # Limpiar caché de CUDA si está disponible
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Modelo de reconocimiento de voz descargado de memoria")
