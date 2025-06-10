#!/usr/bin/env python3
"""
Servicio de Detección de Idioma para VokaFlow Enterprise
Proporciona detección de idioma básica y avanzada con múltiples algoritmos
"""

import logging
import re
from typing import Tuple, Dict, List, Optional
import time

logger = logging.getLogger("vokaflow.language_detection")

class LanguageDetectionService:
    """Servicio de detección de idioma con múltiples algoritmos"""
    
    def __init__(self):
        """Inicializar el servicio de detección de idioma"""
        self.supported_languages = {
            "es": {
                "name": "Español",
                "patterns": ["ñáéíóúü", "que", "el", "la", "de", "en", "un", "es", "se", "no", "te", "lo", "le"],
                "char_patterns": "ñáéíóúü"
            },
            "en": {
                "name": "English", 
                "patterns": ["the", "and", "to", "of", "a", "in", "that", "have", "it", "for", "not", "on", "with"],
                "char_patterns": ""
            },
            "fr": {
                "name": "Français",
                "patterns": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir", "que", "pour"],
                "char_patterns": "çàâéèêëîïôùûüÿ"
            },
            "de": {
                "name": "Deutsch",
                "patterns": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich", "des", "auf"],
                "char_patterns": "äöüß"
            },
            "it": {
                "name": "Italiano",
                "patterns": ["il", "di", "che", "la", "un", "e", "per", "in", "con", "del", "da", "non"],
                "char_patterns": "àèéìíîòóù"
            },
            "pt": {
                "name": "Português",
                "patterns": ["de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "é", "com"],
                "char_patterns": "ãçáàâéêíóôõú"
            },
            "ru": {
                "name": "Русский",
                "patterns": ["и", "в", "не", "на", "я", "быть", "тот", "он", "весь", "а", "по", "это"],
                "char_patterns": "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
            }
        }
        
        # Estadísticas de uso
        self.detection_stats = {
            "total_detections": 0,
            "language_counts": {},
            "confidence_average": 0.0
        }
        
        logger.info("✅ Servicio de detección de idioma inicializado")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detecta el idioma de un texto usando análisis de patrones
        
        Args:
            text: Texto a analizar
            
        Returns:
            Tupla (código_idioma, confianza)
        """
        if not text or len(text.strip()) < 2:
            return "en", 0.3  # Default fallback
        
        text_lower = text.lower().strip()
        scores = {}
        
        # Análisis por caracteres especiales
        for lang_code, lang_info in self.supported_languages.items():
            char_patterns = lang_info["char_patterns"]
            if char_patterns:
                char_matches = sum(1 for char in text_lower if char in char_patterns)
                char_score = char_matches / len(text_lower) if text_lower else 0
                scores[lang_code] = char_score * 0.4  # 40% peso para caracteres
        
        # Análisis por palabras comunes
        words = re.findall(r'\b\w+\b', text_lower)
        if words:
            for lang_code, lang_info in self.supported_languages.items():
                word_matches = sum(1 for word in words if word in lang_info["patterns"])
                word_score = word_matches / len(words) if words else 0
                scores[lang_code] = scores.get(lang_code, 0) + (word_score * 0.6)  # 60% peso para palabras
        
        # Encontrar idioma con mayor puntuación
        if scores:
            detected_lang = max(scores, key=scores.get)
            confidence = min(scores[detected_lang], 0.95)  # Máximo 95% de confianza
            
            # Ajustar confianza basada en longitud del texto
            if len(text) < 10:
                confidence *= 0.7  # Reducir confianza para textos cortos
            elif len(text) > 100:
                confidence = min(confidence * 1.2, 0.95)  # Aumentar para textos largos
        else:
            # Fallback básico
            if any(char in text_lower for char in "ñáéíóúü"):
                detected_lang, confidence = "es", 0.85
            elif any(char in text_lower for char in "çàâéèêëîïôùûüÿ"):
                detected_lang, confidence = "fr", 0.80
            elif any(char in text_lower for char in "äöüß"):
                detected_lang, confidence = "de", 0.80
            else:
                detected_lang, confidence = "en", 0.70
        
        # Actualizar estadísticas
        self._update_stats(detected_lang, confidence)
        
        logger.debug(f"Idioma detectado: {detected_lang} (confianza: {confidence:.2f}) para texto: {text[:50]}...")
        return detected_lang, confidence
    
    def detect_language_advanced(self, text: str, include_alternatives: bool = True) -> Dict:
        """
        Detección avanzada con alternativas y análisis detallado
        
        Args:
            text: Texto a analizar
            include_alternatives: Si incluir idiomas alternativos
            
        Returns:
            Diccionario con resultado detallado
        """
        start_time = time.time()
        
        detected_lang, confidence = self.detect_language(text)
        
        result = {
            "detected_language": detected_lang,
            "confidence": confidence,
            "text_length": len(text),
            "processing_time": time.time() - start_time,
            "alternatives": []
        }
        
        if include_alternatives:
            # Calcular puntuaciones para todos los idiomas
            all_scores = self._calculate_all_scores(text)
            
            # Crear lista de alternativas (excluyendo el detectado)
            alternatives = []
            for lang_code, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
                if lang_code != detected_lang and score > 0.1:
                    alternatives.append({
                        "language": lang_code,
                        "name": self.supported_languages[lang_code]["name"],
                        "confidence": round(score, 3)
                    })
            
            result["alternatives"] = alternatives[:3]  # Top 3 alternativas
        
        return result
    
    def _calculate_all_scores(self, text: str) -> Dict[str, float]:
        """Calcula puntuaciones para todos los idiomas"""
        text_lower = text.lower().strip()
        words = re.findall(r'\b\w+\b', text_lower)
        scores = {}
        
        for lang_code, lang_info in self.supported_languages.items():
            score = 0
            
            # Análisis de caracteres especiales
            char_patterns = lang_info["char_patterns"]
            if char_patterns:
                char_matches = sum(1 for char in text_lower if char in char_patterns)
                char_score = char_matches / len(text_lower) if text_lower else 0
                score += char_score * 0.4
            
            # Análisis de palabras comunes
            if words:
                word_matches = sum(1 for word in words if word in lang_info["patterns"])
                word_score = word_matches / len(words) if words else 0
                score += word_score * 0.6
            
            scores[lang_code] = score
        
        return scores
    
    def _update_stats(self, detected_lang: str, confidence: float):
        """Actualiza estadísticas de detección"""
        self.detection_stats["total_detections"] += 1
        
        if detected_lang not in self.detection_stats["language_counts"]:
            self.detection_stats["language_counts"][detected_lang] = 0
        self.detection_stats["language_counts"][detected_lang] += 1
        
        # Actualizar promedio de confianza
        total = self.detection_stats["total_detections"]
        current_avg = self.detection_stats["confidence_average"]
        self.detection_stats["confidence_average"] = ((current_avg * (total - 1)) + confidence) / total
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del servicio"""
        return {
            "service_status": "active",
            "supported_languages": len(self.supported_languages),
            "detection_stats": self.detection_stats.copy(),
            "top_languages": sorted(
                self.detection_stats["language_counts"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def is_supported_language(self, lang_code: str) -> bool:
        """Verifica si un idioma es soportado"""
        return lang_code in self.supported_languages
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Obtiene lista de idiomas soportados"""
        return [
            {
                "code": code,
                "name": info["name"]
            }
            for code, info in self.supported_languages.items()
        ]

# Instancia global del servicio
_language_detection_service = None

def get_language_detection_service() -> LanguageDetectionService:
    """Obtiene la instancia global del servicio de detección de idioma"""
    global _language_detection_service
    if _language_detection_service is None:
        _language_detection_service = LanguageDetectionService()
    return _language_detection_service

# Función de conveniencia para compatibilidad
def detect_language(text: str) -> Tuple[str, float]:
    """Función de conveniencia para detección de idioma"""
    service = get_language_detection_service()
    return service.detect_language(text)

# Exportar función para importación directa
__all__ = [
    'LanguageDetectionService',
    'get_language_detection_service', 
    'detect_language'
] 