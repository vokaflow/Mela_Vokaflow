"""
Router para Vicky AI - Sistema de IA conversacional avanzado
"""
import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Query, Body
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

# Importaciones locales
from ..database import get_db
from ..auth import get_current_user, get_current_active_user
from ..models import UserDB, ConversationDB, MessageDB

logger = logging.getLogger(__name__)

router = APIRouter()

# Modelos Pydantic para Vicky AI
class VickyPersonality(str, Enum):
    BALANCED = "balanced"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"

class VickyMode(str, Enum):
    CHAT = "chat"
    ASSISTANT = "assistant"
    TUTOR = "tutor"
    TRANSLATOR = "translator"
    CODER = "coder"

class HemisphereBalance(BaseModel):
    technical: float = Field(ge=0.0, le=1.0, description="Balance técnico (0-1)")
    emotional: float = Field(ge=0.0, le=1.0, description="Balance emocional (0-1)")
    
    @validator('emotional')
    def validate_balance(cls, v, values):
        if 'technical' in values and abs(v + values['technical'] - 1.0) > 0.01:
            raise ValueError('La suma de technical y emotional debe ser 1.0')
        return v

class VickyRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[int] = None
    personality: Optional[VickyPersonality] = VickyPersonality.BALANCED
    mode: Optional[VickyMode] = VickyMode.CHAT
    hemisphere_balance: Optional[HemisphereBalance] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000)
    stream: Optional[bool] = False
    include_context: Optional[bool] = True
    language: Optional[str] = "es"

class VickyResponse(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None
    processing_time: Optional[float] = None
    hemisphere_balance: Optional[HemisphereBalance] = None
    confidence: Optional[float] = None
    tokens_used: Optional[int] = None

class VickyStreamChunk(BaseModel):
    chunk: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None

class VickyStatus(BaseModel):
    status: str
    version: str
    uptime: int
    loaded_models: List[str]
    memory_usage: Dict[str, int]
    processing_stats: Dict[str, Any]
    hemisphere_balance: HemisphereBalance
    active_conversations: int
    total_messages: int
    average_response_time: float

class VickyConfig(BaseModel):
    personality: VickyPersonality
    mode: VickyMode
    hemisphere_balance: HemisphereBalance
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=4000)
    language: str = "es"
    context_window: int = Field(10, ge=1, le=50)
    enable_memory: bool = True
    enable_learning: bool = True

class VickyMemory(BaseModel):
    id: Optional[int] = None
    user_id: int
    memory_type: str  # personal, factual, conversational
    content: str
    importance: float = Field(ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0

class VickyAnalytics(BaseModel):
    total_conversations: int
    total_messages: int
    average_response_time: float
    most_used_personality: str
    most_used_mode: str
    user_satisfaction: float
    error_rate: float
    uptime_percentage: float
    daily_stats: List[Dict[str, Any]]

# Simulador del cerebro de Vicky
class VickyBrain:
    def __init__(self):
        self.start_time = datetime.now()
        self.total_requests = 0
        self.total_response_time = 0.0
        self.current_balance = HemisphereBalance(technical=0.6, emotional=0.4)
        self.loaded_models = ["qwen-7b", "nllb-200", "whisper-medium", "vicky-personality-v1"]
        
    async def process_message(
        self, 
        request: VickyRequest, 
        user: Optional[UserDB] = None,
        db: Optional[Session] = None
    ) -> VickyResponse:
        """Procesa un mensaje usando el cerebro de Vicky"""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Determinar balance de hemisferios basado en el mensaje
            balance = self._analyze_hemisphere_balance(request.message, request.hemisphere_balance)
            
            # Generar respuesta basada en personalidad y modo
            response_text = await self._generate_response(request, balance, user)
            
            # Calcular métricas
            processing_time = time.time() - start_time
            self.total_response_time += processing_time
            
            # Guardar conversación si es necesario
            conversation_id, message_id = await self._save_conversation(
                request, response_text, user, db
            )
            
            return VickyResponse(
                response=response_text,
                context=request.context,
                metadata={
                    "personality": request.personality,
                    "mode": request.mode,
                    "language": request.language,
                    "model_used": "vicky-personality-v1",
                    "timestamp": datetime.now().isoformat()
                },
                conversation_id=conversation_id,
                message_id=message_id,
                processing_time=processing_time,
                hemisphere_balance=balance,
                confidence=0.92,
                tokens_used=len(response_text.split())
            )
            
        except Exception as e:
            logger.error(f"Error en VickyBrain.process_message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del cerebro de Vicky"
            )
    
    def _analyze_hemisphere_balance(
        self, 
        message: str, 
        custom_balance: Optional[HemisphereBalance]
    ) -> HemisphereBalance:
        """Analiza el balance de hemisferios necesario para el mensaje"""
        if custom_balance:
            return custom_balance
            
        # Palabras clave técnicas
        technical_keywords = [
            "código", "programa", "algoritmo", "función", "variable", "api", 
            "base de datos", "servidor", "desarrollo", "bug", "error", "debug",
            "framework", "biblioteca", "módulo", "clase", "método", "objeto"
        ]
        
        # Palabras clave emocionales
        emotional_keywords = [
            "siento", "emoción", "feliz", "triste", "preocupado", "ansioso",
            "amor", "miedo", "alegría", "dolor", "esperanza", "sueño",
            "corazón", "alma", "sentimiento", "pasión", "cariño", "amistad"
        ]
        
        message_lower = message.lower()
        technical_count = sum(1 for word in technical_keywords if word in message_lower)
        emotional_count = sum(1 for word in emotional_keywords if word in message_lower)
        
        if technical_count > emotional_count:
            return HemisphereBalance(technical=0.8, emotional=0.2)
        elif emotional_count > technical_count:
            return HemisphereBalance(technical=0.3, emotional=0.7)
        else:
            return HemisphereBalance(technical=0.6, emotional=0.4)
    
    async def _generate_response(
        self, 
        request: VickyRequest, 
        balance: HemisphereBalance,
        user: Optional[UserDB]
    ) -> str:
        """Genera una respuesta usando el modelo de IA"""
        # Simular tiempo de procesamiento
        await asyncio.sleep(0.3 + (balance.technical * 0.2))
        
        # Personalizar respuesta según personalidad
        personality_prefixes = {
            VickyPersonality.TECHNICAL: "Desde un punto de vista técnico, ",
            VickyPersonality.CREATIVE: "Imaginando posibilidades creativas, ",
            VickyPersonality.ANALYTICAL: "Analizando los datos disponibles, ",
            VickyPersonality.EMPATHETIC: "Entiendo cómo te sientes, ",
            VickyPersonality.BALANCED: ""
        }
        
        mode_contexts = {
            VickyMode.CHAT: "conversando contigo",
            VickyMode.ASSISTANT: "como tu asistente personal",
            VickyMode.TUTOR: "en modo educativo",
            VickyMode.TRANSLATOR: "enfocándome en la traducción",
            VickyMode.CODER: "desde la perspectiva de programación"
        }
        
        prefix = personality_prefixes.get(request.personality, "")
        context = mode_contexts.get(request.mode, "conversando contigo")
        
        # Generar respuesta contextual
        user_name = user.full_name if user and user.full_name else "usuario"
        
        if balance.technical > 0.7:
            response = f"{prefix}he procesado tu consulta técnica sobre '{request.message[:50]}...'. Como {context}, puedo ayudarte a resolver este problema paso a paso. ¿Te gustaría que profundice en algún aspecto específico?"
        elif balance.emotional > 0.7:
            response = f"{prefix}percibo que hay emociones importantes en tu mensaje, {user_name}. Como {context}, estoy aquí para escucharte y apoyarte. ¿Quieres contarme más sobre cómo te sientes?"
        else:
            response = f"{prefix}he analizado tu mensaje '{request.message[:50]}...'. Como {context}, puedo ofrecerte una perspectiva equilibrada. ¿En qué aspecto te gustaría que me enfoque más?"
        
        return response
    
    async def _save_conversation(
        self,
        request: VickyRequest,
        response: str,
        user: Optional[UserDB],
        db: Optional[Session]
    ) -> tuple[Optional[int], Optional[int]]:
        """Guarda la conversación en la base de datos"""
        if not user or not db:
            return None, None
            
        try:
            # Buscar o crear conversación
            conversation = None
            if request.conversation_id:
                conversation = db.query(ConversationDB).filter(
                    ConversationDB.id == request.conversation_id,
                    ConversationDB.user_id == user.id
                ).first()
            
            if not conversation:
                conversation = ConversationDB(
                    user_id=user.id,
                    title=request.message[:50] + "..." if len(request.message) > 50 else request.message
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
            
            # Guardar mensaje del usuario
            user_message = MessageDB(
                conversation_id=conversation.id,
                role="user",
                content=request.message
            )
            db.add(user_message)
            
            # Guardar respuesta de Vicky
            vicky_message = MessageDB(
                conversation_id=conversation.id,
                role="assistant",
                content=response
            )
            db.add(vicky_message)
            db.commit()
            db.refresh(vicky_message)
            
            return conversation.id, vicky_message.id
            
        except Exception as e:
            logger.error(f"Error al guardar conversación: {e}")
            return None, None
    
    def get_status(self) -> VickyStatus:
        """Obtiene el estado actual de Vicky"""
        uptime = int((datetime.now() - self.start_time).total_seconds())
        avg_response_time = (
            self.total_response_time / self.total_requests 
            if self.total_requests > 0 else 0.0
        )
        
        return VickyStatus(
            status="online",
            version="1.0.0",
            uptime=uptime,
            loaded_models=self.loaded_models,
            memory_usage={
                "total": 16384,
                "used": 8192,
                "free": 8192
            },
            processing_stats={
                "total_requests": self.total_requests,
                "average_response_time": avg_response_time,
                "requests_per_minute": self.total_requests / max(uptime / 60, 1)
            },
            hemisphere_balance=self.current_balance,
            active_conversations=25,  # Simulado
            total_messages=self.total_requests * 2,  # Usuario + Vicky
            average_response_time=avg_response_time
        )

# Instancia global del cerebro de Vicky
vicky_brain = VickyBrain()

# Endpoints de Vicky AI

@router.post("/process", response_model=VickyResponse)
async def process_vicky_request(
    request: VickyRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[UserDB] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Procesa una solicitud para Vicky AI
    """
    logger.info(f"Solicitud recibida para Vicky: {request.message[:50]}...")
    
    try:
        response = await vicky_brain.process_message(request, current_user, db)
        
        # Tarea en segundo plano para analytics
        background_tasks.add_task(
            _log_vicky_interaction,
            request.message,
            response.response,
            current_user.id if current_user else None,
            response.processing_time
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error al procesar solicitud para Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud"
        )

@router.post("/stream")
async def stream_vicky_response(
    request: VickyRequest,
    current_user: Optional[UserDB] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Procesa una solicitud para Vicky AI con respuesta en streaming
    """
    async def generate_stream():
        try:
            # Procesar mensaje
            response = await vicky_brain.process_message(request, current_user, db)
            
            # Simular streaming dividiendo la respuesta
            words = response.response.split()
            for i, word in enumerate(words):
                chunk = VickyStreamChunk(
                    chunk=word + " ",
                    is_final=(i == len(words) - 1),
                    metadata=response.metadata if i == len(words) - 1 else None
                )
                yield f"data: {chunk.json()}\n\n"
                await asyncio.sleep(0.05)  # Simular delay de streaming
                
        except Exception as e:
            error_chunk = VickyStreamChunk(
                chunk=f"Error: {str(e)}",
                is_final=True,
                metadata={"error": True}
            )
            yield f"data: {error_chunk.json()}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.get("/status", response_model=VickyStatus)
async def get_vicky_status():
    """
    Obtiene el estado actual de Vicky AI
    """
    try:
        return vicky_brain.get_status()
    except Exception as e:
        logger.error(f"Error al obtener estado de Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el estado del sistema"
        )

@router.get("/config", response_model=VickyConfig)
async def get_vicky_config(
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Obtiene la configuración actual de Vicky para el usuario
    """
    # En un sistema real, esto vendría de la base de datos del usuario
    return VickyConfig(
        personality=VickyPersonality.BALANCED,
        mode=VickyMode.CHAT,
        hemisphere_balance=HemisphereBalance(technical=0.6, emotional=0.4),
        temperature=0.7,
        max_tokens=1000,
        language="es",
        context_window=10,
        enable_memory=True,
        enable_learning=True
    )

@router.put("/config", response_model=VickyConfig)
async def update_vicky_config(
    config: VickyConfig,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza la configuración de Vicky para el usuario
    """
    try:
        # En un sistema real, guardaríamos esto en la base de datos
        logger.info(f"Configuración de Vicky actualizada para usuario {current_user.id}")
        
        # Actualizar balance global si es necesario
        vicky_brain.current_balance = config.hemisphere_balance
        
        return config
        
    except Exception as e:
        logger.error(f"Error al actualizar configuración de Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la configuración"
        )

@router.post("/hemisphere-balance", response_model=Dict[str, Any])
async def adjust_hemisphere_balance(
    balance: HemisphereBalance,
    current_user: UserDB = Depends(get_current_active_user)
):
    """
    Ajusta el balance de hemisferios de Vicky
    """
    try:
        vicky_brain.current_balance = balance
        
        return {
            "success": True,
            "message": f"Balance ajustado: {balance.technical:.1%} técnico, {balance.emotional:.1%} emocional",
            "new_balance": balance.dict()
        }
        
    except Exception as e:
        logger.error(f"Error al ajustar balance de hemisferios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al ajustar el balance"
        )

@router.get("/personalities")
async def get_available_personalities():
    """
    Obtiene las personalidades disponibles para Vicky
    """
    personalities = [
        {
            "id": "balanced",
            "name": "Equilibrada",
            "description": "Balance perfecto entre lógica y emoción",
            "hemisphere_balance": {"technical": 0.6, "emotional": 0.4},
            "best_for": ["conversación general", "consultas mixtas"]
        },
        {
            "id": "technical",
            "name": "Técnica",
            "description": "Enfocada en soluciones técnicas y lógicas",
            "hemisphere_balance": {"technical": 0.8, "emotional": 0.2},
            "best_for": ["programación", "resolución de problemas", "análisis"]
        },
        {
            "id": "creative",
            "name": "Creativa",
            "description": "Imaginativa y orientada a la innovación",
            "hemisphere_balance": {"technical": 0.4, "emotional": 0.6},
            "best_for": ["brainstorming", "escritura creativa", "arte"]
        },
        {
            "id": "analytical",
            "name": "Analítica",
            "description": "Basada en datos y análisis profundo",
            "hemisphere_balance": {"technical": 0.9, "emotional": 0.1},
            "best_for": ["análisis de datos", "investigación", "estadísticas"]
        },
        {
            "id": "empathetic",
            "name": "Empática",
            "description": "Comprensiva y emocionalmente inteligente",
            "hemisphere_balance": {"technical": 0.2, "emotional": 0.8},
            "best_for": ["apoyo emocional", "consejería", "conversación personal"]
        }
    ]
    
    return {"personalities": personalities}

@router.get("/modes")
async def get_available_modes():
    """
    Obtiene los modos disponibles para Vicky
    """
    modes = [
        {
            "id": "chat",
            "name": "Chat",
            "description": "Conversación casual y natural",
            "features": ["respuestas conversacionales", "contexto personal", "memoria de sesión"]
        },
        {
            "id": "assistant",
            "name": "Asistente",
            "description": "Asistente personal productivo",
            "features": ["tareas específicas", "recordatorios", "organización"]
        },
        {
            "id": "tutor",
            "name": "Tutor",
            "description": "Enseñanza y explicaciones educativas",
            "features": ["explicaciones paso a paso", "ejemplos", "evaluación"]
        },
        {
            "id": "translator",
            "name": "Traductor",
            "description": "Especializado en traducción y idiomas",
            "features": ["traducción contextual", "explicaciones lingüísticas", "cultura"]
        },
        {
            "id": "coder",
            "name": "Programador",
            "description": "Asistente de programación y desarrollo",
            "features": ["código", "debugging", "arquitectura", "mejores prácticas"]
        }
    ]
    
    return {"modes": modes}

@router.get("/analytics", response_model=VickyAnalytics)
async def get_vicky_analytics(
    days: int = Query(7, ge=1, le=30),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene analytics de Vicky AI
    """
    try:
        # En un sistema real, esto vendría de la base de datos
        daily_stats = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            daily_stats.append({
                "date": date.strftime("%Y-%m-%d"),
                "conversations": 15 + (i * 2),
                "messages": 45 + (i * 6),
                "avg_response_time": 0.8 + (i * 0.1),
                "user_satisfaction": 4.2 + (i * 0.1)
            })
        
        return VickyAnalytics(
            total_conversations=150,
            total_messages=450,
            average_response_time=0.85,
            most_used_personality="balanced",
            most_used_mode="chat",
            user_satisfaction=4.3,
            error_rate=0.02,
            uptime_percentage=99.8,
            daily_stats=daily_stats
        )
        
    except Exception as e:
        logger.error(f"Error al obtener analytics de Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener analytics"
        )

@router.post("/reset")
async def reset_vicky_session(
    conversation_id: Optional[int] = None,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reinicia la sesión de Vicky (limpia contexto y memoria)
    """
    try:
        if conversation_id:
            # Marcar conversación como finalizada
            conversation = db.query(ConversationDB).filter(
                ConversationDB.id == conversation_id,
                ConversationDB.user_id == current_user.id
            ).first()
            
            if conversation:
                conversation.updated_at = datetime.now()
                db.commit()
        
        return {
            "success": True,
            "message": "Sesión de Vicky reiniciada correctamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error al reiniciar sesión de Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al reiniciar la sesión"
        )

# Funciones auxiliares

async def _log_vicky_interaction(
    user_message: str,
    vicky_response: str,
    user_id: Optional[int],
    processing_time: float
):
    """Registra la interacción para analytics (tarea en segundo plano)"""
    try:
        # En un sistema real, esto se guardaría en una base de datos de analytics
        logger.info(f"Interacción registrada: usuario={user_id}, tiempo={processing_time:.3f}s")
    except Exception as e:
        logger.error(f"Error al registrar interacción: {e}")


@router.get("/metrics")
async def get_vicky_cognitive_metrics(
    timeframe: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$"),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene métricas cognitivas detalladas de Vicky
    """
    try:
        # Calcular métricas basadas en el timeframe
        timeframe_hours = {
            "1h": 1, "6h": 6, "24h": 24, "7d": 168, "30d": 720
        }[timeframe]
        
        since = datetime.now() - timedelta(hours=timeframe_hours)
        
        # Métricas cognitivas simuladas pero realistas
        cognitive_metrics = {
            "processing_efficiency": {
                "average_response_time": 0.85,
                "peak_response_time": 2.1,
                "min_response_time": 0.3,
                "efficiency_score": 92.5
            },
            "hemisphere_balance": {
                "current": {
                    "technical": vicky_brain.current_balance.technical,
                    "emotional": vicky_brain.current_balance.emotional
                },
                "average_24h": {"technical": 0.65, "emotional": 0.35},
                "adaptations_count": 15,
                "balance_stability": 0.88
            },
            "learning_metrics": {
                "new_patterns_learned": 23,
                "knowledge_retention": 0.94,
                "adaptation_speed": 0.76,
                "context_understanding": 0.91
            },
            "decision_quality": {
                "accuracy_score": 0.89,
                "confidence_average": 0.87,
                "decision_speed": 0.92,
                "reversal_rate": 0.03
            },
            "memory_usage": {
                "short_term_utilization": 0.67,
                "long_term_utilization": 0.45,
                "context_window_efficiency": 0.82,
                "memory_consolidation_rate": 0.78
            },
            "interaction_patterns": {
                "total_interactions": vicky_brain.total_requests,
                "unique_conversation_topics": 47,
                "average_conversation_length": 8.5,
                "user_satisfaction_score": 4.3
            },
            "cognitive_load": {
                "current_load": 0.34,
                "peak_load_24h": 0.78,
                "load_distribution": {
                    "language_processing": 0.25,
                    "reasoning": 0.30,
                    "memory_access": 0.20,
                    "response_generation": 0.25
                }
            },
            "error_analysis": {
                "total_errors": 3,
                "error_rate": 0.02,
                "recovery_time_average": 0.15,
                "error_categories": {
                    "context_misunderstanding": 1,
                    "processing_timeout": 1,
                    "memory_access_failure": 1
                }
            },
            "personality_metrics": {
                "personality_switches": 8,
                "mode_effectiveness": {
                    "chat": 0.92,
                    "assistant": 0.88,
                    "tutor": 0.85,
                    "translator": 0.90,
                    "coder": 0.87
                },
                "emotional_intelligence_score": 0.84
            },
            "timeframe": timeframe,
            "generated_at": datetime.now().isoformat()
        }
        
        return cognitive_metrics
        
    except Exception as e:
        logger.error(f"Error al obtener métricas cognitivas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener métricas cognitivas"
        )

@router.get("/decisions")
async def get_vicky_decision_history(
    limit: int = Query(50, ge=1, le=200),
    decision_type: Optional[str] = Query(None),
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de decisiones de Vicky
    """
    try:
        # Generar historial de decisiones simulado
        decision_types = [
            "personality_selection", "response_strategy", "hemisphere_balance",
            "context_interpretation", "knowledge_retrieval", "error_recovery",
            "conversation_flow", "emotional_response", "technical_analysis"
        ]
        
        decisions = []
        for i in range(min(limit, 50)):
            decision_time = datetime.now() - timedelta(minutes=i * 15)
            decision_type_selected = decision_types[i % len(decision_types)]
            confidence = 0.6 + (0.4 * (i % 10) / 10)
            
            # Filtrar por confidence_min si se especifica
            if confidence_min and confidence < confidence_min:
                continue
            
            # Filtrar por decision_type si se especifica
            if decision_type and decision_type_selected != decision_type:
                continue
            
            decision = {
                "id": f"dec_{i+1:04d}",
                "timestamp": decision_time.isoformat(),
                "decision_type": decision_type_selected,
                "context": f"Contexto de decisión {i+1}",
                "options_considered": [
                    {"option": "A", "score": confidence},
                    {"option": "B", "score": confidence - 0.1},
                    {"option": "C", "score": confidence - 0.2}
                ],
                "selected_option": "A",
                "confidence": round(confidence, 3),
                "reasoning": f"Seleccionada opción A basada en análisis de contexto y experiencia previa",
                "outcome": "successful" if confidence > 0.7 else "partial",
                "processing_time": round(0.1 + (0.3 * (1 - confidence)), 3),
                "hemisphere_influence": {
                    "technical": round(0.4 + (0.4 * confidence), 2),
                    "emotional": round(0.6 - (0.4 * confidence), 2)
                },
                "user_feedback": "positive" if confidence > 0.8 else "neutral",
                "learned_patterns": [f"pattern_{i%5+1}", f"context_{i%3+1}"]
            }
            decisions.append(decision)
        
        return {
            "decisions": decisions,
            "total_count": len(decisions),
            "filters_applied": {
                "limit": limit,
                "decision_type": decision_type,
                "confidence_min": confidence_min
            },
            "summary": {
                "avg_confidence": sum(d["confidence"] for d in decisions) / len(decisions) if decisions else 0,
                "successful_decisions": len([d for d in decisions if d["outcome"] == "successful"]),
                "decision_types_count": len(set(d["decision_type"] for d in decisions))
            }
        }
        
    except Exception as e:
        logger.error(f"Error al obtener historial de decisiones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener historial de decisiones"
        )

@router.post("/experimental")
async def vicky_experimental_analysis(
    analysis_request: Dict[str, Any] = Body(...),
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Realiza análisis experimental con Vicky
    """
    try:
        experiment_type = analysis_request.get("experiment_type", "general")
        data_input = analysis_request.get("data", {})
        parameters = analysis_request.get("parameters", {})
        
        # Validar tipo de experimento
        valid_experiments = [
            "sentiment_analysis", "pattern_recognition", "predictive_modeling",
            "anomaly_detection", "clustering_analysis", "neural_pathway_test",
            "cognitive_load_test", "memory_efficiency", "decision_tree_analysis"
        ]
        
        if experiment_type not in valid_experiments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de experimento no válido. Tipos disponibles: {valid_experiments}"
            )
        
        # Simular análisis experimental
        start_time = time.time()
        
        # Generar resultados basados en el tipo de experimento
        if experiment_type == "sentiment_analysis":
            results = {
                "sentiment_scores": {
                    "positive": 0.65,
                    "negative": 0.15,
                    "neutral": 0.20
                },
                "emotional_indicators": {
                    "joy": 0.45, "sadness": 0.10, "anger": 0.05,
                    "fear": 0.08, "surprise": 0.12, "disgust": 0.03
                },
                "confidence": 0.87
            }
        elif experiment_type == "pattern_recognition":
            results = {
                "patterns_found": 12,
                "pattern_types": ["temporal", "linguistic", "behavioral"],
                "pattern_strength": [0.89, 0.76, 0.82],
                "anomalies_detected": 2,
                "confidence": 0.91
            }
        elif experiment_type == "predictive_modeling":
            results = {
                "prediction_accuracy": 0.84,
                "confidence_intervals": {"lower": 0.78, "upper": 0.90},
                "feature_importance": {
                    "context": 0.35, "history": 0.28, "user_behavior": 0.22, "temporal": 0.15
                },
                "model_performance": {"precision": 0.86, "recall": 0.82, "f1_score": 0.84}
            }
        else:
            # Análisis general
            results = {
                "analysis_completed": True,
                "data_points_processed": len(str(data_input)),
                "insights_generated": 8,
                "recommendations": [
                    "Optimizar balance hemisférico para este tipo de análisis",
                    "Incrementar ventana de contexto para mejor precisión",
                    "Considerar factores temporales en futuras iteraciones"
                ],
                "confidence": 0.79
            }
        
        processing_time = time.time() - start_time
        
        # Crear registro del experimento
        experiment_record = {
            "experiment_id": f"exp_{int(time.time())}",
            "user_id": current_user.id,
            "experiment_type": experiment_type,
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 3),
            "parameters_used": parameters,
            "results": results,
            "vicky_state": {
                "hemisphere_balance": vicky_brain.current_balance.dict(),
                "cognitive_load": 0.45,
                "memory_utilization": 0.67
            }
        }
        
        logger.info(f"Experimento {experiment_type} completado para usuario {current_user.id}")
        
        return {
            "success": True,
            "experiment": experiment_record,
            "insights": {
                "key_findings": f"Análisis {experiment_type} completado con {results.get('confidence', 0.8):.1%} de confianza",
                "recommendations": results.get("recommendations", ["Continuar con análisis similares"]),
                "next_steps": [
                    "Revisar resultados detallados",
                    "Considerar experimentos relacionados",
                    "Aplicar insights a configuración de Vicky"
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en análisis experimental: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error durante el análisis experimental"
        )

