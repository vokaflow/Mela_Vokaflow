#!/usr/bin/env python3
"""
💬 Router de Conversaciones - VokaFlow Enterprise
API completa para gestión de conversaciones y mensajes
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, and_, func

# Importar dependencias del sistema de autenticación
try:
    from ..auth_robust import auth_manager, get_current_user
except ImportError:
    # Fallback si no está disponible
    def get_current_user():
        return {"id": 1, "username": "admin"}

# Importar modelos de mensajería
from ..messaging.models import (
    Conversation, Message, ConversationParticipant,
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse, ParticipantAdd, MessageSearch,
    ConversationType, MessageType, MessageStatus,
    WebSocketMessage, TypingIndicator
)

# Importar base de datos
try:
    from ..database import get_db, SessionLocal
except ImportError:
    # Crear una sesión básica si no está disponible
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    SQLALCHEMY_DATABASE_URL = "sqlite:///./vokaflow_messaging.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# ENDPOINTS DE CONVERSACIONES
# ============================================================================

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva conversación"""
    try:
        # Crear conversación
        db_conversation = Conversation(
            title=conversation.title,
            description=conversation.description,
            type=conversation.type,
            created_by=current_user.get("id", 1),
            msg_metadata=conversation.msg_metadata
        )
        
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        
        # Añadir participantes
        participants_to_add = conversation.participants or [current_user.get("id", 1)]
        if current_user.get("id", 1) not in participants_to_add:
            participants_to_add.append(current_user.get("id", 1))
        
        for user_id in participants_to_add:
            participant = ConversationParticipant(
                conversation_id=db_conversation.id,
                user_id=user_id,
                role="admin" if user_id == current_user.get("id", 1) else "member"
            )
            db.add(participant)
        
        db.commit()
        
        # Preparar respuesta
        response = ConversationResponse(
            id=db_conversation.id,
            title=db_conversation.title,
            description=db_conversation.description,
            type=db_conversation.type,
            created_at=db_conversation.created_at,
            updated_at=db_conversation.updated_at,
            created_by=db_conversation.created_by,
            is_active=db_conversation.is_active,
            metadata=db_conversation.msg_metadata,
            message_count=0,
            participants=participants_to_add
        )
        
        logger.info(f"✅ Conversación creada: {db_conversation.title} (ID: {db_conversation.id})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error creando conversación: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    conversation_type: Optional[ConversationType] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener conversaciones del usuario"""
    try:
        query = db.query(Conversation).join(ConversationParticipant).filter(
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.is_active == True,
            Conversation.is_active == True
        )
        
        if conversation_type:
            query = query.filter(Conversation.type == conversation_type)
        
        conversations = query.order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
        
        results = []
        for conv in conversations:
            # Contar mensajes
            message_count = db.query(func.count(Message.id)).filter(Message.conversation_id == conv.id).scalar()
            
            # Último mensaje
            last_message = db.query(Message).filter(Message.conversation_id == conv.id).order_by(desc(Message.created_at)).first()
            last_message_response = None
            if last_message:
                last_message_response = MessageResponse(
                    id=last_message.id,
                    conversation_id=last_message.conversation_id,
                    user_id=last_message.user_id,
                    content=last_message.content,
                    message_type=last_message.message_type,
                    status=last_message.status,
                    created_at=last_message.created_at,
                    updated_at=last_message.updated_at,
                    reply_to_id=last_message.reply_to_id,
                    metadata=last_message.msg_metadata
                )
            
            # Participantes
            participants = db.query(ConversationParticipant.user_id).filter(
                ConversationParticipant.conversation_id == conv.id,
                ConversationParticipant.is_active == True
            ).all()
            participant_ids = [p.user_id for p in participants]
            
            results.append(ConversationResponse(
                id=conv.id,
                title=conv.title,
                description=conv.description,
                type=conv.type,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                created_by=conv.created_by,
                is_active=conv.is_active,
                metadata=conv.msg_metadata,
                message_count=message_count,
                last_message=last_message_response,
                participants=participant_ids
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo conversaciones: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    include_messages: bool = Query(False),
    message_limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener conversación específica"""
    try:
        # Verificar acceso
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Contar mensajes
        message_count = db.query(func.count(Message.id)).filter(Message.conversation_id == conversation_id).scalar()
        
        # Último mensaje
        last_message = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(desc(Message.created_at)).first()
        last_message_response = None
        if last_message:
            last_message_response = MessageResponse(
                id=last_message.id,
                conversation_id=last_message.conversation_id,
                user_id=last_message.user_id,
                content=last_message.content,
                message_type=last_message.message_type,
                status=last_message.status,
                created_at=last_message.created_at,
                updated_at=last_message.updated_at,
                reply_to_id=last_message.reply_to_id,
                metadata=last_message.msg_metadata
            )
        
        # Participantes
        participants = db.query(ConversationParticipant.user_id).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.is_active == True
        ).all()
        participant_ids = [p.user_id for p in participants]
        
        response = ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            description=conversation.description,
            type=conversation.type,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            created_by=conversation.created_by,
            is_active=conversation.is_active,
            metadata=conversation.msg_metadata,
            message_count=message_count,
            last_message=last_message_response,
            participants=participant_ids
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo conversación {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")

@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar conversación"""
    try:
        # Verificar acceso de admin
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.role.in_(["admin", "moderator"]),
            ConversationParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Actualizar campos
        if conversation_update.title is not None:
            conversation.title = conversation_update.title
        if conversation_update.description is not None:
            conversation.description = conversation_update.description
        if conversation_update.msg_metadata is not None:
            conversation.msg_metadata = conversation_update.msg_metadata
        
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conversation)
        
        return await get_conversation(conversation_id, current_user=current_user, db=db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando conversación {conversation_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {str(e)}")

# ============================================================================
# ENDPOINTS DE MENSAJES
# ============================================================================

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar mensaje a conversación"""
    try:
        # Verificar acceso
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
        # Crear mensaje
        db_message = Message(
            conversation_id=conversation_id,
            user_id=current_user.get("id", 1),
            content=message.content,
            message_type=message.message_type,
            reply_to_id=message.reply_to_id,
            metadata=message.msg_metadata
        )
        
        db.add(db_message)
        
        # Actualizar timestamp de conversación
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_message)
        
        response = MessageResponse(
            id=db_message.id,
            conversation_id=db_message.conversation_id,
            user_id=db_message.user_id,
            content=db_message.content,
            message_type=db_message.message_type,
            status=db_message.status,
            created_at=db_message.created_at,
            updated_at=db_message.updated_at,
            reply_to_id=db_message.reply_to_id,
            metadata=db_message.msg_metadata
        )
        
        logger.info(f"✅ Mensaje enviado: conversación {conversation_id}, mensaje {db_message.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener mensajes de conversación"""
    try:
        # Verificar acceso
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()
        
        results = []
        for msg in messages:
            results.append(MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                user_id=msg.user_id,
                content=msg.content,
                message_type=msg.message_type,
                status=msg.status,
                created_at=msg.created_at,
                updated_at=msg.updated_at,
                reply_to_id=msg.reply_to_id,
                metadata=msg.msg_metadata
            ))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo mensajes: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")

@router.get("/conversations/{conversation_id}/search", response_model=Dict[str, Any])
async def search_messages(
    conversation_id: int,
    query: str = Query(..., min_length=1),
    limit: int = Query(50, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar mensajes en conversación"""
    try:
        # Verificar acceso
        participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.is_active == True
        ).first()
        
        if not participant:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
        # Buscar mensajes
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.content.contains(query)
        ).order_by(desc(Message.created_at)).limit(limit).all()
        
        results = []
        for msg in messages:
            results.append({
                "id": msg.id,
                "content": msg.content,
                "user_id": msg.user_id,
                "created_at": msg.created_at.isoformat(),
                "message_type": msg.message_type.value,
                "relevance_score": 1.0  # Puntuación básica
            })
        
        return {
            "query": query,
            "conversation_id": conversation_id,
            "total_results": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error buscando mensajes: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching messages: {str(e)}")

@router.post("/conversations/{conversation_id}/participants")
async def add_participant(
    conversation_id: int,
    participant_data: ParticipantAdd,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Añadir participante a conversación"""
    try:
        # Verificar permisos de admin
        admin_participant = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.role.in_(["admin", "moderator"]),
            ConversationParticipant.is_active == True
        ).first()
        
        if not admin_participant:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Verificar si ya es participante
        existing = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == participant_data.user_id
        ).first()
        
        if existing:
            if existing.is_active:
                raise HTTPException(status_code=400, detail="User is already a participant")
            else:
                # Reactivar participante
                existing.is_active = True
                existing.role = participant_data.role
                existing.joined_at = datetime.utcnow()
        else:
            # Crear nuevo participante
            new_participant = ConversationParticipant(
                conversation_id=conversation_id,
                user_id=participant_data.user_id,
                role=participant_data.role
            )
            db.add(new_participant)
        
        db.commit()
        
        return {"message": "Participant added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error añadiendo participante: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding participant: {str(e)}")

# ============================================================================
# ENDPOINTS ADICIONALES
# ============================================================================

@router.get("/search/messages", response_model=Dict[str, Any])
async def search_all_messages(
    query: str = Query(..., min_length=1),
    limit: int = Query(50, le=100),
    conversation_type: Optional[ConversationType] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar mensajes en todas las conversaciones del usuario"""
    try:
        # Obtener IDs de conversaciones del usuario
        participant_conversations = db.query(ConversationParticipant.conversation_id).filter(
            ConversationParticipant.user_id == current_user.get("id", 1),
            ConversationParticipant.is_active == True
        ).subquery()
        
        query_builder = db.query(Message, Conversation).join(
            Conversation, Message.conversation_id == Conversation.id
        ).filter(
            Message.conversation_id.in_(participant_conversations),
            Message.content.contains(query),
            Conversation.is_active == True
        )
        
        if conversation_type:
            query_builder = query_builder.filter(Conversation.type == conversation_type)
        
        results_raw = query_builder.order_by(desc(Message.created_at)).limit(limit).all()
        
        results = []
        for msg, conv in results_raw:
            results.append({
                "id": msg.id,
                "content": msg.content,
                "user_id": msg.user_id,
                "created_at": msg.created_at.isoformat(),
                "conversation_id": msg.conversation_id,
                "conversation_title": conv.title,
                "conversation_type": conv.type.value,
                "relevance_score": 1.0
            })
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Error buscando en todos los mensajes: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching messages: {str(e)}")

# Endpoint adicional para compatibilidad con las pruebas
@router.post("/conversations/{conversation_id}/message", response_model=MessageResponse)
async def send_message_compat(
    conversation_id: int,
    message_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint de compatibilidad para envío de mensajes"""
    try:
        # Extraer contenido del mensaje
        content = (
            message_data.get("content") or 
            message_data.get("message") or
            str(message_data)
        )
        
        message = MessageCreate(
            content=content,
            message_type=MessageType.TEXT,
            metadata=message_data.get("metadata", {})
        )
        
        return await send_message(conversation_id, message, current_user, db)
        
    except Exception as e:
        logger.error(f"❌ Error en endpoint de compatibilidad: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

# Endpoints adicionales para compatibilidad
@router.get("/conversations/{conversation_id}/details", response_model=ConversationResponse)
async def get_conversation_details(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de conversación (endpoint de compatibilidad)"""
    return await get_conversation(conversation_id, current_user=current_user, db=db)

@router.get("/conversations/{conversation_id}/history", response_model=List[MessageResponse])
async def get_conversation_history(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener historial de conversación (endpoint de compatibilidad)"""
    return await get_messages(conversation_id, skip, limit, current_user, db)
