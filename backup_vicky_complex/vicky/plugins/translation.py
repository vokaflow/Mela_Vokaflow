"""
Plugin de traducción para Vicky
"""
import logging
from typing import Dict, Any, Optional, List
import re

from .base import Plugin

logger = logging.getLogger("vicky.plugins.translation")

class TranslationPlugin(Plugin):
    """
    Plugin para traducción de mensajes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa el plugin de traducción.
        
        Args:
            config: Configuración del plugin
        """
        super().__init__("translation", config)
        
        # Configuración por defecto
        self.default_target_language = self.config.get("default_target_language", "es")
        self.cache_translations = self.config.get("cache_translations", True)
        
        # Caché de traducciones
        self.translation_cache = {}
        
        # Patrones para detectar comandos de traducción
        self.translation_patterns = [
            r"^traduce(?:\s+esto)?\s*:\s*(.+)$",
            r"^traducir(?:\s+esto)?\s*:\s*(.+)$",
            r"^translate(?:\s+this)?\s*:\s*(.+)$",
            r"^traducir\s+[\"'](.+)[\"']\s+(?:al?|to)\s+([a-z]{2})$",
            r"^translate\s+[\"'](.+)[\"']\s+(?:al?|to)\s+([a-z]{2})$"
        ]
        
        logger.info("Plugin de traducción inicializado")
    
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
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Procesa un mensaje para detectar y ejecutar comandos de traducción.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Traducción o None si no es un comando de traducción
        """
        # Verificar si es un comando de traducción
        for pattern in self.translation_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                # Extraer texto a traducir
                text_to_translate = match.group(1).strip()
                
                # Extraer idioma de destino si está especificado
                target_language = self.default_target_language
                if len(match.groups()) > 1 and match.group(2):
                    target_language = match.group(2).strip()
                
                # Detectar idioma de origen
                source_language = self.detect_language(text_to_translate)
                
                # Verificar caché
                cache_key = f"{source_language}:{target_language}:{text_to_translate}"
                if self.cache_translations and cache_key in self.translation_cache:
                    logger.info(f"Usando traducción en caché para: {text_to_translate[:50]}...")
                    return self.translation_cache[cache_key]
                
                # Traducir texto
                logger.info(f"Traduciendo de {source_language} a {target_language}: {text_to_translate[:50]}...")
                
                try:
                    # Obtener el cerebro de Vicky
                    from ..core.brain import VickyBrain
                    brain = VickyBrain()
                    
                    # Traducir texto
                    translated_text = brain.translate(text_to_translate, source_language, target_language)
                    
                    # Guardar en caché
                    if self.cache_translations:
                        self.translation_cache[cache_key] = translated_text
                    
                    return translated_text
                except Exception as e:
                    logger.error(f"Error al traducir texto: {e}")
                    return f"Error al traducir: {str(e)}"
        
        return None
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Obtiene la lista de idiomas soportados.
        
        Returns:
            Lista de idiomas soportados
        """
        # Esta es una lista de ejemplo, en un caso real vendría del modelo
        languages = [
            {"code": "es", "name": "Español"},
            {"code": "en", "name": "Inglés"},
            {"code": "fr", "name": "Francés"},
            {"code": "de", "name": "Alemán"},
            {"code": "it", "name": "Italiano"},
            {"code": "pt", "name": "Portugués"},
            {"code": "ru", "name": "Ruso"},
            {"code": "zh", "name": "Chino"},
            {"code": "ja", "name": "Japonés"},
            {"code": "ko", "name": "Coreano"}
        ]
        
        return languages
