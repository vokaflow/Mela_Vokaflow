#!/usr/bin/env python3
"""
⚡ WebSocket Manager - VokaFlow Enterprise
Sistema completo de mensajería en tiempo real
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

# Importar modelos
try:
    from .messaging.models import (
        WebSocketMessage, TypingIndicator, MessageType, 
        Conversation, Message, ConversationParticipant
    )
    from .database import get_db
    from .auth_robust import get_current_user
except ImportError:
    # Fallbacks básicos
    from typing import Dict
    
    class WebSocketMessage:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    def get_db():
        pass

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Gestor de conexiones WebSocket"""
    
    def __init__(self):
        # Conexiones activas: user_id -> List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
        # Conversaciones activas: conversation_id -> Set[user_id]
        self.conversation_participants: Dict[int, Set[int]] = {}
        
        # Estado de escritura: conversation_id -> Set[user_id]
        self.typing_users: Dict[int, Set[int]] = {}
        
        # Metadatos de conexión
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        logger.info("✅ WebSocket ConnectionManager inicializado")
    
    async def connect(self, websocket: WebSocket, user_id: int, metadata: Dict[str, Any] = None):
        """Conectar usuario"""
        try:
            await websocket.accept()
            
            # Agregar conexión
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            
            # Guardar metadatos
            self.connection_metadata[websocket] = {
                "user_id": user_id,
                "connected_at": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            logger.info(f"✅ Usuario {user_id} conectado via WebSocket")
            
            # Notificar conexión
            await self.broadcast_user_status(user_id, "online")
            
        except Exception as e:
            logger.error(f"❌ Error conectando usuario {user_id}: {e}")
            raise
    
    async def disconnect(self, websocket: WebSocket):
        """Desconectar usuario"""
        try:
            if websocket in self.connection_metadata:
                user_id = self.connection_metadata[websocket]["user_id"]
                
                # Remover conexión
                if user_id in self.active_connections:
                    if websocket in self.active_connections[user_id]:
                        self.active_connections[user_id].remove(websocket)
                    
                    # Si no quedan conexiones, remover usuario
                    if not self.active_connections[user_id]:
                        del self.active_connections[user_id]
                        await self.broadcast_user_status(user_id, "offline")
                
                # Limpiar metadatos
                del self.connection_metadata[websocket]
                
                # Limpiar estado de escritura
                self.cleanup_typing_status(user_id)
                
                logger.info(f"✅ Usuario {user_id} desconectado")
            
        except Exception as e:
            logger.error(f"❌ Error desconectando: {e}")
    
    async def send_personal_message(self, message: str, user_id: int):
        """Enviar mensaje personal a usuario"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected.append(websocket)
            
            # Limpiar conexiones muertas
            for ws in disconnected:
                await self.disconnect(ws)
    
    async def send_to_conversation(self, message: str, conversation_id: int, exclude_user: int = None):
        """Enviar mensaje a todos los participantes de una conversación"""
        if conversation_id in self.conversation_participants:
            for user_id in self.conversation_participants[conversation_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                await self.send_personal_message(message, user_id)
    
    async def broadcast_user_status(self, user_id: int, status: str):
        """Notificar cambio de estado de usuario"""
        message = json.dumps({
            "type": "user_status",
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Enviar a todas las conversaciones donde participa el usuario
        for conv_id, participants in self.conversation_participants.items():
            if user_id in participants:
                await self.send_to_conversation(message, conv_id, exclude_user=user_id)
    
    async def join_conversation(self, user_id: int, conversation_id: int):
        """Usuario se une a conversación"""
        if conversation_id not in self.conversation_participants:
            self.conversation_participants[conversation_id] = set()
        
        self.conversation_participants[conversation_id].add(user_id)
        
        # Notificar a otros participantes
        message = json.dumps({
            "type": "user_joined_conversation",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.send_to_conversation(message, conversation_id, exclude_user=user_id)
        logger.info(f"✅ Usuario {user_id} se unió a conversación {conversation_id}")
    
    async def leave_conversation(self, user_id: int, conversation_id: int):
        """Usuario deja conversación"""
        if conversation_id in self.conversation_participants:
            self.conversation_participants[conversation_id].discard(user_id)
            
            # Si no quedan participantes, limpiar conversación
            if not self.conversation_participants[conversation_id]:
                del self.conversation_participants[conversation_id]
                if conversation_id in self.typing_users:
                    del self.typing_users[conversation_id]
        
        # Notificar a otros participantes
        message = json.dumps({
            "type": "user_left_conversation",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.send_to_conversation(message, conversation_id, exclude_user=user_id)
        logger.info(f"✅ Usuario {user_id} dejó conversación {conversation_id}")
    
    async def handle_typing_indicator(self, user_id: int, conversation_id: int, is_typing: bool):
        """Manejar indicador de escritura"""
        if conversation_id not in self.typing_users:
            self.typing_users[conversation_id] = set()
        
        if is_typing:
            self.typing_users[conversation_id].add(user_id)
        else:
            self.typing_users[conversation_id].discard(user_id)
        
        # Notificar a otros participantes
        message = json.dumps({
            "type": "typing_indicator",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.send_to_conversation(message, conversation_id, exclude_user=user_id)
    
    def cleanup_typing_status(self, user_id: int):
        """Limpiar estado de escritura al desconectar"""
        for conv_id in list(self.typing_users.keys()):
            self.typing_users[conv_id].discard(user_id)
            if not self.typing_users[conv_id]:
                del self.typing_users[conv_id]
    
    def get_conversation_status(self, conversation_id: int) -> Dict[str, Any]:
        """Obtener estado de conversación"""
        participants = list(self.conversation_participants.get(conversation_id, []))
        typing_users = list(self.typing_users.get(conversation_id, []))
        
        return {
            "conversation_id": conversation_id,
            "active_participants": participants,
            "typing_users": typing_users,
            "participant_count": len(participants)
        }
    
    def get_user_status(self, user_id: int) -> Dict[str, Any]:
        """Obtener estado de usuario"""
        is_online = user_id in self.active_connections
        connection_count = len(self.active_connections.get(user_id, []))
        
        return {
            "user_id": user_id,
            "is_online": is_online,
            "connection_count": connection_count
        }

# Instancia global del gestor de conexiones
connection_manager = ConnectionManager()

# Router para WebSocket
websocket_router = APIRouter()

@websocket_router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """Endpoint principal de WebSocket para chat"""
    user_id = None
    
    try:
        # Aceptar conexión inicial
        await websocket.accept()
        
        # Esperar mensaje de autenticación
        auth_data = await websocket.receive_text()
        auth_message = json.loads(auth_data)
        
        if auth_message.get("type") != "auth":
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Authentication required",
                "code": "AUTH_REQUIRED"
            }))
            await websocket.close()
            return
        
        # Validar token/credenciales (simplificado)
        user_id = auth_message.get("user_id", 1)  # En producción, validar token
        
        # Conectar usuario
        await connection_manager.connect(websocket, user_id, auth_message.get("metadata"))
        
        # Confirmar autenticación
        await websocket.send_text(json.dumps({
            "type": "auth_success",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Loop principal de mensajes
        while True:
            # Recibir mensaje
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Procesar mensaje según tipo
            await handle_websocket_message(user_id, message_data, websocket)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado para usuario {user_id}")
    except Exception as e:
        logger.error(f"❌ Error en WebSocket: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e),
                "code": "WEBSOCKET_ERROR"
            }))
        except:
            pass
    finally:
        if user_id:
            await connection_manager.disconnect(websocket)

async def handle_websocket_message(user_id: int, message_data: Dict[str, Any], websocket: WebSocket):
    """Procesar mensajes WebSocket"""
    try:
        message_type = message_data.get("type")
        
        if message_type == "join_conversation":
            conversation_id = message_data.get("conversation_id")
            await connection_manager.join_conversation(user_id, conversation_id)
            
            # Confirmar join
            await websocket.send_text(json.dumps({
                "type": "conversation_joined",
                "conversation_id": conversation_id,
                "status": connection_manager.get_conversation_status(conversation_id)
            }))
        
        elif message_type == "leave_conversation":
            conversation_id = message_data.get("conversation_id")
            await connection_manager.leave_conversation(user_id, conversation_id)
            
            # Confirmar leave
            await websocket.send_text(json.dumps({
                "type": "conversation_left",
                "conversation_id": conversation_id
            }))
        
        elif message_type == "typing":
            conversation_id = message_data.get("conversation_id")
            is_typing = message_data.get("is_typing", False)
            await connection_manager.handle_typing_indicator(user_id, conversation_id, is_typing)
        
        elif message_type == "message":
            # Retransmitir mensaje a participantes de la conversación
            conversation_id = message_data.get("conversation_id")
            
            # Agregar metadatos del remitente
            message_data["sender_id"] = user_id
            message_data["timestamp"] = datetime.utcnow().isoformat()
            
            # Enviar a otros participantes
            await connection_manager.send_to_conversation(
                json.dumps(message_data), 
                conversation_id, 
                exclude_user=user_id
            )
        
        elif message_type == "get_conversation_status":
            conversation_id = message_data.get("conversation_id")
            status = connection_manager.get_conversation_status(conversation_id)
            
            await websocket.send_text(json.dumps({
                "type": "conversation_status",
                "data": status
            }))
        
        elif message_type == "ping":
            # Heartbeat
            await websocket.send_text(json.dumps({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }))
        
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "code": "UNKNOWN_MESSAGE_TYPE"
            }))
    
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje WebSocket: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e),
            "code": "MESSAGE_PROCESSING_ERROR"
        }))

# Endpoints HTTP adicionales para WebSocket
@websocket_router.get("/api/websocket/info")
async def websocket_info():
    """Información sobre WebSocket"""
    return {
        "websocket_available": True,
        "endpoint": "/ws/chat",
        "protocol": "WebSocket",
        "features": [
            "Real-time messaging",
            "Typing indicators", 
            "User presence",
            "Conversation management"
        ]
    }

@websocket_router.get("/api/websocket/status")
async def websocket_status():
    """Estado actual de WebSockets"""
    return {
        "active_connections": len(connection_manager.connection_metadata),
        "active_users": len(connection_manager.active_connections),
        "active_conversations": len(connection_manager.conversation_participants),
        "typing_conversations": len(connection_manager.typing_users)
    }

@websocket_router.get("/api/websocket/conversation/{conversation_id}/status")
async def conversation_websocket_status(conversation_id: int):
    """Estado WebSocket de conversación específica"""
    return connection_manager.get_conversation_status(conversation_id)

@websocket_router.get("/api/websocket/user/{user_id}/status")
async def user_websocket_status(user_id: int):
    """Estado WebSocket de usuario específico"""
    return connection_manager.get_user_status(user_id)

# Función para notificar nuevo mensaje via WebSocket
async def notify_new_message(message_data: Dict[str, Any]):
    """Notificar nuevo mensaje a través de WebSocket"""
    try:
        conversation_id = message_data.get("conversation_id")
        sender_id = message_data.get("user_id")
        
        websocket_message = {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": message_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.send_to_conversation(
            json.dumps(websocket_message),
            conversation_id,
            exclude_user=sender_id
        )
        
        logger.info(f"✅ Notificación WebSocket enviada para mensaje en conversación {conversation_id}")
        
    except Exception as e:
        logger.error(f"❌ Error notificando mensaje via WebSocket: {e}")

# Función para notificar cambios en conversación
async def notify_conversation_update(conversation_id: int, update_type: str, data: Dict[str, Any]):
    """Notificar actualizaciones de conversación"""
    try:
        websocket_message = {
            "type": "conversation_update",
            "conversation_id": conversation_id,
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.send_to_conversation(
            json.dumps(websocket_message),
            conversation_id
        )
        
        logger.info(f"✅ Notificación de actualización enviada para conversación {conversation_id}")
        
    except Exception as e:
        logger.error(f"❌ Error notificando actualización de conversación: {e}")

logger.info("✅ WebSocket Manager inicializado con funcionalidad completa") 