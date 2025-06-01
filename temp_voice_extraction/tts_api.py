"""
API para síntesis de voz en VokaFlow.
Permite convertir texto a voz con diferentes opciones y voces.
"""
import os
import time
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..models.tts_model import TTSModel
from ..core.voice_cloning import VoiceCloner

logger = logging.getLogger("vicky.api.tts_api")

# Modelos Pydantic
class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "es"
    gender: Optional[str] = "female"
    custom_voice_id: Optional[str] = None
    emotion: Optional[str] = "neutral"
    speed: Optional[float] = 1.0
    pitch: Optional[float] = 0.0

class TTSResponse(BaseModel):
    success: bool
    audio_path: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

# Router
router = APIRouter(prefix="/api/tts", tags=["text-to-speech"])

# Dependencia para obtener el modelo TTS
def get_tts_model():
    model = TTSModel()
    if not model.model:
        model.load()
    return model

# Dependencia para obtener el clonador de voz
def get_voice_cloner():
    return VoiceCloner()

@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(
    request: TTSRequest,
    tts_model: TTSModel = Depends(get_tts_model),
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Sintetiza voz a partir de texto.
    """
    start_time = time.time()
    
    try:
        # Determinar si se usa una voz personalizada
        speaker_wav = None
        if request.custom_voice_id:
            speaker_wav = voice_cloner.get_voice_sample_path(request.custom_voice_id)
            if not speaker_wav:
                logger.warning(f"Voz personalizada {request.custom_voice_id} no encontrada")
        
        # Sintetizar voz
        audio = tts_model.synthesize(
            text=request.text,
            language=request.language,
            gender=request.gender,
            speaker_wav=speaker_wav,
            emotion=request.emotion,
            speed=request.speed,
            pitch_shift=request.pitch
        )
        
        if len(audio) == 0:
            return TTSResponse(
                success=False,
                error="Error al sintetizar voz",
                processing_time=time.time() - start_time
            )
        
        # Guardar audio en archivo temporal
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"tts_output_{int(time.time())}.wav")
        
        if not tts_model.save_audio(audio, output_path):
            return TTSResponse(
                success=False,
                error="Error al guardar audio",
                processing_time=time.time() - start_time
            )
        
        return TTSResponse(
            success=True,
            audio_path=output_path,
            processing_time=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Error en síntesis de voz: {e}")
        return TTSResponse(
            success=False,
            error=str(e),
            processing_time=time.time() - start_time
        )

@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    Obtiene un archivo de audio generado.
    """
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        return FileResponse(
            file_path,
            media_type="audio/wav",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener archivo de audio {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices(
    language: Optional[str] = None,
    gender: Optional[str] = None,
    include_custom: bool = True,
    user_id: Optional[str] = None,
    tts_model: TTSModel = Depends(get_tts_model),
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Obtiene las voces disponibles.
    """
    try:
        # Obtener voces estándar
        if language:
            voices = tts_model.get_voices_for_language(language)
        else:
            languages = tts_model.get_available_languages()
            voices = {
                "languages": languages,
                "standard_voices": {}
            }
            for lang in languages:
                lang_code = lang["code"]
                voices["standard_voices"][lang_code] = tts_model.get_voices_for_language(lang_code)
        
        # Incluir voces personalizadas si se solicita
        if include_custom:
            custom_voices = []
            if user_id:
                custom_voices = voice_cloner.get_user_voices(user_id)
            else:
                # Obtener todas las voces personalizadas
                for voice_id in voice_cloner.voice_metadata:
                    voice = voice_cloner.get_voice(voice_id)
                    if voice:
                        custom_voices.append(voice)
            
            voices["custom_voices"] = custom_voices
        
        return voices
    except Exception as e:
        logger.error(f"Error al obtener voces disponibles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
