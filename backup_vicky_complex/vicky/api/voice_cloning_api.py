"""
API para la clonación de voz en VokaFlow.
Permite a los usuarios subir muestras de voz y clonarlas para síntesis.
"""
import os
import time
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ..core.voice_cloning import VoiceCloner

logger = logging.getLogger("vicky.api.voice_cloning_api")

# Modelos Pydantic
class VoiceMetadata(BaseModel):
    name: str
    language: str
    gender: str
    description: Optional[str] = None

class VoiceResponse(BaseModel):
    success: bool
    voice_id: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VoiceListResponse(BaseModel):
    success: bool
    voices: List[Dict[str, Any]] = []
    error: Optional[str] = None

# Router
router = APIRouter(prefix="/api/voice-cloning", tags=["voice-cloning"])

# Dependencia para obtener el clonador de voz
def get_voice_cloner():
    return VoiceCloner()

@router.post("/upload", response_model=VoiceResponse)
async def upload_voice_sample(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Sube una muestra de voz para su procesamiento.
    """
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Escribir contenido
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Importar la muestra
        result = voice_cloner.import_voice_sample(temp_path)
        
        # Programar limpieza del archivo temporal
        background_tasks.add_task(os.unlink, temp_path)
        
        if not result["success"]:
            return VoiceResponse(success=False, error=result["error"])
        
        return VoiceResponse(
            success=True,
            metadata={
                "temp_id": result["temp_id"],
                "temp_path": result["temp_path"],
                "duration": result["duration"],
                "sample_rate": result["sample_rate"],
                "channels": result["channels"],
                "original_filename": result["original_filename"]
            }
        )
    except Exception as e:
        logger.error(f"Error al subir muestra de voz: {e}")
        return VoiceResponse(success=False, error=str(e))

@router.post("/process", response_model=VoiceResponse)
async def process_voice_sample(
    metadata: VoiceMetadata,
    user_id: str,
    temp_id: str,
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Procesa una muestra de voz previamente subida.
    """
    try:
        # Obtener ruta del archivo temporal
        temp_path = os.path.join(voice_cloner.temp_dir, temp_id)
        if not os.path.exists(temp_path):
            return VoiceResponse(success=False, error="Muestra temporal no encontrada")
        
        # Buscar archivo de audio en el directorio temporal
        audio_files = []
        for ext in voice_cloner.supported_formats:
            audio_files.extend([f for f in os.listdir(temp_path) if f.endswith(ext)])
        
        if not audio_files:
            return VoiceResponse(success=False, error="No se encontró archivo de audio en la muestra temporal")
        
        # Procesar la muestra
        sample_path = os.path.join(temp_path, audio_files[0])
        result = voice_cloner.process_voice_sample(
            sample_path=sample_path,
            user_id=user_id,
            voice_name=metadata.name,
            language=metadata.language,
            gender=metadata.gender,
            description=metadata.description
        )
        
        # Programar limpieza del directorio temporal
        voice_cloner.cleanup_temp_files(temp_id)
        
        if not result["success"]:
            return VoiceResponse(success=False, error=result.get("error", "Error desconocido"))
        
        return VoiceResponse(
            success=True,
            voice_id=result["voice_id"],
            metadata=result["metadata"]
        )
    except Exception as e:
        logger.error(f"Error al procesar muestra de voz: {e}")
        return VoiceResponse(success=False, error=str(e))

@router.get("/voices/{user_id}", response_model=VoiceListResponse)
async def get_user_voices(
    user_id: str,
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Obtiene todas las voces personalizadas de un usuario.
    """
    try:
        voices = voice_cloner.get_user_voices(user_id)
        return VoiceListResponse(success=True, voices=voices)
    except Exception as e:
        logger.error(f"Error al obtener voces del usuario {user_id}: {e}")
        return VoiceListResponse(success=False, error=str(e))

@router.get("/voice/{voice_id}", response_model=VoiceResponse)
async def get_voice_info(
    voice_id: str,
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Obtiene información de una voz específica.
    """
    try:
        voice = voice_cloner.get_voice(voice_id)
        if not voice:
            return VoiceResponse(success=False, error="Voz no encontrada")
        
        return VoiceResponse(success=True, voice_id=voice_id, metadata=voice)
    except Exception as e:
        logger.error(f"Error al obtener información de voz {voice_id}: {e}")
        return VoiceResponse(success=False, error=str(e))

@router.delete("/voice/{voice_id}", response_model=VoiceResponse)
async def delete_voice(
    voice_id: str,
    user_id: str,
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Elimina una voz personalizada.
    """
    try:
        success = voice_cloner.delete_voice(voice_id, user_id)
        if not success:
            return VoiceResponse(success=False, error="No se pudo eliminar la voz")
        
        return VoiceResponse(success=True)
    except Exception as e:
        logger.error(f"Error al eliminar voz {voice_id}: {e}")
        return VoiceResponse(success=False, error=str(e))

@router.get("/sample/{voice_id}")
async def get_voice_sample(
    voice_id: str,
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Obtiene el archivo de muestra de una voz.
    """
    try:
        sample_path = voice_cloner.get_voice_sample_path(voice_id)
        if not sample_path:
            raise HTTPException(status_code=404, detail="Muestra de voz no encontrada")
        
        return FileResponse(
            sample_path,
            media_type="audio/wav",
            filename=f"voice_sample_{voice_id}.wav"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener muestra de voz {voice_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/voice/{voice_id}", response_model=VoiceResponse)
async def update_voice_metadata(
    voice_id: str,
    metadata: VoiceMetadata,
    user_id: str,
    voice_cloner: VoiceCloner = Depends(get_voice_cloner)
):
    """
    Actualiza los metadatos de una voz personalizada.
    """
    try:
        updates = {
            "name": metadata.name,
            "language": metadata.language,
            "gender": metadata.gender,
            "description": metadata.description
        }
        
        success = voice_cloner.update_voice_metadata(voice_id, updates, user_id)
        if not success:
            return VoiceResponse(success=False, error="No se pudieron actualizar los metadatos")
        
        # Obtener metadatos actualizados
        voice = voice_cloner.get_voice(voice_id)
        
        return VoiceResponse(success=True, voice_id=voice_id, metadata=voice)
    except Exception as e:
        logger.error(f"Error al actualizar metadatos de voz {voice_id}: {e}")
        return VoiceResponse(success=False, error=str(e))
