"""
Integración sensorial completa para Vicky
Coordina OÍDO, VISTA y VOZ con el cerebro dual y Kinect
"""

import os
import time
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from .audio_processor import VickyAudioProcessor
from .vision_processor import VickyVisionProcessor
from ..core.brain import VickyBrain

logger = logging.getLogger("vicky.sensors.integration")

@dataclass
class SensoryState:
    """Estado sensorial actual de Vicky"""
    is_listening: bool = False
    is_watching: bool = False
    is_activated: bool = False
    person_present: bool = False
    last_interaction: float = 0
    faces_detected: int = 0
    audio_level: float = 0.0
    current_mood: str = "neutral"

class VickySensoryIntegration:
    """
    Integración sensorial completa para Vicky.
    
    Coordina todas las capacidades sensoriales:
    - 👂 OÍDO: Reconocimiento de voz y activación
    - 👀 VISTA: Detección de caras, gestos y presencia
    - 🎵 VOZ: Síntesis de voz con contexto emocional
    - 🤖 KINECT: Control de movimiento y orientación
    """
    
    def __init__(self, kinect_integration=None):
        # Componentes principales
        self.kinect = kinect_integration
        self.brain = VickyBrain()
        self.audio_processor = VickyAudioProcessor(kinect_integration)
        self.vision_processor = VickyVisionProcessor(kinect_integration)
        
        # Estado sensorial
        self.state = SensoryState()
        self.interaction_history = []
        
        # Configuración
        self.auto_orient_to_person = True
        self.conversation_timeout = 60  # 60 segundos sin interacción
        self.emotional_response_enabled = True
        
        # Callbacks externos
        self.on_interaction = None
        self.on_state_change = None
        
        # Configurar callbacks internos
        self._setup_callbacks()
        
        logger.info("🎭 VickySensoryIntegration inicializado")
    
    def _setup_callbacks(self):
        """Configura los callbacks entre componentes"""
        # Callbacks de audio
        self.audio_processor.set_activation_callback(self._on_voice_activation)
        self.audio_processor.set_speech_callback(self._on_speech_detected)
        
        # Callbacks de visión
        self.vision_processor.set_face_callback(self._on_face_detected)
        self.vision_processor.set_gesture_callback(self._on_gesture_detected)
        self.vision_processor.set_presence_callback(self._on_presence_changed)
        self.vision_processor.set_expression_callback(self._on_expression_detected)
    
    async def start_all_sensors(self):
        """Inicia todos los sensores"""
        logger.info("🚀 Iniciando todos los sensores de Vicky...")
        
        # Iniciar procesamiento de audio
        self.audio_processor.start_listening()
        self.state.is_listening = True
        
        # Iniciar procesamiento de visión
        self.vision_processor.start_processing()
        self.state.is_watching = True
        
        # Inicializar estado
        self.state.last_interaction = time.time()
        
        logger.info("✅ Todos los sensores iniciados")
        
        # Mensaje de bienvenida
        await self._speak_welcome_message()
    
    def stop_all_sensors(self):
        """Detiene todos los sensores"""
        logger.info("🛑 Deteniendo todos los sensores...")
        
        self.audio_processor.stop_listening()
        self.vision_processor.stop_processing()
        
        self.state.is_listening = False
        self.state.is_watching = False
        self.state.is_activated = False
        
        logger.info("✅ Todos los sensores detenidos")
    
    async def _speak_welcome_message(self):
        """Reproduce mensaje de bienvenida"""
        try:
            welcome_text = "Hola, soy Vicky. Mis sentidos están activos y estoy lista para ayudarte. Solo di 'Hey Vicky' para activarme."
            
            result = await self.brain.synthesize_speech(
                text=welcome_text,
                language="es",
                emotion="friendly"
            )
            
            if result["success"]:
                logger.info("🎵 Mensaje de bienvenida reproducido")
                # En un sistema real, aquí reproduciríamos el audio en los altavoces
                await self._play_audio(result["audio_path"])
            
        except Exception as e:
            logger.error(f"Error reproduciendo mensaje de bienvenida: {e}")
    
    async def _play_audio(self, audio_path: str):
        """Reproduce audio en los altavoces (simulado)"""
        try:
            # En un sistema real, aquí usaríamos pygame, sounddevice o similar
            logger.info(f"🔊 Reproduciendo audio: {os.path.basename(audio_path)}")
            # Simular duración de reproducción
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}")
    
    # ===== CALLBACKS DE AUDIO =====
    
    def _on_voice_activation(self, timestamp: float):
        """Callback cuando se detecta activación por voz"""
        logger.info("🔥 Vicky activada por voz")
        
        self.state.is_activated = True
        self.state.last_interaction = timestamp
        
        # Orientar hacia la fuente de sonido si hay una cara detectada
        if self.state.faces_detected > 0 and self.auto_orient_to_person:
            self._orient_to_main_face()
        
        # Notificar cambio de estado
        self._notify_state_change("voice_activation", timestamp)
    
    def _on_speech_detected(self, text: str, timestamp: float):
        """Callback cuando se detecta habla"""
        logger.info(f"👂 Habla detectada: '{text}'")
        
        self.state.last_interaction = timestamp
        
        # Procesar con el cerebro de Vicky
        asyncio.create_task(self._process_speech_input(text, timestamp))
    
    async def _process_speech_input(self, text: str, timestamp: float):
        """Procesa entrada de voz con el cerebro de Vicky"""
        try:
            # Crear contexto con información sensorial
            context = {
                "timestamp": timestamp,
                "person_present": self.state.person_present,
                "faces_detected": self.state.faces_detected,
                "mood": self.state.current_mood,
                "interaction_mode": "voice"
            }
            
            # Procesar con el cerebro dual
            brain_response = self.brain.process_message(text, context)
            
            # Determinar emoción de respuesta basada en el contexto
            emotion = self._determine_response_emotion(brain_response, context)
            
            # Sintetizar respuesta
            tts_result = await self.brain.synthesize_speech(
                text=brain_response.get("response", "No pude procesar tu mensaje"),
                language="es",
                emotion=emotion
            )
            
            if tts_result["success"]:
                # Reproducir respuesta
                await self._play_audio(tts_result["audio_path"])
                
                # Registrar interacción
                self._log_interaction({
                    "type": "voice_conversation",
                    "input": text,
                    "output": brain_response.get("response"),
                    "emotion": emotion,
                    "timestamp": timestamp,
                    "processing_time": brain_response.get("metadata", {}).get("processingTime", 0)
                })
            
            # Notificar interacción
            if self.on_interaction:
                self.on_interaction("voice", text, brain_response.get("response"), timestamp)
            
        except Exception as e:
            logger.error(f"Error procesando entrada de voz: {e}")
    
    # ===== CALLBACKS DE VISIÓN =====
    
    def _on_face_detected(self, faces: List[Dict], timestamp: float):
        """Callback cuando se detectan caras"""
        face_count = len(faces)
        logger.info(f"👤 {face_count} cara(s) detectada(s)")
        
        self.state.faces_detected = face_count
        self.state.last_interaction = timestamp
        
        # Orientar hacia la cara principal si está habilitado
        if faces and self.auto_orient_to_person:
            main_face = max(faces, key=lambda f: f["width"] * f["height"])  # Cara más grande
            self.vision_processor.look_at_person(main_face["center"])
        
        # Saludo automático si es una cara nueva y no hay conversación activa
        if face_count > 0 and not self.state.is_activated:
            asyncio.create_task(self._greet_person())
    
    def _on_gesture_detected(self, gestures: List[Dict], timestamp: float):
        """Callback cuando se detectan gestos"""
        for gesture in gestures:
            logger.info(f"👋 Gesto detectado: {gesture['type']}")
            
            # Responder a gestos específicos
            if gesture["type"] in ["looking_left", "looking_right"]:
                asyncio.create_task(self._respond_to_looking_gesture(gesture))
    
    def _on_presence_changed(self, person_present: bool, timestamp: float):
        """Callback cuando cambia la presencia de persona"""
        self.state.person_present = person_present
        self.state.last_interaction = timestamp
        
        if person_present:
            logger.info("🧑 Persona detectada en el área")
            asyncio.create_task(self._on_person_enters())
        else:
            logger.info("👻 Persona salió del área")
            asyncio.create_task(self._on_person_leaves())
    
    def _on_expression_detected(self, expressions: List[Dict], timestamp: float):
        """Callback cuando se detectan expresiones"""
        for expression in expressions:
            logger.info(f"😊 Expresión detectada: {expression['type']}")
            
            # Ajustar mood basado en expresiones
            if expression["type"] == "smile":
                self.state.current_mood = "happy"
            elif expression["type"] == "calm":
                self.state.current_mood = "peaceful"
            elif expression["type"] == "animated":
                self.state.current_mood = "excited"
    
    # ===== RESPUESTAS AUTOMÁTICAS =====
    
    async def _greet_person(self):
        """Saluda automáticamente a una persona detectada"""
        try:
            greetings = [
                "Hola, te he visto llegar. Si necesitas algo, solo di 'Hey Vicky'.",
                "¡Qué bueno verte! Estoy aquí si me necesitas.",
                "Hola, soy Vicky. Di 'Hey Vicky' si quieres hablar conmigo."
            ]
            
            greeting = greetings[int(time.time()) % len(greetings)]
            
            result = await self.brain.synthesize_speech(
                text=greeting,
                language="es",
                emotion="friendly"
            )
            
            if result["success"]:
                await self._play_audio(result["audio_path"])
            
        except Exception as e:
            logger.error(f"Error saludando: {e}")
    
    async def _respond_to_looking_gesture(self, gesture: Dict):
        """Responde a gestos de mirada"""
        try:
            if gesture["type"] == "looking_left":
                response = "Veo que miras hacia la izquierda. ¿Hay algo interesante por allí?"
            elif gesture["type"] == "looking_right":
                response = "Noté que miras hacia la derecha. ¿Te puedo ayudar con algo?"
            else:
                return
            
            # Solo responder si estamos activados
            if self.state.is_activated:
                result = await self.brain.synthesize_speech(
                    text=response,
                    language="es",
                    emotion="curious"
                )
                
                if result["success"]:
                    await self._play_audio(result["audio_path"])
            
        except Exception as e:
            logger.error(f"Error respondiendo a gesto: {e}")
    
    async def _on_person_enters(self):
        """Acciones cuando una persona entra al área"""
        if not self.state.is_activated:
            await asyncio.sleep(2)  # Esperar un poco
            await self._greet_person()
    
    async def _on_person_leaves(self):
        """Acciones cuando una persona sale del área"""
        if self.state.is_activated:
            farewell = "¡Hasta luego! Aquí estaré si regresas."
            
            result = await self.brain.synthesize_speech(
                text=farewell,
                language="es",
                emotion="friendly"
            )
            
            if result["success"]:
                await self._play_audio(result["audio_path"])
            
            # Desactivar después de despedirse
            self.state.is_activated = False
    
    # ===== UTILIDADES =====
    
    def _orient_to_main_face(self):
        """Orienta el Kinect hacia la cara principal detectada"""
        if self.vision_processor.current_faces:
            main_face = max(
                self.vision_processor.current_faces, 
                key=lambda f: f["width"] * f["height"]
            )
            self.vision_processor.look_at_person(main_face["center"])
    
    def _determine_response_emotion(self, brain_response: Dict, context: Dict) -> str:
        """Determina la emoción apropiada para la respuesta"""
        if not self.emotional_response_enabled:
            return "neutral"
        
        # Basado en el balance hemisférico
        hemisphere = brain_response.get("metadata", {}).get("hemisphere", {})
        technical_weight = hemisphere.get("technical", 0.5)
        emotional_weight = hemisphere.get("emotional", 0.5)
        
        # Basado en el mood actual
        mood = context.get("mood", "neutral")
        
        if technical_weight > 0.7:
            return "professional"
        elif emotional_weight > 0.7:
            if mood == "happy":
                return "cheerful"
            elif mood == "excited":
                return "enthusiastic"
            else:
                return "warm"
        else:
            return "neutral"
    
    def _log_interaction(self, interaction: Dict):
        """Registra una interacción"""
        self.interaction_history.append(interaction)
        
        # Mantener solo las últimas 100 interacciones
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
    
    def _notify_state_change(self, change_type: str, timestamp: float):
        """Notifica cambios de estado"""
        if self.on_state_change:
            self.on_state_change(change_type, self.state, timestamp)
    
    # ===== API PÚBLICA =====
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema sensorial"""
        return {
            "sensory_state": {
                "is_listening": self.state.is_listening,
                "is_watching": self.state.is_watching,
                "is_activated": self.state.is_activated,
                "person_present": self.state.person_present,
                "faces_detected": self.state.faces_detected,
                "current_mood": self.state.current_mood,
                "last_interaction": self.state.last_interaction
            },
            "audio_status": self.audio_processor.get_status(),
            "vision_status": self.vision_processor.get_status(),
            "brain_status": {
                "hemisphere_balance": self.brain.current_balance,
                "total_requests": getattr(self.brain.dual_brain, 'stats', {}).get('total_requests', 0)
            },
            "kinect_status": self.kinect.get_status() if self.kinect else {"connected": False},
            "interaction_history_count": len(self.interaction_history),
            "configuration": {
                "auto_orient_to_person": self.auto_orient_to_person,
                "conversation_timeout": self.conversation_timeout,
                "emotional_response_enabled": self.emotional_response_enabled
            }
        }
    
    def set_interaction_callback(self, callback: Callable[[str, str, str, float], None]):
        """Establece callback para interacciones"""
        self.on_interaction = callback
    
    def set_state_change_callback(self, callback: Callable[[str, SensoryState, float], None]):
        """Establece callback para cambios de estado"""
        self.on_state_change = callback 