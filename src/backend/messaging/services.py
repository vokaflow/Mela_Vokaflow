#!/usr/bin/env python3
"""
💼 Servicios de Mensajería - VokaFlow Enterprise
Lógica de negocio para mensajería y conversaciones
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, or_, and_

from .models import (
    Conversation, Message, ConversationParticipant,
    ConversationCreate, ConversationUpdate, MessageCreate,
    ConversationType, MessageType, MessageStatus
)

logger = logging.getLogger(__name__)

class ConversationService:
    """Servicio para gestión de conversaciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, conversation_data: ConversationCreate, created_by: int) -> Conversation:
        """Crear nueva conversación"""
        try:
            # Crear conversación
            conversation = Conversation(
                title=conversation_data.title,
                description=conversation_data.description,
                type=conversation_data.type,
                created_by=created_by,
                metadata=conversation_data.msg_metadata
            )
            
            self.db.add(conversation)
            self.db.flush()  # Para obtener el ID
            
            # Añadir participantes
            participants_to_add = conversation_data.participants or []
            if created_by not in participants_to_add:
                participants_to_add.append(created_by)
            
            for user_id in participants_to_add:
                participant = ConversationParticipant(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role="admin" if user_id == created_by else "member"
                )
                self.db.add(participant)
            
            self.db.commit()
            logger.info(f"✅ Conversación creada: {conversation.title} (ID: {conversation.id})")
            return conversation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creando conversación: {e}")
            raise
    
    def get_user_conversations(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50,
        conversation_type: Optional[ConversationType] = None
    ) -> List[Conversation]:
        """Obtener conversaciones del usuario"""
        try:
            query = self.db.query(Conversation).join(ConversationParticipant).filter(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True,
                Conversation.is_active == True
            )
            
            if conversation_type:
                query = query.filter(Conversation.type == conversation_type)
            
            conversations = query.order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversaciones para usuario {user_id}: {e}")
            raise
    
    def get_conversation_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Obtener conversación por ID (verificando acceso)"""
        try:
            # Verificar acceso del usuario
            participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True
            ).first()
            
            if not participant:
                return None
            
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.is_active == True
            ).first()
            
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo conversación {conversation_id}: {e}")
            raise
    
    def update_conversation(
        self, 
        conversation_id: int, 
        user_id: int, 
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """Actualizar conversación"""
        try:
            # Verificar permisos (admin o moderador)
            participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.role.in_(["admin", "moderator"]),
                ConversationParticipant.is_active == True
            ).first()
            
            if not participant:
                return None
            
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return None
            
            # Aplicar actualizaciones
            if update_data.title is not None:
                conversation.title = update_data.title
            if update_data.description is not None:
                conversation.description = update_data.description
            if update_data.msg_metadata is not None:
                conversation.msg_metadata = update_data.msg_metadata
            
            conversation.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"✅ Conversación {conversation_id} actualizada")
            return conversation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error actualizando conversación {conversation_id}: {e}")
            raise
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Eliminar conversación (soft delete)"""
        try:
            # Verificar permisos (solo admin/creador)
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.created_by == user_id
            ).first()
            
            if not conversation:
                return False
            
            conversation.is_active = False
            conversation.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"✅ Conversación {conversation_id} eliminada")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error eliminando conversación {conversation_id}: {e}")
            raise
    
    def add_participant(self, conversation_id: int, admin_user_id: int, new_user_id: int, role: str = "member") -> bool:
        """Añadir participante a conversación"""
        try:
            # Verificar permisos del admin
            admin_participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == admin_user_id,
                ConversationParticipant.role.in_(["admin", "moderator"]),
                ConversationParticipant.is_active == True
            ).first()
            
            if not admin_participant:
                return False
            
            # Verificar si ya es participante
            existing = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == new_user_id
            ).first()
            
            if existing:
                if existing.is_active:
                    return False  # Ya es participante activo
                else:
                    # Reactivar
                    existing.is_active = True
                    existing.role = role
                    existing.joined_at = datetime.utcnow()
            else:
                # Crear nuevo participante
                new_participant = ConversationParticipant(
                    conversation_id=conversation_id,
                    user_id=new_user_id,
                    role=role
                )
                self.db.add(new_participant)
            
            self.db.commit()
            logger.info(f"✅ Participante {new_user_id} añadido a conversación {conversation_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error añadiendo participante: {e}")
            raise
    
    def remove_participant(self, conversation_id: int, admin_user_id: int, user_to_remove: int) -> bool:
        """Remover participante de conversación"""
        try:
            # Verificar permisos del admin
            admin_participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == admin_user_id,
                ConversationParticipant.role.in_(["admin", "moderator"]),
                ConversationParticipant.is_active == True
            ).first()
            
            if not admin_participant:
                return False
            
            # No permitir que el creador se remueva a sí mismo
            conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation and conversation.created_by == user_to_remove and admin_user_id == user_to_remove:
                return False
            
            # Remover participante
            participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_to_remove
            ).first()
            
            if participant:
                participant.is_active = False
                self.db.commit()
                logger.info(f"✅ Participante {user_to_remove} removido de conversación {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error removiendo participante: {e}")
            raise
    
    def get_conversation_participants(self, conversation_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Obtener participantes de conversación"""
        try:
            # Verificar acceso
            access_check = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True
            ).first()
            
            if not access_check:
                return []
            
            participants = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.is_active == True
            ).all()
            
            result = []
            for p in participants:
                result.append({
                    "user_id": p.user_id,
                    "role": p.role,
                    "joined_at": p.joined_at.isoformat(),
                    "last_read_message_id": p.last_read_message_id
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo participantes: {e}")
            raise

class MessageService:
    """Servicio para gestión de mensajes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_message(
        self, 
        conversation_id: int, 
        user_id: int, 
        message_data: MessageCreate
    ) -> Optional[Message]:
        """Enviar mensaje a conversación"""
        try:
            # Verificar acceso a la conversación
            participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True
            ).first()
            
            if not participant:
                return None
            
            # Crear mensaje
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                content=message_data.content,
                message_type=message_data.message_type,
                reply_to_id=message_data.reply_to_id,
                metadata=message_data.msg_metadata
            )
            
            self.db.add(message)
            self.db.flush()  # Para obtener el ID
            
            # Actualizar timestamp de conversación
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"✅ Mensaje {message.id} enviado a conversación {conversation_id}")
            return message
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error enviando mensaje: {e}")
            raise
    
    def get_conversation_messages(
        self, 
        conversation_id: int, 
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        since_message_id: Optional[int] = None
    ) -> List[Message]:
        """Obtener mensajes de conversación"""
        try:
            # Verificar acceso
            participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True
            ).first()
            
            if not participant:
                return []
            
            query = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            )
            
            # Filtro opcional desde mensaje específico
            if since_message_id:
                query = query.filter(Message.id > since_message_id)
            
            messages = query.order_by(desc(Message.created_at)).offset(skip).limit(limit).all()
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo mensajes: {e}")
            raise
    
    def search_messages(
        self, 
        user_id: int,
        query: str,
        conversation_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Tuple[Message, Conversation]]:
        """Buscar mensajes"""
        try:
            # Obtener conversaciones del usuario
            user_conversations = self.db.query(ConversationParticipant.conversation_id).filter(
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True
            ).subquery()
            
            query_builder = self.db.query(Message, Conversation).join(
                Conversation, Message.conversation_id == Conversation.id
            ).filter(
                Message.conversation_id.in_(user_conversations),
                Message.content.contains(query),
                Conversation.is_active == True
            )
            
            if conversation_id:
                query_builder = query_builder.filter(Message.conversation_id == conversation_id)
            
            results = query_builder.order_by(desc(Message.created_at)).limit(limit).all()
            return results
            
        except Exception as e:
            logger.error(f"❌ Error buscando mensajes: {e}")
            raise
    
    def mark_message_as_read(self, message_id: int, user_id: int) -> bool:
        """Marcar mensaje como leído"""
        try:
            message = self.db.query(Message).filter(Message.id == message_id).first()
            if not message:
                return False
            
            # Verificar acceso a la conversación
            participant = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == message.conversation_id,
                ConversationParticipant.user_id == user_id,
                ConversationParticipant.is_active == True
            ).first()
            
            if not participant:
                return False
            
            # Actualizar último mensaje leído
            participant.last_read_message_id = message_id
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error marcando mensaje como leído: {e}")
            raise
    
    def get_unread_count(self, user_id: int, conversation_id: Optional[int] = None) -> int:
        """Obtener cantidad de mensajes no leídos"""
        try:
            if conversation_id:
                # Mensajes no leídos en conversación específica
                participant = self.db.query(ConversationParticipant).filter(
                    ConversationParticipant.conversation_id == conversation_id,
                    ConversationParticipant.user_id == user_id,
                    ConversationParticipant.is_active == True
                ).first()
                
                if not participant:
                    return 0
                
                query = self.db.query(func.count(Message.id)).filter(
                    Message.conversation_id == conversation_id,
                    Message.user_id != user_id  # No contar propios mensajes
                )
                
                if participant.last_read_message_id:
                    query = query.filter(Message.id > participant.last_read_message_id)
                
                return query.scalar() or 0
            else:
                # Total de mensajes no leídos en todas las conversaciones
                user_conversations = self.db.query(ConversationParticipant).filter(
                    ConversationParticipant.user_id == user_id,
                    ConversationParticipant.is_active == True
                ).all()
                
                total_unread = 0
                for participant in user_conversations:
                    conv_unread = self.get_unread_count(user_id, participant.conversation_id)
                    total_unread += conv_unread
                
                return total_unread
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo mensajes no leídos: {e}")
            return 0
    
    def update_message_status(self, message_id: int, status: MessageStatus) -> bool:
        """Actualizar estado de mensaje"""
        try:
            message = self.db.query(Message).filter(Message.id == message_id).first()
            if not message:
                return False
            
            message.status = status
            message.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error actualizando estado de mensaje: {e}")
            raise

class NotificationService:
    """Servicio para notificaciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def notify_new_message(self, message: Message):
        """Notificar nuevo mensaje"""
        try:
            # Importar aquí para evitar importación circular
            from ..websocket_manager import notify_new_message
            
            message_data = {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "user_id": message.user_id,
                "content": message.content,
                "message_type": message.message_type.value,
                "created_at": message.created_at.isoformat()
            }
            
            await notify_new_message(message_data)
            
        except Exception as e:
            logger.error(f"❌ Error notificando nuevo mensaje: {e}")
    
    async def notify_conversation_update(self, conversation_id: int, update_type: str, data: Dict[str, Any]):
        """Notificar actualización de conversación"""
        try:
            from ..websocket_manager import notify_conversation_update
            await notify_conversation_update(conversation_id, update_type, data)
            
        except Exception as e:
            logger.error(f"❌ Error notificando actualización de conversación: {e}")

# Funciones de utilidad
def get_conversation_service(db: Session) -> ConversationService:
    """Factory para ConversationService"""
    return ConversationService(db)

def get_message_service(db: Session) -> MessageService:
    """Factory para MessageService"""
    return MessageService(db)

def get_notification_service(db: Session) -> NotificationService:
    """Factory para NotificationService"""
    return NotificationService(db)

logger.info("✅ Servicios de mensajería inicializados") 