#!/usr/bin/env python3
"""
VokaFlow - Router de Traducción
Maneja traducción de texto, detección de idiomas, historial y estadísticas
"""

import os
import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from pydantic import BaseModel, validator, Field
import json
import hashlib
import random

# Configuración de logging
logger = logging.getLogger("vokaflow.translate")

# Router
router = APIRouter()

# Configuración de traducción
SUPPORTED_LANGUAGES = {
    "es": {"name": "Español", "native": "Español", "flag": "🇪🇸", "rtl": False},
    "en": {"name": "English", "native": "English", "flag": "🇺🇸", "rtl": False},
    "fr": {"name": "Français", "native": "Français", "flag": "🇫🇷", "rtl": False},
    "de": {"name": "Deutsch", "native": "Deutsch", "flag": "🇩🇪", "rtl": False},
    "it": {"name": "Italiano", "native": "Italiano", "flag": "🇮🇹", "rtl": False},
    "pt": {"name": "Português", "native": "Português", "flag": "🇵🇹", "rtl": False},
    "ru": {"name": "Русский", "native": "Русский", "flag": "🇷🇺", "rtl": False},
    "zh": {"name": "中文", "native": "中文", "flag": "🇨🇳", "rtl": False},
    "ja": {"name": "日本語", "native": "日本語", "flag": "🇯🇵", "rtl": False},
    "ko": {"name": "한국어", "native": "한국어", "flag": "🇰🇷", "rtl": False},
    "ar": {"name": "العربية", "native": "العربية", "flag": "🇸🇦", "rtl": True},
    "hi": {"name": "हिन्दी", "native": "हिन्दी", "flag": "🇮🇳", "rtl": False},
    "tr": {"name": "Türkçe", "native": "Türkçe", "flag": "🇹🇷", "rtl": False},
    "nl": {"name": "Nederlands", "native": "Nederlands", "flag": "🇳🇱", "rtl": False},
    "sv": {"name": "Svenska", "native": "Svenska", "flag": "🇸🇪", "rtl": False}
}

# Modelos Pydantic
class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Texto a traducir")
    source_lang: Optional[str] = Field(None, description="Idioma origen (auto-detectar si es None)")
    target_lang: str = Field(..., description="Idioma destino")
    context: Optional[str] = Field(None, description="Contexto adicional para mejorar traducción")
    preserve_formatting: bool = Field(True, description="Preservar formato del texto")
    
    @validator('target_lang')
    def validate_target_lang(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f'Idioma no soportado: {v}')
        return v
    
    @validator('source_lang')
    def validate_source_lang(cls, v):
        if v is not None and v not in SUPPORTED_LANGUAGES:
            raise ValueError(f'Idioma no soportado: {v}')
        return v

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time: float
    detected_lang: Optional[str] = None
    alternatives: List[str] = []
    metadata: Dict[str, Any] = {}

class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    source_lang: Optional[str] = None
    target_lang: str
    preserve_order: bool = True

class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    total_processed: int
    total_time: float
    average_confidence: float

class LanguageDetectionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    alternatives: List[Dict[str, Union[str, float]]] = []

class TranslationHistory(BaseModel):
    id: str
    text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float
    created_at: datetime
    user_id: Optional[str] = None

class TranslationStats(BaseModel):
    total_translations: int
    languages_used: Dict[str, int]
    most_translated_pair: Dict[str, str]
    average_confidence: float
    total_characters: int
    translations_today: int
    translations_this_week: int
    translations_this_month: int

# Funciones de utilidad
def detect_language(text: str) -> tuple[str, float]:
    """Detecta el idioma del texto (simulado)"""
    # Simulación simple de detección de idioma
    text_lower = text.lower()
    
    # Patrones simples para detectar idiomas
    if any(word in text_lower for word in ['the', 'and', 'is', 'are', 'you', 'that', 'it']):
        return "en", 0.95
    elif any(word in text_lower for word in ['el', 'la', 'es', 'son', 'que', 'de', 'en', 'y']):
        return "es", 0.92
    elif any(word in text_lower for word in ['le', 'la', 'est', 'sont', 'que', 'de', 'et', 'dans']):
        return "fr", 0.88
    elif any(word in text_lower for word in ['der', 'die', 'das', 'ist', 'sind', 'und', 'in']):
        return "de", 0.85
    elif any(word in text_lower for word in ['il', 'la', 'è', 'sono', 'che', 'di', 'e', 'in']):
        return "it", 0.82
    else:
        return "en", 0.70  # Default a inglés con baja confianza

async def translate_text_engine(text: str, source_lang: str, target_lang: str, context: Optional[str] = None) -> dict:
    """Motor de traducción simulado"""
    start_time = time.time()
    
    # Simular tiempo de procesamiento
    await asyncio.sleep(0.2 + len(text) * 0.001)
    
    # Simulación de traducción
    if source_lang == target_lang:
        translated = text
        confidence = 1.0
    else:
        # Traducción simulada básica
        translations = {
            ("es", "en"): {
                "hola": "hello",
                "mundo": "world",
                "gracias": "thank you",
                "por favor": "please",
                "adiós": "goodbye"
            },
            ("en", "es"): {
                "hello": "hola",
                "world": "mundo",
                "thank you": "gracias",
                "please": "por favor",
                "goodbye": "adiós"
            },
            ("es", "fr"): {
                "hola": "bonjour",
                "mundo": "monde",
                "gracias": "merci"
            }
        }
        
        # Buscar traducciones conocidas
        text_lower = text.lower()
        lang_pair = (source_lang, target_lang)
        
        if lang_pair in translations:
            for original, translation in translations[lang_pair].items():
                if original in text_lower:
                    translated = text_lower.replace(original, translation)
                    confidence = 0.95
                    break
            else:
                translated = f"[{target_lang.upper()}] {text}"
                confidence = 0.75
        else:
            translated = f"[{target_lang.upper()}] {text}"
            confidence = 0.70
    
    processing_time = time.time() - start_time
    
    return {
        "translated_text": translated,
        "confidence": confidence,
        "processing_time": processing_time,
        "alternatives": [f"Alt: {translated}", f"Var: {translated}"] if confidence > 0.8 else []
    }

# Dependencias simuladas
async def get_current_user():
    """Simulación de obtener usuario actual"""
    return {
        "id": "user_123",
        "username": "admin",
        "email": "admin@vokaflow.com"
    }

# Endpoints principales
@router.post("/", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Traduce un texto del idioma origen al idioma destino"""
    try:
        logger.info(f"Solicitud de traducción: {request.text[:50]}... -> {request.target_lang}")
        
        # Detectar idioma si no se especifica
        source_lang = request.source_lang
        detected_lang = None
        
        if not source_lang:
            detected_lang, confidence = detect_language(request.text)
            source_lang = detected_lang
            logger.info(f"Idioma detectado: {detected_lang} (confianza: {confidence})")
        
        # Validar que el idioma origen sea diferente al destino
        if source_lang == request.target_lang:
            logger.warning("Idioma origen y destino son iguales")
        
        # Realizar traducción
        translation_result = await translate_text_engine(
            request.text,
            source_lang,
            request.target_lang,
            request.context
        )
        
        # Crear respuesta
        response = TranslationResponse(
            translated_text=translation_result["translated_text"],
            source_lang=source_lang,
            target_lang=request.target_lang,
            confidence=translation_result["confidence"],
            processing_time=translation_result["processing_time"],
            detected_lang=detected_lang,
            alternatives=translation_result["alternatives"],
            metadata={
                "character_count": len(request.text),
                "word_count": len(request.text.split()),
                "preserve_formatting": request.preserve_formatting,
                "context_provided": request.context is not None
            }
        )
        
        # Guardar en historial (tarea en segundo plano)
        background_tasks.add_task(
            save_translation_history,
            current_user["id"],
            request.text,
            response.translated_text,
            source_lang,
            request.target_lang,
            response.confidence
        )
        
        logger.info(f"Traducción completada en {response.processing_time:.3f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error en traducción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar traducción: {str(e)}"
        )

@router.post("/batch", response_model=BatchTranslationResponse)
async def translate_batch(
    request: BatchTranslationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Traduce múltiples textos en lote"""
    try:
        logger.info(f"Traducción en lote: {len(request.texts)} textos -> {request.target_lang}")
        
        start_time = time.time()
        translations = []
        total_confidence = 0
        
        for i, text in enumerate(request.texts):
            try:
                # Detectar idioma si no se especifica
                source_lang = request.source_lang
                if not source_lang:
                    source_lang, _ = detect_language(text)
                
                # Traducir texto
                translation_result = await translate_text_engine(
                    text, source_lang, request.target_lang
                )
                
                translation_response = TranslationResponse(
                    translated_text=translation_result["translated_text"],
                    source_lang=source_lang,
                    target_lang=request.target_lang,
                    confidence=translation_result["confidence"],
                    processing_time=translation_result["processing_time"],
                    alternatives=translation_result["alternatives"],
                    metadata={"batch_index": i}
                )
                
                translations.append(translation_response)
                total_confidence += translation_result["confidence"]
                
            except Exception as e:
                logger.error(f"Error en traducción de lote {i}: {e}")
                # Continuar con el siguiente texto
                continue
        
        total_time = time.time() - start_time
        average_confidence = total_confidence / len(translations) if translations else 0
        
        response = BatchTranslationResponse(
            translations=translations,
            total_processed=len(translations),
            total_time=total_time,
            average_confidence=average_confidence
        )
        
        logger.info(f"Lote completado: {len(translations)}/{len(request.texts)} en {total_time:.3f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error en traducción de lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar lote: {str(e)}"
        )

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_text_language(request: LanguageDetectionRequest):
    """Detecta el idioma de un texto"""
    try:
        logger.info(f"Detección de idioma: {request.text[:50]}...")
        
        detected_lang, confidence = detect_language(request.text)
        
        # Generar alternativas simuladas
        alternatives = []
        if confidence < 0.9:
            other_langs = ["en", "es", "fr", "de"]
            for lang in other_langs:
                if lang != detected_lang:
                    alternatives.append({
                        "language": lang,
                        "confidence": max(0.1, confidence - 0.2)
                    })
                    if len(alternatives) >= 3:
                        break
        
        response = LanguageDetectionResponse(
            detected_language=detected_lang,
            confidence=confidence,
            alternatives=alternatives
        )
        
        logger.info(f"Idioma detectado: {detected_lang} (confianza: {confidence})")
        return response
        
    except Exception as e:
        logger.error(f"Error en detección de idioma: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al detectar idioma: {str(e)}"
        )

@router.get("/languages")
async def get_supported_languages():
    """Obtiene la lista de idiomas soportados"""
    try:
        languages = []
        for code, info in SUPPORTED_LANGUAGES.items():
            languages.append({
                "code": code,
                "name": info["name"],
                "native_name": info["native"],
                "flag": info["flag"],
                "rtl": info["rtl"],
                "translation_quality": "high" if code in ["es", "en", "fr", "de"] else "medium"
            })
        
        return {
            "languages": languages,
            "total_count": len(languages),
            "popular_pairs": [
                {"source": "es", "target": "en"},
                {"source": "en", "target": "es"},
                {"source": "fr", "target": "es"},
                {"source": "de", "target": "en"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error al obtener idiomas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener idiomas soportados"
        )

@router.get("/history", response_model=List[TranslationHistory])
async def get_translation_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source_lang: Optional[str] = Query(None),
    target_lang: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene el historial de traducciones del usuario"""
    try:
        # Simular historial de traducciones
        history = []
        for i in range(min(limit, 10)):  # Simular hasta 10 entradas
            history.append(TranslationHistory(
                id=f"trans_{i+1}",
                text=f"Texto de ejemplo {i+1}",
                translated_text=f"Example text {i+1}",
                source_lang="es",
                target_lang="en",
                confidence=0.85 + (i * 0.01),
                created_at=datetime.now() - timedelta(hours=i),
                user_id=current_user["id"]
            ))
        
        logger.info(f"Historial obtenido: {len(history)} entradas")
        return history
        
    except Exception as e:
        logger.error(f"Error al obtener historial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener historial"
        )

@router.get("/stats", response_model=TranslationStats)
async def get_translation_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Obtiene estadísticas de traducción del usuario"""
    try:
        stats = TranslationStats(
            total_translations=1250,
            languages_used={
                "es": 450,
                "en": 380,
                "fr": 120,
                "de": 95,
                "it": 75,
                "pt": 60,
                "other": 70
            },
            most_translated_pair={
                "source": "es",
                "target": "en"
            },
            average_confidence=0.87,
            total_characters=125000,
            translations_today=25,
            translations_this_week=180,
            translations_this_month=750
        )
        
        logger.info("Estadísticas de traducción obtenidas")
        return stats
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )

@router.get("/dashboard-stats")
async def get_translations_dashboard_stats():
    """
    🌐 Estadísticas de traducciones para el dashboard
    
    Endpoint específico para el dashboard frontend que devuelve
    las estadísticas en el formato exacto esperado
    """
    try:
        # Simular datos reales de traducciones
        dashboard_stats = {
            "active": random.randint(15, 25),
            "completed": random.randint(100, 150),
            "german": random.randint(30, 40),
            "spanish": random.randint(15, 25), 
            "french": random.randint(15, 25),
            "japanese": random.randint(10, 15),
            # Alias para compatibilidad
            "de": random.randint(30, 40),
            "es": random.randint(15, 25),
            "fr": random.randint(15, 25),
            "ja": random.randint(10, 15)
        }
        
        return {
            "success": True,
            "data": dashboard_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas de traducciones: {str(e)}"
        )

@router.delete("/history/{translation_id}")
async def delete_translation(
    translation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Elimina una traducción del historial"""
    try:
        logger.info(f"Eliminando traducción {translation_id}")
        
        # Simular eliminación
        return {
            "message": f"Traducción {translation_id} eliminada exitosamente",
            "deleted_id": translation_id
        }
        
    except Exception as e:
        logger.error(f"Error al eliminar traducción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar traducción"
        )

@router.get("/status")
async def translation_service_status():
    """Verifica el estado del servicio de traducción"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "components": {
            "translation_engine": "operational",
            "language_detection": "operational",
            "batch_processing": "operational",
            "history_storage": "operational"
        },
        "supported_languages": len(SUPPORTED_LANGUAGES),
        "metrics": {
            "translations_today": 1250,
            "average_response_time": "0.3s",
            "success_rate": "99.2%",
            "most_popular_pair": "es->en"
        }
    }

# Funciones auxiliares
async def save_translation_history(
    user_id: str,
    original_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str,
    confidence: float
):
    """Guarda una traducción en el historial (tarea en segundo plano)"""
    try:
        # Simular guardado en base de datos
        translation_id = hashlib.md5(f"{user_id}{original_text}{datetime.now()}".encode()).hexdigest()[:12]
        logger.info(f"Traducción guardada en historial: {translation_id}")
    except Exception as e:
        logger.error(f"Error al guardar en historial: {e}")
