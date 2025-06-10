#!/usr/bin/env python3
"""
Router de Chat - VokaFlow Backend con Vicky AI
=============================================

Sistema de chat inteligente con Vicky, la asistente personal con personalidad 
y capacidades de voz en español.
"""

import os
import logging
import asyncio
import tempfile
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

# Importaciones locales
from src.backend.database import get_db
from src.backend.models import ConversationDB, MessageDB, UserDB
from src.backend.services.deepseek_service import DeepSeekService
from src.backend.services.stt_service import STTService
from src.backend.services.tts_service import TTSService
from src.backend.services.vicky_personality import VickyPersonality
from src.backend.auth import get_current_user_optional

logger = logging.getLogger("vokaflow.chat")

# Crear router
router = APIRouter()

# Inicializar servicios
deepseek_service = DeepSeekService()
stt_service = STTService()
tts_service = TTSService()
vicky_personality = VickyPersonality()

# Modelos Pydantic
class ChatMessage(BaseModel):
    role: str = Field(..., description="Rol del mensaje: 'user', 'assistant', 'system'")
    content: str = Field(..., min_length=1, max_length=4000, description="Contenido del mensaje")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'Rol debe ser uno de: {allowed_roles}')
        return v

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Mensaje del usuario")
    conversation_id: Optional[int] = Field(None, description="ID de conversación existente")
    include_voice: bool = Field(False, description="Incluir respuesta de voz")
    voice_speed: float = Field(1.0, ge=0.5, le=2.0, description="Velocidad de síntesis de voz")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('El mensaje no puede estar vacío')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    thinking_process: Optional[str] = None
    voice_url: Optional[str] = None
    voice_base64: Optional[str] = None
    processing_time: float
    vicky_mood: str
    memory_updated: bool

class VoiceChatRequest(BaseModel):
    conversation_id: Optional[int] = Field(None, description="ID de conversación existente")
    include_voice_response: bool = Field(True, description="Incluir respuesta de voz")
    voice_speed: float = Field(1.0, ge=0.5, le=2.0, description="Velocidad de síntesis")

class VoiceChatResponse(BaseModel):
    transcribed_text: str
    response: str
    conversation_id: int
    thinking_process: Optional[str] = None
    voice_url: str
    voice_base64: Optional[str] = None
    processing_time: float
    vicky_mood: str

class ConversationSummary(BaseModel):
    id: int
    title: str
    message_count: int
    last_message: str
    created_at: str
    updated_at: str

class VickyStatusResponse(BaseModel):
    name: str
    version: str
    personality_active: bool
    mood: str
    memory_entries: int
    conversations_today: int
    uptime: str
    voice_available: bool

# Endpoints principales

@router.post("/message", response_model=ChatResponse)
async def chat_with_vicky(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_current_user_optional)
):
    """
    Chat con Vicky, la asistente personal con IA avanzada.
    
    Vicky tiene personalidad propia, memoria persistente y puede responder con voz.
    """
    try:
        logger.info(f"Mensaje para Vicky: '{request.message[:50]}...'")
        
        start_time = datetime.now()
        
        # Obtener o crear conversación
        conversation = await get_or_create_conversation(
            db, request.conversation_id, current_user, request.message
        )
        
        # Obtener historial de conversación para contexto
        conversation_history = await get_conversation_history(db, conversation.id)
        
        # Procesar mensaje con Vicky
        logger.info("Procesando mensaje con Vicky AI...")
        vicky_response = await vicky_personality.process_message(
            user_message=request.message,
            conversation_history=conversation_history,
            user_info=get_user_info(current_user) if current_user else None
        )
        
        # Generar respuesta con DeepSeek
        deepseek_result = await deepseek_service.generate_response(
            message=request.message,
            conversation_history=conversation_history,
            vicky_context=vicky_response
        )
        
        # Personalizar respuesta con personalidad de Vicky
        final_response = await vicky_personality.personalize_response(
            base_response=deepseek_result["response"],
            user_message=request.message,
            thinking_process=deepseek_result.get("thinking_process")
        )
        
        # Guardar mensajes en base de datos
        await save_chat_messages(
            db, conversation.id, request.message, final_response["response"]
        )
        
        # Actualizar memoria de Vicky
        memory_updated = await vicky_personality.update_memory(
            user_message=request.message,
            assistant_response=final_response["response"],
            user_info=get_user_info(current_user) if current_user else None
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Preparar respuesta base
        response = ChatResponse(
            response=final_response["response"],
            conversation_id=conversation.id,
            thinking_process=deepseek_result.get("thinking_process"),
            processing_time=processing_time,
            vicky_mood=final_response["mood"],
            memory_updated=memory_updated
        )
        
        # Generar voz si se solicita
        if request.include_voice:
            logger.info("Generando respuesta de voz...")
            voice_result = await tts_service.synthesize_speech(
                text=final_response["response"],
                language="es",
                voice_id="speaker_es_f01",  # Voz femenina en español
                speed=request.voice_speed
            )
            
            response.voice_url = voice_result["audio_url"]
            response.voice_base64 = voice_result.get("audio_base64")
        
        logger.info(f"Vicky respondió en {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error en chat con Vicky: {e}")
        raise HTTPException(status_code=500, detail=f"Error en chat: {str(e)}")

@router.post("/voice", response_model=VoiceChatResponse)
async def voice_chat_with_vicky(
    audio: UploadFile = File(..., description="Archivo de audio con mensaje para Vicky"),
    conversation_id: Optional[int] = Form(None, description="ID de conversación"),
    include_voice_response: bool = Form(True, description="Incluir respuesta de voz"),
    voice_speed: float = Form(1.0, description="Velocidad de síntesis"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_current_user_optional)
):
    """
    Chat por voz con Vicky: Audio → STT → Chat → TTS
    
    Proceso completo:
    1. Convierte audio a texto (STT)
    2. Procesa con Vicky
    3. Responde con voz en español
    """
    try:
        logger.info("Iniciando chat por voz con Vicky...")
        
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
        
        # Leer y validar contenido
        content = await audio.read()
        if len(content) > 25 * 1024 * 1024:  # 25MB
            raise HTTPException(status_code=413, detail="Archivo demasiado grande (máximo 25MB)")
        
        # Paso 1: Audio a texto (STT)
        logger.info("Transcribiendo audio del usuario...")
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_audio:
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        try:
            stt_result = await stt_service.transcribe_audio(
                audio_path=temp_audio_path,
                language="es"  # Forzar español para Vicky
            )
            
            transcribed_text = stt_result["transcript"]
            
            if not transcribed_text.strip():
                raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")
            
            logger.info(f"Usuario dijo: '{transcribed_text}'")
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
        # Paso 2: Procesar con Vicky (igual que chat de texto)
        conversation = await get_or_create_conversation(
            db, conversation_id, current_user, transcribed_text
        )
        
        conversation_history = await get_conversation_history(db, conversation.id)
        
        vicky_response = await vicky_personality.process_message(
            user_message=transcribed_text,
            conversation_history=conversation_history,
            user_info=get_user_info(current_user) if current_user else None
        )
        
        deepseek_result = await deepseek_service.generate_response(
            message=transcribed_text,
            conversation_history=conversation_history,
            vicky_context=vicky_response
        )
        
        final_response = await vicky_personality.personalize_response(
            base_response=deepseek_result["response"],
            user_message=transcribed_text,
            thinking_process=deepseek_result.get("thinking_process")
        )
        
        # Guardar mensajes
        await save_chat_messages(
            db, conversation.id, transcribed_text, final_response["response"]
        )
        
        # Actualizar memoria
        await vicky_personality.update_memory(
            user_message=transcribed_text,
            assistant_response=final_response["response"],
            user_info=get_user_info(current_user) if current_user else None
        )
        
        # Paso 3: Generar respuesta de voz
        logger.info("Vicky generando respuesta de voz...")
        voice_result = await tts_service.synthesize_speech(
            text=final_response["response"],
            language="es",
            voice_id="speaker_es_f01",  # Voz femenina de Vicky
            speed=voice_speed
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = VoiceChatResponse(
            transcribed_text=transcribed_text,
            response=final_response["response"],
            conversation_id=conversation.id,
            thinking_process=deepseek_result.get("thinking_process"),
            voice_url=voice_result["audio_url"],
            voice_base64=voice_result.get("audio_base64"),
            processing_time=processing_time,
            vicky_mood=final_response["mood"]
        )
        
        logger.info(f"Chat por voz completado en {processing_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en chat por voz: {e}")
        raise HTTPException(status_code=500, detail=f"Error en chat por voz: {str(e)}")

@router.get("/conversations", response_model=List[ConversationSummary])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user_optional)
):
    """
    Obtiene el historial de conversaciones con Vicky.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    
    try:
        conversations = db.query(ConversationDB)\
            .filter(ConversationDB.user_id == current_user.id)\
            .order_by(ConversationDB.updated_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        summaries = []
        for conv in conversations:
            # Obtener último mensaje
            last_message = db.query(MessageDB)\
                .filter(MessageDB.conversation_id == conv.id)\
                .order_by(MessageDB.created_at.desc())\
                .first()
            
            # Contar mensajes
            message_count = db.query(MessageDB)\
                .filter(MessageDB.conversation_id == conv.id)\
                .count()
            
            summaries.append(ConversationSummary(
                id=conv.id,
                title=conv.title,
                message_count=message_count,
                last_message=last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else (last_message.content if last_message else ""),
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat()
            ))
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user_optional)
):
    """
    Obtiene los mensajes de una conversación específica.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    
    try:
        # Verificar que la conversación pertenece al usuario
        conversation = db.query(ConversationDB)\
            .filter(ConversationDB.id == conversation_id, ConversationDB.user_id == current_user.id)\
            .first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        messages = db.query(MessageDB)\
            .filter(MessageDB.conversation_id == conversation_id)\
            .order_by(MessageDB.created_at.asc())\
            .all()
        
        return {
            "conversation_id": conversation_id,
            "title": conversation.title,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo mensajes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vicky/status", response_model=VickyStatusResponse)
async def get_vicky_status(db: Session = Depends(get_db)):
    """
    Obtiene el estado actual de Vicky AI.
    """
    try:
        status = await vicky_personality.get_status()
        
        # Estadísticas de base de datos
        today = datetime.now().date()
        conversations_today = db.query(ConversationDB)\
            .filter(ConversationDB.created_at >= today)\
            .count()
        
        return VickyStatusResponse(
            name="Vicky",
            version="1.0.0",
            personality_active=status["personality_active"],
            mood=status["current_mood"],
            memory_entries=status["memory_entries"],
            conversations_today=conversations_today,
            uptime=status["uptime"],
            voice_available=True
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de Vicky: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vicky/introduce")
async def vicky_introduction(
    include_voice: bool = Form(True),
    voice_speed: float = Form(1.0),
    db: Session = Depends(get_db),
    current_user: Optional[UserDB] = Depends(get_current_user_optional)
):
    """
    Vicky se presenta al usuario con su mensaje de introducción.
    """
    try:
        introduction = await vicky_personality.get_introduction(
            user_info=get_user_info(current_user) if current_user else None
        )
        
        response_data = {
            "message": introduction["text"],
            "mood": introduction["mood"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Agregar voz si se solicita
        if include_voice:
            voice_result = await tts_service.synthesize_speech(
                text=introduction["text"],
                language="es",
                voice_id="speaker_es_f01",
                speed=voice_speed
            )
            
            response_data["voice_url"] = voice_result["audio_url"]
            response_data["voice_base64"] = voice_result.get("audio_base64")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error en introducción de Vicky: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Funciones auxiliares

async def get_or_create_conversation(
    db: Session, 
    conversation_id: Optional[int], 
    user: Optional[UserDB],
    first_message: str
) -> ConversationDB:
    """Obtiene conversación existente o crea una nueva."""
    if conversation_id:
        conversation = db.query(ConversationDB).filter(ConversationDB.id == conversation_id).first()
        if conversation:
            return conversation
    
    # Crear nueva conversación
    title = generate_conversation_title(first_message)
    conversation = ConversationDB(
        user_id=user.id if user else None,
        title=title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

async def get_conversation_history(db: Session, conversation_id: int) -> List[Dict[str, str]]:
    """Obtiene el historial de mensajes de una conversación."""
    messages = db.query(MessageDB)\
        .filter(MessageDB.conversation_id == conversation_id)\
        .order_by(MessageDB.created_at.asc())\
        .all()
    
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

async def save_chat_messages(db: Session, conversation_id: int, user_message: str, assistant_response: str):
    """Guarda mensajes de chat en la base de datos."""
    try:
        # Mensaje del usuario
        user_msg = MessageDB(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        db.add(user_msg)
        
        # Respuesta de Vicky
        assistant_msg = MessageDB(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_response
        )
        db.add(assistant_msg)
        
        db.commit()
        logger.info(f"Mensajes guardados para conversación {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error guardando mensajes: {e}")
        db.rollback()

def generate_conversation_title(first_message: str) -> str:
    """Genera un título para la conversación basado en el primer mensaje."""
    # Tomar las primeras palabras del mensaje
    words = first_message.split()[:5]
    title = " ".join(words)
    
    # Limpiar y limitar
    title = title.strip()
    if len(title) > 50:
        title = title[:47] + "..."
    
    return title or "Nueva conversación"

def get_user_info(user: Optional[UserDB]) -> Optional[Dict[str, Any]]:
    """Obtiene información del usuario para el contexto."""
    if not user:
        return None
    
    return {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "is_new_user": (datetime.now() - user.created_at).days < 1
    }
