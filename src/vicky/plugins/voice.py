"""
Plugin de voz para Vicky
"""
import logging
import os
from typing import Dict, Any, Optional, Tuple
import re
import tempfile

from .base import Plugin

logger = logging.getLogger("vicky.plugins.voice")

class VoicePlugin(Plugin):
    """
    Plugin para procesamiento de voz.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa el plugin de voz.
        
        Args:
            config: Configuración del plugin
        """
        super().__init__("voice", config)
        
        # Configuración por defecto
        self.activation_word = self.config.get("activation_word", "vicky")
        self.voice_id = self.config.get("voice_id", "es_female_1")
        
        # Patrones para detectar comandos de voz
        self.voice_patterns = [
            r"^(?:di|say|speak|habla)(?:\s+esto)?\s*:\s*(.+)$",
            r"^(?:lee|read)(?:\s+esto)?\s*:\s*(.+)$",
            r"^(?:convierte|convert)(?:\s+esto)?\s+(?:a|to)\s+(?:voz|audio|speech)\s*:\s*(.+)$"
        ]
        
        logger.info("Plugin de voz inicializado")
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Procesa un mensaje para detectar y ejecutar comandos de voz.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Ruta al archivo de audio generado o None si no es un comando de voz
        """
        # Verificar si es un comando de voz
        for pattern in self.voice_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                # Extraer texto a convertir a voz
                text_to_speak = match.group(1).strip()
                
                # Detectar idioma
                language = self.detect_language(text_to_speak)
                
                # Convertir a voz
                logger.info(f"Convirtiendo a voz: {text_to_speak[:50]}...")
                
                try:
                    # Obtener el cerebro de Vicky
                    from ..core.brain import VickyBrain
                    brain = VickyBrain()
                    
                    # Generar archivo temporal para el audio
                    temp_dir = tempfile.gettempdir()
                    output_file = os.path.join(temp_dir, f"vicky_speech_{int(time.time())}.wav")
                    
                    # Sintetizar voz
                    audio_path = brain.synthesize_speech(text_to_speak, language, output_file)
                    
                    return f"Audio generado: {audio_path}"
                except Exception as e:
                    logger.error(f"Error al convertir texto a voz: {e}")
                    return f"Error al generar audio: {str(e)}"
        
        return None
    
    def detect_language(self, text: str) -> str:
        """
        Detecta el idioma de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Código de idioma detectado
        """
        # En un caso real, aquí se usaría un detector de idioma
        # Por ahora, simplemente asumimos inglés si hay más palabras en inglés que en español
        
        # Lista de palabras comunes en inglés
        english_words = {"the", "a", "an", "and", "or", "but", "if", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can", "will", "just", "should", "now"}
        
        # Lista de palabras comunes en español
        spanish_words = {"el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero", "si", "de", "a", "en", "por", "para", "con", "sobre", "entre", "contra", "durante", "antes", "después", "arriba", "abajo", "hacia", "desde", "hasta", "dentro", "fuera", "encima", "debajo", "otra", "vez", "entonces", "una", "vez", "aquí", "allí", "cuando", "donde", "por", "qué", "cómo", "todo", "alguno", "alguna", "ambos", "cada", "pocos", "más", "mayoría", "otro", "algunos", "tal", "no", "ni", "tampoco", "sólo", "propio", "mismo", "así", "que", "tan", "demasiado", "muy", "puede", "podrá", "sólo", "debería", "ahora"}
        
        # Contar palabras en inglés y español
        words = text.lower().split()
        english_count = sum(1 for word in words if word in english_words)
        spanish_count = sum(1 for word in words if word in spanish_words)
        
        # Determinar idioma
        if english_count > spanish_count:
            return "en"
        else:
            return "es"
    
    def transcribe_audio(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe un archivo de audio a texto.
        
        Args:
            audio_path: Ruta al archivo de audio
            
        Returns:
            Tupla con el texto transcrito y el idioma detectado
        """
        try:
            # Obtener el cerebro de Vicky
            from ..core.brain import VickyBrain
            brain = VickyBrain()
            
            # Transcribir audio
            transcription = brain.transcribe_audio(audio_path)
            
            # Detectar idioma
            language = self.detect_language(transcription)
            
            return transcription, language
        except Exception as e:
            logger.error(f"Error al transcribir audio: {e}")
            return f"Error al transcribir audio: {str(e)}", "es"
