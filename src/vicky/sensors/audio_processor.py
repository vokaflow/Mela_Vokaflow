"""
Procesador de audio para Vicky - OÍDO
Capacidades de reconocimiento de voz, detección de activación y procesamiento de audio
"""

import os
import time
import logging
import threading
import queue
import numpy as np
from typing import Dict, Any, Optional, Callable, List
import asyncio

logger = logging.getLogger("vicky.sensors.audio")

class VickyAudioProcessor:
    """
    Procesador de audio para Vicky con capacidades de:
    - Reconocimiento de voz (Speech-to-Text)
    - Detección de palabra de activación ("Hey Vicky")
    - Procesamiento de audio desde Kinect
    - Filtrado de ruido y mejora de audio
    """
    
    def __init__(self, kinect_integration=None):
        self.kinect = kinect_integration
        self.is_listening = False
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.activation_queue = queue.Queue()
        
        # Configuración de audio
        self.sample_rate = 16000  # 16kHz para Whisper
        self.chunk_size = 1024
        self.channels = 1
        
        # Callbacks
        self.on_activation_detected = None
        self.on_speech_detected = None
        self.on_audio_processed = None
        
        # Estado de activación
        self.activation_phrases = ["hey vicky", "vicky", "oye vicky", "hola vicky"]
        self.is_activated = False
        self.activation_timeout = 30  # 30 segundos de timeout
        self.last_activation = 0
        
        # Mock de Whisper (en producción sería el modelo real)
        self.whisper_model = MockWhisperModel()
        
        logger.info("VickyAudioProcessor inicializado")
    
    def start_listening(self):
        """Inicia la escucha continua de audio"""
        if self.is_listening:
            logger.warning("Ya se está escuchando audio")
            return
            
        self.is_listening = True
        logger.info("🎧 Iniciando escucha de audio...")
        
        # Iniciar hilos de procesamiento
        self.listening_thread = threading.Thread(target=self._audio_listening_loop, daemon=True)
        self.processing_thread = threading.Thread(target=self._audio_processing_loop, daemon=True)
        
        self.listening_thread.start()
        self.processing_thread.start()
        
        logger.info("✅ Escucha de audio iniciada")
    
    def stop_listening(self):
        """Detiene la escucha de audio"""
        self.is_listening = False
        logger.info("🔇 Deteniendo escucha de audio...")
    
    def _audio_listening_loop(self):
        """Loop principal de captura de audio"""
        while self.is_listening:
            try:
                # Simular captura de audio del Kinect
                if self.kinect and self.kinect.connected:
                    # En un sistema real, capturaríamos audio del Kinect
                    audio_data = self._capture_kinect_audio()
                else:
                    # Simular datos de audio
                    audio_data = self._simulate_audio_capture()
                
                if audio_data is not None:
                    self.audio_queue.put({
                        "data": audio_data,
                        "timestamp": time.time(),
                        "source": "kinect" if self.kinect and self.kinect.connected else "simulated"
                    })
                
                time.sleep(0.1)  # 100ms de intervalo
                
            except Exception as e:
                logger.error(f"Error en captura de audio: {e}")
                time.sleep(1)
    
    def _audio_processing_loop(self):
        """Loop principal de procesamiento de audio"""
        while self.is_listening:
            try:
                # Obtener datos de audio de la cola
                if not self.audio_queue.empty():
                    audio_item = self.audio_queue.get()
                    self._process_audio_chunk(audio_item)
                else:
                    time.sleep(0.05)  # 50ms si no hay datos
                    
            except Exception as e:
                logger.error(f"Error en procesamiento de audio: {e}")
                time.sleep(1)
    
    def _process_audio_chunk(self, audio_item: Dict[str, Any]):
        """Procesa un chunk de audio"""
        audio_data = audio_item["data"]
        timestamp = audio_item["timestamp"]
        
        # 1. Detectar activación si no estamos activados
        if not self.is_activated:
            activation_detected = self._detect_activation_phrase(audio_data)
            if activation_detected:
                self._handle_activation(timestamp)
                return
        
        # 2. Si estamos activados, procesar speech-to-text
        elif self._is_activation_valid(timestamp):
            text = self._speech_to_text(audio_data)
            if text and text.strip():
                self._handle_speech_detected(text, timestamp)
        
        # 3. Verificar timeout de activación
        else:
            self._deactivate()
    
    def _capture_kinect_audio(self) -> Optional[np.ndarray]:
        """Captura audio del Kinect"""
        if not self.kinect or not self.kinect.connected:
            return None
            
        try:
            # En un sistema real, aquí capturaríamos audio del Kinect
            # Por ahora simulamos
            return np.random.normal(0, 0.1, self.chunk_size).astype(np.float32)
        except Exception as e:
            logger.error(f"Error capturando audio del Kinect: {e}")
            return None
    
    def _simulate_audio_capture(self) -> np.ndarray:
        """Simula captura de audio para desarrollo"""
        # Simular audio con algunas palabras de activación ocasionales
        if np.random.random() < 0.001:  # 0.1% probabilidad de activación
            # Simular "Hey Vicky"
            return np.random.normal(0, 0.5, self.chunk_size).astype(np.float32)
        else:
            # Ruido de fondo normal
            return np.random.normal(0, 0.1, self.chunk_size).astype(np.float32)
    
    def _detect_activation_phrase(self, audio_data: np.ndarray) -> bool:
        """Detecta frases de activación en el audio"""
        try:
            # Simular detección de activación
            # En un sistema real usaríamos un modelo de detección de wake words
            energy = np.mean(np.abs(audio_data))
            
            # Si hay suficiente energía, podría ser una palabra de activación
            if energy > 0.3:  # Umbral de energía
                # Simular transcripción rápida para detección
                quick_text = self.whisper_model.quick_transcribe(audio_data)
                if quick_text:
                    for phrase in self.activation_phrases:
                        if phrase.lower() in quick_text.lower():
                            logger.info(f"🎯 Frase de activación detectada: '{phrase}' en '{quick_text}'")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detectando activación: {e}")
            return False
    
    def _speech_to_text(self, audio_data: np.ndarray) -> Optional[str]:
        """Convierte audio a texto usando Whisper"""
        try:
            # Usar modelo Whisper para transcripción
            text = self.whisper_model.transcribe(audio_data)
            return text
            
        except Exception as e:
            logger.error(f"Error en speech-to-text: {e}")
            return None
    
    def _handle_activation(self, timestamp: float):
        """Maneja la detección de activación"""
        self.is_activated = True
        self.last_activation = timestamp
        
        logger.info("🔥 ¡Vicky activada! Escuchando comando...")
        
        # Callback de activación
        if self.on_activation_detected:
            self.on_activation_detected(timestamp)
    
    def _handle_speech_detected(self, text: str, timestamp: float):
        """Maneja la detección de habla"""
        logger.info(f"👂 Texto detectado: '{text}'")
        
        # Callback de habla detectada
        if self.on_speech_detected:
            self.on_speech_detected(text, timestamp)
        
        # Resetear activación después de procesar
        self._deactivate()
    
    def _is_activation_valid(self, timestamp: float) -> bool:
        """Verifica si la activación sigue siendo válida"""
        return (timestamp - self.last_activation) <= self.activation_timeout
    
    def _deactivate(self):
        """Desactiva el estado de escucha activa"""
        if self.is_activated:
            self.is_activated = False
            logger.info("💤 Vicky desactivada, volviendo a modo pasivo")
    
    def set_activation_callback(self, callback: Callable[[float], None]):
        """Establece callback para cuando se detecta activación"""
        self.on_activation_detected = callback
    
    def set_speech_callback(self, callback: Callable[[str, float], None]):
        """Establece callback para cuando se detecta habla"""
        self.on_speech_detected = callback
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del procesador de audio"""
        return {
            "is_listening": self.is_listening,
            "is_activated": self.is_activated,
            "last_activation": self.last_activation,
            "queue_size": self.audio_queue.qsize(),
            "kinect_connected": self.kinect.connected if self.kinect else False,
            "activation_phrases": self.activation_phrases
        }


class MockWhisperModel:
    """Modelo Whisper simulado para desarrollo"""
    
    def __init__(self):
        self.model_name = "whisper-medium"
        self.supported_languages = ["es", "en", "fr", "de", "it"]
        
    def quick_transcribe(self, audio_data: np.ndarray) -> str:
        """Transcripción rápida para detección de activación"""
        # Simular detección de wake words
        energy = np.mean(np.abs(audio_data))
        
        if energy > 0.4:
            return "hey vicky"
        elif energy > 0.3:
            return "vicky"
        else:
            return ""
    
    def transcribe(self, audio_data: np.ndarray, language: str = "es") -> str:
        """Transcripción completa del audio"""
        # Simular transcripción real
        energy = np.mean(np.abs(audio_data))
        
        if energy > 0.3:
            # Simular diferentes frases basadas en la energía del audio
            phrases = [
                "¿Cómo estás Vicky?",
                "¿Qué hora es?",
                "Cuéntame sobre el clima",
                "Ayúdame con programación",
                "¿Puedes traducir esto?",
                "Necesito ayuda con mi proyecto"
            ]
            return phrases[int(energy * 10) % len(phrases)]
        else:
            return "" 