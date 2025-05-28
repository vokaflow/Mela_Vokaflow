from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
import random

from ..models.conversations_model import (
    Conversation, ConversationCreate, ConversationUpdate, ConversationSummary,
    Message, MessageCreate, MessageResponse, ConversationResponse,
    ConversationStats, ConversationExport, ConversationSearch,
    ConversationType, ConversationStatus, MessageRole
)

router = APIRouter(tags=["Conversations"])

# Simulación de base de datos en memoria
conversations_db = {
    "conversations": {},
    "user_conversations": {},  # user_id -> [conversation_ids]
    "stats": {
        "total_conversations": 0,
        "total_messages": 0
    }
}

def generate_conversation_id():
    """Generar ID único para conversación"""
    return f"conv_{uuid.uuid4().hex[:12]}"

def generate_message_id():
    """Generar ID único para mensaje"""
    return f"msg_{uuid.uuid4().hex[:8]}"

def get_user_conversations(user_id: str) -> List[str]:
    """Obtener IDs de conversaciones de un usuario"""
    return conversations_db["user_conversations"].get(user_id, [])

def add_user_conversation(user_id: str, conversation_id: str):
    """Agregar conversación a un usuario"""
    if user_id not in conversations_db["user_conversations"]:
        conversations_db["user_conversations"][user_id] = []
    if conversation_id not in conversations_db["user_conversations"][user_id]:
        conversations_db["user_conversations"][user_id].append(conversation_id)

@router.get("/list", response_model=ConversationResponse)
async def list_conversations(
    user_id: str = Query(..., description="ID del usuario"),
    status: Optional[ConversationStatus] = Query(None, description="Filtrar por estado"),
    type: Optional[ConversationType] = Query(None, description="Filtrar por tipo"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de conversaciones"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    include_messages: bool = Query(False, description="Incluir mensajes en la respuesta")
):
    """
    📋 Listar conversaciones del usuario
    
    Obtiene lista de conversaciones:
    - Filtros por estado y tipo
    - Paginación
    - Opción de incluir mensajes
    - Ordenado por última actividad
    """
    try:
        # Generar conversaciones de ejemplo si no existen
        if user_id not in conversations_db["user_conversations"]:
            sample_conversations = []
            for i in range(15):
                conv_id = generate_conversation_id()
                conversation = Conversation(
                    id=conv_id,
                    title=f"Conversación {i+1}",
                    description=f"Descripción de la conversación {i+1}",
                    type=random.choice(list(ConversationType)),
                    status=random.choice(list(ConversationStatus)),
                    user_id=user_id,
                    participants=[user_id],
                    created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                    updated_at=datetime.now() - timedelta(hours=random.randint(0, 72)),
                    message_count=random.randint(1, 50),
                    tags=[f"tag{random.randint(1,5)}" for _ in range(random.randint(0,3))]
                )
                
                # Agregar algunos mensajes de ejemplo
                for j in range(random.randint(1, 5)):
                    msg_id = generate_message_id()
                    message = Message(
                        id=msg_id,
                        role=random.choice([MessageRole.USER, MessageRole.ASSISTANT]),
                        content=f"Mensaje {j+1} en conversación {i+1}",
                        timestamp=datetime.now() - timedelta(hours=random.randint(0, 48))
                    )
                    conversation.messages.append(message)
                
                if conversation.messages:
                    conversation.last_message_at = max(msg.timestamp for msg in conversation.messages)
                
                conversations_db["conversations"][conv_id] = conversation.dict()
                add_user_conversation(user_id, conv_id)
                sample_conversations.append(conversation)
        
        # Obtener conversaciones del usuario
        user_conv_ids = get_user_conversations(user_id)
        user_conversations = []
        
        for conv_id in user_conv_ids:
            if conv_id in conversations_db["conversations"]:
                conv_data = conversations_db["conversations"][conv_id]
                conversation = Conversation(**conv_data)
                
                # Aplicar filtros
                if status and conversation.status != status:
                    continue
                if type and conversation.type != type:
                    continue
                
                # Si no incluir mensajes, crear resumen
                if not include_messages:
                    last_message_preview = None
                    if conversation.messages:
                        last_message_preview = conversation.messages[-1].content[:100] + "..."
                    
                    summary = ConversationSummary(
                        id=conversation.id,
                        title=conversation.title,
                        type=conversation.type,
                        status=conversation.status,
                        message_count=conversation.message_count,
                        last_message_at=conversation.last_message_at,
                        last_message_preview=last_message_preview,
                        unread_count=random.randint(0, 5),
                        created_at=conversation.created_at
                    )
                    user_conversations.append(summary)
                else:
                    user_conversations.append(conversation)
        
        # Ordenar por última actividad
        user_conversations.sort(
            key=lambda x: x.last_message_at or x.created_at, 
            reverse=True
        )
        
        # Aplicar paginación
        total = len(user_conversations)
        paginated_conversations = user_conversations[offset:offset + limit]
        
        return ConversationResponse(
            message=f"Retrieved {len(paginated_conversations)} conversations",
            data={
                "conversations": paginated_conversations,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")

@router.post("/create", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    user_id: str = Query(..., description="ID del usuario creador")
):
    """
    ➕ Crear nueva conversación
    
    Crea una nueva conversación:
    - Asigna ID único
    - Configura participantes
    - Establece configuraciones iniciales
    - Agrega etiquetas
    """
    try:
        conv_id = generate_conversation_id()
        
        # Crear conversación
        conversation = Conversation(
            id=conv_id,
            title=conversation_data.title,
            description=conversation_data.description,
            type=conversation_data.type,
            status=ConversationStatus.ACTIVE,
            user_id=user_id,
            participants=[user_id] + conversation_data.participants,
            settings=conversation_data.settings or {},
            tags=conversation_data.tags
        )
        
        # Guardar en base de datos
        conversations_db["conversations"][conv_id] = conversation.dict()
        add_user_conversation(user_id, conv_id)
        
        # Agregar a participantes
        for participant_id in conversation_data.participants:
            add_user_conversation(participant_id, conv_id)
        
        # Actualizar estadísticas
        conversations_db["stats"]["total_conversations"] += 1
        
        return ConversationResponse(
            message="Conversation created successfully",
            data=conversation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str = Path(..., description="ID de la conversación"),
    user_id: str = Query(..., description="ID del usuario"),
    include_messages: bool = Query(True, description="Incluir mensajes"),
    message_limit: int = Query(50, ge=1, le=200, description="Límite de mensajes")
):
    """
    🔍 Obtener conversación específica
    
    Obtiene detalles completos de una conversación:
    - Validación de permisos
    - Mensajes con paginación
    - Metadatos completos
    - Información de participantes
    """
    try:
        if conversation_id not in conversations_db["conversations"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db["conversations"][conversation_id]
        conversation = Conversation(**conv_data)
        
        # Validar permisos
        if user_id not in conversation.participants:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Limitar mensajes si se solicita
        if include_messages and len(conversation.messages) > message_limit:
            conversation.messages = conversation.messages[-message_limit:]
        elif not include_messages:
            conversation.messages = []
        
        return ConversationResponse(
            message="Conversation retrieved successfully",
            data=conversation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")

@router.post("/{conversation_id}/message", response_model=MessageResponse)
async def send_message(
    conversation_id: str = Path(..., description="ID de la conversación"),
    user_id: str = Query(..., description="ID del usuario"),
    message_data: MessageCreate = Body(..., description="Datos del mensaje")
):
    """
    💬 Enviar mensaje a conversación
    
    Agrega un nuevo mensaje:
    - Validación de permisos
    - Generación de respuesta automática (si es assistant)
    - Actualización de timestamps
    - Conteo de tokens
    """
    try:
        if conversation_id not in conversations_db["conversations"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db["conversations"][conversation_id]
        conversation = Conversation(**conv_data)
        
        # Validar permisos
        if user_id not in conversation.participants:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Crear mensaje
        msg_id = generate_message_id()
        message = Message(
            id=msg_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata or {},
            attachments=message_data.attachments,
            tokens=len(message_data.content.split()) * 1.3  # Estimación simple
        )
        
        # Agregar mensaje a la conversación
        conversation.messages.append(message)
        conversation.message_count += 1
        conversation.last_message_at = message.timestamp
        conversation.updated_at = datetime.now()
        
        # Guardar cambios
        conversations_db["conversations"][conversation_id] = conversation.dict()
        conversations_db["stats"]["total_messages"] += 1
        
        # Generar respuesta automática si es mensaje de usuario
        if message_data.role == MessageRole.USER and conversation.type == ConversationType.CHAT:
            assistant_msg_id = generate_message_id()
            assistant_message = Message(
                id=assistant_msg_id,
                role=MessageRole.ASSISTANT,
                content=f"He recibido tu mensaje: '{message_data.content[:50]}...'. ¿En qué más puedo ayudarte?",
                metadata={"auto_generated": True, "response_to": msg_id}
            )
            
            conversation.messages.append(assistant_message)
            conversation.message_count += 1
            conversation.last_message_at = assistant_message.timestamp
            
            # Guardar con respuesta automática
            conversations_db["conversations"][conversation_id] = conversation.dict()
            conversations_db["stats"]["total_messages"] += 1
        
        return MessageResponse(
            message="Message sent successfully",
            data=message,
            conversation_id=conversation_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.delete("/{conversation_id}", response_model=ConversationResponse)
async def delete_conversation(
    conversation_id: str = Path(..., description="ID de la conversación"),
    user_id: str = Query(..., description="ID del usuario"),
    permanent: bool = Query(False, description="Eliminación permanente")
):
    """
    🗑️ Eliminar conversación
    
    Elimina o archiva una conversación:
    - Validación de permisos (solo propietario)
    - Eliminación suave (archivado) por defecto
    - Opción de eliminación permanente
    - Actualización de estadísticas
    """
    try:
        if conversation_id not in conversations_db["conversations"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db["conversations"][conversation_id]
        conversation = Conversation(**conv_data)
        
        # Validar permisos (solo el propietario puede eliminar)
        if conversation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only the owner can delete this conversation")
        
        if permanent:
            # Eliminación permanente
            del conversations_db["conversations"][conversation_id]
            
            # Remover de todos los usuarios
            for user_conv_list in conversations_db["user_conversations"].values():
                if conversation_id in user_conv_list:
                    user_conv_list.remove(conversation_id)
            
            conversations_db["stats"]["total_conversations"] -= 1
            conversations_db["stats"]["total_messages"] -= conversation.message_count
            
            return ConversationResponse(
                message="Conversation permanently deleted",
                data={"conversation_id": conversation_id, "deleted": True}
            )
        else:
            # Eliminación suave (archivar)
            conversation.status = ConversationStatus.DELETED
            conversation.updated_at = datetime.now()
            conversations_db["conversations"][conversation_id] = conversation.dict()
            
            return ConversationResponse(
                message="Conversation archived",
                data=conversation
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str = Path(..., description="ID de la conversación"),
    user_id: str = Query(..., description="ID del usuario"),
    update_data: ConversationUpdate = Body(..., description="Datos de actualización")
):
    """
    ✏️ Actualizar conversación
    
    Actualiza propiedades de la conversación:
    - Título y descripción
    - Estado y participantes
    - Configuraciones y etiquetas
    - Validación de permisos
    """
    try:
        if conversation_id not in conversations_db["conversations"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv_data = conversations_db["conversations"][conversation_id]
        conversation = Conversation(**conv_data)
        
        # Validar permisos
        if user_id not in conversation.participants:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Solo el propietario puede cambiar ciertos campos
        owner_only_fields = ["participants", "status"]
        if conversation.user_id != user_id:
            for field in owner_only_fields:
                if getattr(update_data, field) is not None:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Only the owner can modify {field}"
                    )
        
        # Aplicar actualizaciones
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(conversation, field, value)
        
        conversation.updated_at = datetime.now()
        
        # Actualizar participantes si se modificaron
        if update_data.participants is not None:
            # Remover conversación de participantes anteriores
            old_participants = set(conv_data["participants"])
            new_participants = set(update_data.participants)
            
            removed_participants = old_participants - new_participants
            added_participants = new_participants - old_participants
            
            for participant_id in removed_participants:
                if participant_id in conversations_db["user_conversations"]:
                    user_convs = conversations_db["user_conversations"][participant_id]
                    if conversation_id in user_convs:
                        user_convs.remove(conversation_id)
            
            for participant_id in added_participants:
                add_user_conversation(participant_id, conversation_id)
        
        # Guardar cambios
        conversations_db["conversations"][conversation_id] = conversation.dict()
        
        return ConversationResponse(
            message="Conversation updated successfully",
            data=conversation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating conversation: {str(e)}")

# Endpoints adicionales útiles

@router.get("/stats/{user_id}", response_model=ConversationResponse)
async def get_conversation_stats(user_id: str):
    """Obtener estadísticas de conversaciones del usuario"""
    try:
        user_conv_ids = get_user_conversations(user_id)
        user_conversations = []
        
        total_messages = 0
        conversations_by_type = {}
        conversations_by_status = {}
        recent_activity = []
        
        for conv_id in user_conv_ids:
            if conv_id in conversations_db["conversations"]:
                conv_data = conversations_db["conversations"][conv_id]
                conversation = Conversation(**conv_data)
                user_conversations.append(conversation)
                
                total_messages += conversation.message_count
                
                # Contar por tipo
                type_str = conversation.type.value
                conversations_by_type[type_str] = conversations_by_type.get(type_str, 0) + 1
                
                # Contar por estado
                status_str = conversation.status.value
                conversations_by_status[status_str] = conversations_by_status.get(status_str, 0) + 1
                
                # Actividad reciente
                if conversation.last_message_at:
                    recent_activity.append({
                        "conversation_id": conversation.id,
                        "title": conversation.title,
                        "last_activity": conversation.last_message_at,
                        "message_count": conversation.message_count
                    })
        
        # Ordenar actividad reciente
        recent_activity.sort(key=lambda x: x["last_activity"], reverse=True)
        recent_activity = recent_activity[:10]  # Top 10
        
        active_conversations = sum(1 for conv in user_conversations if conv.status == ConversationStatus.ACTIVE)
        avg_messages = total_messages / len(user_conversations) if user_conversations else 0
        
        stats = ConversationStats(
            total_conversations=len(user_conversations),
            active_conversations=active_conversations,
            total_messages=total_messages,
            average_messages_per_conversation=avg_messages,
            conversations_by_type=conversations_by_type,
            conversations_by_status=conversations_by_status,
            recent_activity=recent_activity
        )
        
        return ConversationResponse(
            message="Conversation statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation statistics: {str(e)}")
