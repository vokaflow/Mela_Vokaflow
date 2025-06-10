#!/usr/bin/env python3
"""
Router de Traducción - VokaFlow Backend
======================================

Servicios de traducción de texto y audio con soporte completo para múltiples idiomas.
"""

import os
import logging
import asyncio
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

# Importaciones locales
from src.backend.database import get_db
from src.backend.models import TranslationDB, UserDB
from src.backend.services.translation_service import TranslationService
from src.backend.services.stt_service import STTService
from src.backend.services.tts_service import TTSService
from src.backend.auth import get_current_user_optional

logger = logging.getLogger("vokaflow.translation")

# Crear router
router = APIRouter()

# Inicializar servicios
translation_service = TranslationService()
stt_service = STTService()
tts_service = TTSService()

# Modelos Pydantic
class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Texto a traducir")
    source_lang: str = Field("auto", description="Idioma origen (código ISO 639-1 o 'auto')")
    target_lang: str = Field(..., description="Idioma destino (código ISO 639-1)")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('El texto no puede estar vacío')
        return v.strip()
    
    @validator('source_lang', 'target_lang')
    def validate_language_codes(cls, v):
        # Lista de códigos de idioma soportados
        supported_languages = [
            'auto', 'es', 'en', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 
            'ar', 'hi', 'tr', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'sk',
            'hu', 'ro', 'bg', 'hr', 'sl', 'et', 'lv', 'lt', 'mt', 'el', 'cy'
        ]
        
        if v not in supported_languages:
            raise ValueError(f'Código de idioma no soportado: {v}')
        return v

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time: float
    detected_language: Optional[str] = None

class AudioTranslationRequest(BaseModel):
    source_lang: str = Field("auto", description="Idioma origen")
    target_lang: str = Field(..., description="Idioma destino")
    voice_id: Optional[str] = Field("speaker_es_f01", description="ID de voz para síntesis")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Velocidad de síntesis")

class AudioTranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    audio_url: str
    audio_base64: Optional[str] = None
    processing_time: float

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    supported_languages: List[str]

class SupportedLanguagesResponse(BaseModel):
    languages: Dict[str, str]
    total_count: int

# Endpoints principales

@router.post("/text", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_current_user_optional)
):
    """
    Traduce texto entre idiomas soportados.
    
    - **text**: Texto a traducir (máximo 5000 caracteres)
    - **source_lang**: Idioma origen ('auto' para detección automática)
    - **target_lang**: Idioma destino
    """
    try:
        logger.info(f"Traduciendo texto: {request.source_lang} -> {request.target_lang}")
        
        start_time = datetime.now()
        
        # Realizar traducción
        result = await translation_service.translate_text(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Preparar respuesta
        response = TranslationResponse(
            translated_text=result["translated_text"],
            source_lang=result["source_lang"],
            target_lang=result["target_lang"],
            confidence=result["confidence"],
            processing_time=processing_time,
            detected_language=result.get("detected_language")
        )
        
        # Guardar en base de datos de forma asíncrona
        if current_user:
            background_tasks.add_task(
                save_translation_to_db,
                db, current_user.id, request, response, processing_time
            )
        
        logger.info(f"Traducción completada en {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error en traducción de texto: {e}")
        raise HTTPException(status_code=500, detail=f"Error en traducción: {str(e)}")

@router.post("/audio", response_model=AudioTranslationResponse)
async def translate_audio(
    audio: UploadFile = File(..., description="Archivo de audio (WAV, MP3, M4A, FLAC)"),
    source_lang: str = Form("auto", description="Idioma origen"),
    target_lang: str = Form(..., description="Idioma destino"),
    voice_id: str = Form("speaker_es_f01", description="ID de voz para síntesis"),
    speed: float = Form(1.0, description="Velocidad de síntesis"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_current_user_optional)
):
    """
    Traduce audio: STT → Traducción → TTS
    
    Proceso completo:
    1. Convierte audio a texto (STT)
    2. Traduce el texto
    3. Convierte traducción a audio (TTS)
    """
    try:
        logger.info(f"Traduciendo audio: {source_lang} -> {target_lang}")
        
        start_time = datetime.now()
        
        # Validar archivo de audio
        if not audio.filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
        file_extension = Path(audio.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Verificar tamaño del archivo
        content = await audio.read()
        if len(content) > 25 * 1024 * 1024:  # 25MB
            raise HTTPException(status_code=413, detail="Archivo demasiado grande (máximo 25MB)")
        
        # Paso 1: Audio a texto (STT)
        logger.info("Paso 1: Transcribiendo audio...")
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_audio:
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            stt_result = await stt_service.transcribe_audio(
                audio_path=temp_audio_path,
                language=source_lang if source_lang != "auto" else None
            )
            
            original_text = stt_result["transcript"]
            detected_lang = stt_result.get("language", source_lang)
            
            if not original_text.strip():
                raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")
            
            logger.info(f"Transcripción: '{original_text[:50]}...'")
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
        # Paso 2: Traducir texto
        logger.info("Paso 2: Traduciendo texto...")
        translation_result = await translation_service.translate_text(
            text=original_text,
            source_lang=detected_lang,
            target_lang=target_lang
        )
        
        translated_text = translation_result["translated_text"]
        confidence = translation_result["confidence"]
        
        logger.info(f"Traducción: '{translated_text[:50]}...'")
        
        # Paso 3: Texto a audio (TTS)
        logger.info("Paso 3: Sintetizando audio...")
        tts_result = await tts_service.synthesize_speech(
            text=translated_text,
            language=target_lang,
            voice_id=voice_id,
            speed=speed
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Preparar respuesta
        response = AudioTranslationResponse(
            original_text=original_text,
            translated_text=translated_text,
            source_language=detected_lang,
            target_language=target_lang,
            confidence=confidence,
            audio_url=tts_result["audio_url"],
            audio_base64=tts_result.get("audio_base64"),
            processing_time=processing_time
        )
        
        # Guardar en base de datos
        if current_user:
            background_tasks.add_task(
                save_audio_translation_to_db,
                db, current_user.id, original_text, translated_text, 
                detected_lang, target_lang, confidence, processing_time
            )
        
        logger.info(f"Traducción de audio completada en {processing_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en traducción de audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error en traducción de audio: {str(e)}")

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(text: str = Form(..., min_length=1)):
    """
    Detecta el idioma de un texto.
    """
    try:
        result = await translation_service.detect_language(text)
        
        return LanguageDetectionResponse(
            detected_language=result["language"],
            confidence=result["confidence"],
            supported_languages=translation_service.get_supported_languages()
        )
        
    except Exception as e:
        logger.error(f"Error en detección de idioma: {e}")
        raise HTTPException(status_code=500, detail=f"Error en detección: {str(e)}")

@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """
    Obtiene la lista de idiomas soportados.
    """
    try:
        languages = translation_service.get_language_names()
        
        return SupportedLanguagesResponse(
            languages=languages,
            total_count=len(languages)
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo idiomas soportados: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_translation_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user_optional)
):
    """
    Obtiene el historial de traducciones del usuario.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    
    try:
        translations = db.query(TranslationDB)\
            .filter(TranslationDB.user_id == current_user.id)\
            .order_by(TranslationDB.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return {
            "translations": [
                {
                    "id": t.id,
                    "source_text": t.source_text,
                    "translated_text": t.translated_text,
                    "source_lang": t.source_lang,
                    "target_lang": t.target_lang,
                    "confidence": t.confidence,
                    "created_at": t.created_at.isoformat()
                }
                for t in translations
            ],
            "total": len(translations),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Funciones auxiliares

def save_translation_to_db(
    db: Session, 
    user_id: int, 
    request: TranslationRequest, 
    response: TranslationResponse, 
    processing_time: float
):
    """Guarda traducción en base de datos."""
    try:
        translation = TranslationDB(
            user_id=user_id,
            source_text=request.text,
            translated_text=response.translated_text,
            source_lang=response.source_lang,
            target_lang=response.target_lang,
            confidence=response.confidence,
            processing_time=processing_time
        )
        db.add(translation)
        db.commit()
        logger.info(f"Traducción guardada en BD para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error guardando traducción en BD: {e}")
        db.rollback()

def save_audio_translation_to_db(
    db: Session,
    user_id: int,
    original_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str,
    confidence: float,
    processing_time: float
):
    """Guarda traducción de audio en base de datos."""
    try:
        translation = TranslationDB(
            user_id=user_id,
            source_text=original_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=confidence,
            processing_time=processing_time
        )
        db.add(translation)
        db.commit()
        logger.info(f"Traducción de audio guardada en BD para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error guardando traducción de audio en BD: {e}")
        db.rollback()
