"""
Núcleo central de Vicky, la IA de VokaFlow.

Este módulo implementa la lógica principal del cerebro de Vicky,
incluyendo la gestión de modelos, el procesamiento del lenguaje natural
y la coordinación de los hemisferios técnico y emocional.
"""

import logging
from typing import Dict, Any, Optional
import traceback
import time

# Importaciones internas
from .model_manager import ModelManager
from .personality_manager import PersonalityManager
from .context import Context
from .memory import Memory
from .state import State
from .dual_brain import DualBrain

# Configurar logger
logger = logging.getLogger("vicky.core.brain")

class VickyBrain:
    """
    Núcleo central de Vicky, la IA de VokaFlow.
    
    Coordina los diferentes componentes del sistema para procesar
    consultas del usuario y generar respuestas coherentes y adaptadas.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el cerebro de Vicky.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Inicializar componentes básicos
        self.model_manager = ModelManager()
        self.context = Context()
        self.memory = Memory()
        self.state = State()
        self.personality_manager = PersonalityManager()
        
        # Inicializar plugins (vacío por ahora)
        self.plugins = {}
        
        # Registrar tiempo de inicio
        self.state.set("start_time", time.time())
        
        # Inicializar cerebro dual como motor principal de procesamiento
        self.dual_brain = DualBrain()
        
        # Inicializar generador de respuestas
        from .response_generator import ResponseGenerator
        self.response_generator = ResponseGenerator(
            model_manager=self.model_manager,
            personality_manager=self.personality_manager,
            dual_brain=self.dual_brain,
            context=self.context,
            memory=self.memory,
            state=self.state,
            config=self.config.get("response_generator", {})
        )
        
        logger.info("Cerebro de Vicky inicializado")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Carga la configuración del sistema.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
            
        Returns:
            Diccionario con la configuración
        """
        # Implementación de carga de configuración (aún no implementada)
        # En una versión completa, se leería un archivo YAML o JSON
        # y se cargaría la configuración
        
        # Por ahora, devolver configuración por defecto
        return {
            "name": "Vicky",
            "version": "0.1.0",
            "log_level": "INFO",
            "response_generator": {
                "default_response_type": "text",
                "default_content_format": "markdown",
                "enable_voice": True,
                "enable_multimodal": True,
                "max_response_length": 2000,
                "enable_suggestions": True,
                "enable_sources": True,
                "cache_max_size": 100,
                "cache_ttl": 3600,
                "sentiment_analysis": True,
                "contextual_suggestions": True,
                "hemisphere_adaptation": True
            }
        }
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Procesa un mensaje y genera una respuesta.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Respuesta generada
        """
        logger.info(f"Procesando mensaje: {message[:50]}...")
        context = context or {}
        
        # Actualizar contexto con metadatos
        for key, value in context.items():
            self.context.set_metadata(key, value)
        
        # Añadir mensaje al historial de contexto
        self.context.add_message("user", message)
        
        # Usar el generador de respuestas para procesar el mensaje
        try:
            # Generar respuesta utilizando el generador de respuestas
            from .response_generator import ResponseType
            response_obj = self.response_generator.generate_response(
                query=message,
                response_type=ResponseType.TEXT,  # Por defecto, usar texto
                context_data=context,
                user_id=context.get("user_id"),
                conversation_id=context.get("conversation_id")
            )
            
            # Extraer el contenido de texto
            if isinstance(response_obj.content, str):
                response_text = response_obj.content
            else:
                # Si es multimodal, extraer el texto
                text_elements = [e.content for e in response_obj.content if e.element_type == "text"]
                response_text = '\n\n'.join(text_elements) if text_elements else "No se pudo generar una respuesta de texto."
            
            # Añadir respuesta al historial de contexto
            self.context.add_message("assistant", response_text)
            
            # Registrar métricas
            self.state.set("last_processing_time", response_obj.metadata.generation_time)
            self.state.set("total_messages_processed", self.state.get("total_messages_processed", 0) + 1)
            
            logger.info(f"Mensaje procesado en {response_obj.metadata.generation_time:.2f}s")
            return response_text
        except Exception as e:
            logger.error(f"Error al procesar mensaje con generador de respuestas: {e}")
            logger.debug(traceback.format_exc())
            
            # Fallback al método tradicional
            return self._legacy_process_message(message, context)
    
    def _legacy_process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Procesa un mensaje utilizando el método tradicional (con personalidades pero sin Motor Dual-Hemisferio).
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Respuesta generada
        """
        logger.warning("Usando fallback al método tradicional de procesamiento")
        
        try:
            # Obtener información de personalidad actual
            personality = self.personality_manager.get_current_personality()
            response_style = self.personality_manager.get_response_style()
            hemisphere_balance = self.personality_manager.get_hemisphere_balance()
            
            # Generar respuesta básica adaptada a la personalidad
            if personality:
                personality_name = personality.get('nombre', 'Vicky')
                
                # Respuesta básica personalizada
                if "saludo" in message.lower() or "hola" in message.lower():
                    if response_style.get('usar_emojis', False):
                        response = f"¡Hola! 👋 Soy {personality_name}, tu asistente de VokaFlow. ¿En qué puedo ayudarte hoy?"
                    else:
                        response = f"Hola, soy {personality_name}, tu asistente de VokaFlow. ¿En qué puedo ayudarte?"
                
                elif "backend" in message.lower() or "servidor" in message.lower():
                    technical_level = hemisphere_balance.get('technical', 0.6)
                    if technical_level > 0.7:
                        response = f"Como {personality_name}, puedo ayudarte con la gestión y supervisión del backend de VokaFlow. ¿Necesitas revisar algún endpoint específico o analizar el rendimiento del sistema?"
                    else:
                        response = f"¡Por supuesto! Como {personality_name}, estoy aquí para ayudarte con el backend. ¿Qué te gustaría revisar?"
                
                elif "personalidad" in message.lower():
                    available_personalities = self.personality_manager.get_personality_names()
                    current = self.personality_manager.current_personality
                    response = f"Actualmente estoy usando la personalidad '{current}'. Las personalidades disponibles son: {', '.join(available_personalities)}"
                
                elif "ayuda" in message.lower() or "help" in message.lower():
                    capabilities = personality.get('caracteristicas', {}).get('capacidades', {})
                    cap_list = [k for k, v in capabilities.items() if v]
                    response = f"Como {personality_name}, puedo ayudarte con: {', '.join(cap_list)}. ¿Qué necesitas específicamente?"
                
                else:
                    # Respuesta genérica adaptada al estilo
                    if response_style.get('estilo') == 'profesional':
                        response = f"He recibido tu consulta: '{message}'. Como {personality_name}, estoy procesando la información para brindarte la mejor respuesta posible."
                    else:
                        response = f"¡Interesante! 🤔 Como {personality_name}, entiendo que preguntas sobre '{message}'. Déjame procesar esto para ayudarte mejor."
                
                # Aplicar límite de longitud si es necesario
                max_length = response_style.get('longitud_maxima', 1000)
                if len(response) > max_length:
                    response = response[:max_length-3] + "..."
                
                return response
            
            else:
                # Fallback si no hay personalidad
                return "Hola, soy Vicky de VokaFlow. Estoy aquí para ayudarte, aunque aún estoy configurando mi personalidad completa."
                
        except Exception as e:
            logger.error(f"Error en procesamiento legacy: {e}")
            return "Lo siento, tengo dificultades técnicas procesando tu consulta. Por favor, inténtalo de nuevo."
    
    def translate(self, text: str, source_lang: str = None, target_lang: str = "es") -> str:
        """
        Traduce un texto de un idioma a otro.
        
        Args:
            text: Texto a traducir
            source_lang: Idioma de origen (auto-detectado si es None)
            target_lang: Idioma de destino
            
        Returns:
            Texto traducido
        """
        logger.info(f"Traduciendo texto de {source_lang} a {target_lang}")
        
        try:
            # Obtener el modelo de traducción
            translation_model = self.model_manager.get_model("translation")
            
            if translation_model:
                # Traducir texto
                translated_text = translation_model.translate(text, source_lang, target_lang)
                return translated_text
            else:
                error_msg = "No se pudo cargar el modelo de traducción"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"Error al traducir texto: {e}"
            logger.error(error_msg)
            return error_msg
    
    def transcribe_audio(self, audio_path: str, language: str = None) -> str:
        """
        Transcribe un archivo de audio a texto.
        
        Args:
            audio_path: Ruta al archivo de audio
            language: Código de idioma (auto-detectado si es None)
            
        Returns:
            Texto transcrito
        """
        logger.info(f"Transcribiendo audio: {audio_path}")
        
        try:
            # Obtener el modelo de reconocimiento de voz
            speech_model = self.model_manager.get_model("speech")
            
            if speech_model:
                # Transcribir audio
                transcription = speech_model.transcribe(audio_path, language)
                return transcription
            else:
                error_msg = "No se pudo cargar el modelo de reconocimiento de voz"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"Error al transcribir audio: {e}"
            logger.error(error_msg)
            return error_msg
    
    def synthesize_speech(self, text: str, language: str = "es", gender: str = None, 
                         emotion: str = None, output_path: str = None) -> str:
        """
        Sintetiza voz a partir de texto.
        
        Args:
            text: Texto a sintetizar
            language: Código de idioma
            gender: Género de la voz (male/female)
            emotion: Emoción a transmitir (neutral, happy, sad, angry)
            output_path: Ruta de salida para el archivo de audio
            
        Returns:
            Ruta al archivo de audio generado o mensaje de error
        """
        logger.info(f"Sintetizando voz para texto: {text[:50]}...")
        
        try:
            # Obtener el modelo de síntesis de voz
            tts_model = self.model_manager.get_model("tts")
            
            if tts_model:
                # Sintetizar voz
                audio = tts_model.synthesize(
                    text=text, 
                    language=language,
                    gender=gender,
                    emotion=emotion
                )
                
                # Guardar audio si se especifica una ruta
                if output_path:
                    if tts_model.save_audio(audio, output_path):
                        return output_path
                    else:
                        return "Error al guardar el audio"
                
                # Si no se especifica ruta, generar una temporal
                import tempfile
                import os
                
                temp_dir = tempfile.gettempdir()
                output_file = os.path.join(temp_dir, f"vicky_speech_{int(time.time())}.wav")
                
                if tts_model.save_audio(audio, output_file):
                    return output_file
                else:
                    return "Error al guardar el audio"
            else:
                error_msg = "No se pudo cargar el modelo de síntesis de voz"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            error_msg = f"Error al sintetizar voz: {e}"
            logger.error(error_msg)
            return error_msg
    
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
            output_path: Ruta donde guardar el archivo de audio
            
        Returns:
            Diccionario con información del proceso y resultados
        """
        logger.info(f"Iniciando proceso de traducción y síntesis para: {text[:50]}...")
        
        try:
            result = self.multimodal_service.translate_and_speak(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                gender=gender,
                emotion=emotion,
                output_path=output_path
            )
            
            return result
        except Exception as e:
            error_msg = f"Error en el proceso de traducción y síntesis: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
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
        logger.info(f"Iniciando proceso de transcripción, traducción y síntesis para: {audio_path}")
        
        try:
            result = self.multimodal_service.transcribe_translate_speak(
                audio_path=audio_path,
                source_lang=source_lang,
                target_lang=target_lang,
                gender=gender,
                emotion=emotion,
                output_path=output_path
            )
            
            return result
        except Exception as e:
            error_msg = f"Error en el proceso de transcripción, traducción y síntesis: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema.
        
        Returns:
            Diccionario con información del estado del sistema
        """
        try:
            # Obtener estadísticas del cerebro dual
            dual_brain_stats = self.dual_brain.get_processing_stats()
            
            # Obtener modelos cargados
            loaded_models = {}
            for model_type in ["language", "translation", "speech", "tts", "embedding"]:
                model = self.model_manager.get_model(model_type)
                loaded_models[model_type] = model.__class__.__name__ if model else None
            
            # Obtener configuraciones activas de personalidad
            active_configs = {}
            if hasattr(self.personality_manager, 'get_active_configurations'):
                active_configs = self.personality_manager.get_active_configurations()
            
            # Construir estado del sistema
            system_status = {
                "status": "online",
                "uptime": time.time() - self.state.get("start_time", time.time()),
                "total_messages_processed": self.state.get("total_messages_processed", 0),
                "last_processing_time": self.state.get("last_processing_time", 0),
                "loaded_models": loaded_models,
                "active_personality": active_configs,
                "plugins_enabled": [name for name, plugin in self.plugins.items() if plugin.get("enabled", False)],
                "dual_brain_stats": dual_brain_stats,
                "memory_usage": {
                    "context_size": self.context.get_size() if hasattr(self.context, 'get_size') else -1,
                    "memory_entries": len(self.memory.get_all_keys()) if hasattr(self.memory, 'get_all_keys') else -1
                },
                "hemisphere_balance": {
                    "technical": self.dual_brain.default_weights.get("technical", 0.5),
                    "emotional": self.dual_brain.default_weights.get("emotional", 0.5)
                },
                "combination_strategy": self.dual_brain.default_combination_strategy
            }
            
            return system_status
        except Exception as e:
            logger.error(f"Error al obtener estado del sistema: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def set_hemisphere_balance(self, technical_weight: float, emotional_weight: float) -> bool:
        """
        Establece el balance entre hemisferios técnico y emocional.
        
        Args:
            technical_weight: Peso para el hemisferio técnico (0.0-1.0)
            emotional_weight: Peso para el hemisferio emocional (0.0-1.0)
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            weights = {
                "technical": max(0.0, min(1.0, technical_weight)),
                "emotional": max(0.0, min(1.0, emotional_weight))
            }
            
            result = self.dual_brain.set_hemisphere_weights(weights)
            
            if result:
                # Actualizar configuración
                if "dual_brain" not in self.config:
                    self.config["dual_brain"] = {}
                
                self.config["dual_brain"]["technical_weight"] = weights["technical"]
                self.config["dual_brain"]["emotional_weight"] = weights["emotional"]
                
                logger.info(f"Balance de hemisferios actualizado: técnico={weights['technical']}, "
                           f"emocional={weights['emotional']}")
            
            return result
        except Exception as e:
            logger.error(f"Error al establecer balance de hemisferios: {e}")
            return False
    
    def set_combination_strategy(self, strategy: str) -> bool:
        """
        Establece la estrategia de combinación de respuestas.
        
        Args:
            strategy: Nombre de la estrategia
            
        Returns:
            True si se estableció correctamente, False en caso contrario
        """
        try:
            result = self.dual_brain.set_combination_strategy(strategy)
            
            if result:
                # Actualizar configuración
                if "dual_brain" not in self.config:
                    self.config["dual_brain"] = {}
                
                self.config["dual_brain"]["combination_strategy"] = strategy
                
                logger.info(f"Estrategia de combinación actualizada: {strategy}")
            
            return result
        except Exception as e:
            logger.error(f"Error al establecer estrategia de combinación: {e}")
            return False
