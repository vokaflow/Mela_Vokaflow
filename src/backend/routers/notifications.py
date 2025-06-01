from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
import json
import uuid
from datetime import datetime, timedelta
import random

from ..models.notifications_model import (
    Notification, NotificationCreate, NotificationSend, NotificationUpdate,
    NotificationSettings, NotificationPreferences, NotificationTemplate,
    NotificationStats, NotificationResponse, BulkNotificationResult,
    NotificationType, NotificationPriority, NotificationChannel, NotificationStatus
)

router = APIRouter(tags=["Notifications"])

# Simulación de base de datos en memoria
notifications_db = {
    "notifications": {},
    "settings": {},
    "templates": {},
    "stats": {
        "total_sent": 0,
        "total_delivered": 0,
        "total_read": 0,
        "total_failed": 0
    }
}

def generate_notification_id():
    """Generar ID único para notificación"""
    return f"notif_{uuid.uuid4().hex[:8]}"

def simulate_notification_delivery(notification_id: str, channel: NotificationChannel):
    """Simular entrega de notificación"""
    import time
    time.sleep(random.uniform(0.1, 0.5))  # Simular latencia
    
    # Simular éxito/fallo de entrega
    success_rate = 0.95 if channel == NotificationChannel.IN_APP else 0.85
    return random.random() < success_rate

@router.get("/list", response_model=NotificationResponse)
async def list_notifications(
    user_id: Optional[str] = Query(None, description="ID del usuario"),
    type: Optional[NotificationType] = Query(None, description="Filtrar por tipo"),
    status: Optional[NotificationStatus] = Query(None, description="Filtrar por estado"),
    priority: Optional[NotificationPriority] = Query(None, description="Filtrar por prioridad"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de notificaciones"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    unread_only: bool = Query(False, description="Solo notificaciones no leídas")
):
    """
    📋 Listar notificaciones
    
    Obtiene lista de notificaciones con filtros:
    - Por usuario
    - Por tipo (info, warning, error, etc.)
    - Por estado (pending, sent, read, etc.)
    - Por prioridad
    - Solo no leídas
    """
    try:
        # Generar notificaciones de ejemplo si no existen
        if not notifications_db["notifications"]:
            sample_notifications = []
            for i in range(50):
                notif_id = generate_notification_id()
                notification = Notification(
                    id=notif_id,
                    title=f"Notificación {i+1}",
                    message=f"Este es el mensaje de la notificación {i+1}",
                    type=random.choice(list(NotificationType)),
                    priority=random.choice(list(NotificationPriority)),
                    channel=random.choice(list(NotificationChannel)),
                    status=random.choice(list(NotificationStatus)),
                    user_id=f"user_{random.randint(1, 10)}",
                    created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                    sent_at=datetime.now() - timedelta(days=random.randint(0, 29)) if random.random() > 0.3 else None,
                    read_at=datetime.now() - timedelta(days=random.randint(0, 28)) if random.random() > 0.5 else None
                )
                notifications_db["notifications"][notif_id] = notification.dict()
                sample_notifications.append(notification)
        
        # Filtrar notificaciones
        filtered_notifications = []
        for notif_data in notifications_db["notifications"].values():
            notification = Notification(**notif_data)
            
            # Aplicar filtros
            if user_id and notification.user_id != user_id:
                continue
            if type and notification.type != type:
                continue
            if status and notification.status != status:
                continue
            if priority and notification.priority != priority:
                continue
            if unread_only and notification.read_at is not None:
                continue
            
            filtered_notifications.append(notification)
        
        # Ordenar por fecha de creación (más recientes primero)
        filtered_notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginación
        total = len(filtered_notifications)
        paginated_notifications = filtered_notifications[offset:offset + limit]
        
        return NotificationResponse(
            message=f"Retrieved {len(paginated_notifications)} notifications",
            data={
                "notifications": paginated_notifications,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notifications: {str(e)}")

@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    notification_data: NotificationSend,
    background_tasks: BackgroundTasks
):
    """
    📤 Enviar notificación
    
    Envía notificaciones a múltiples destinatarios:
    - Soporte para múltiples canales
    - Envío inmediato o programado
    - Procesamiento en background
    - Seguimiento de entrega
    """
    try:
        results = []
        failed_recipients = []
        
        for recipient in notification_data.recipients:
            for channel in notification_data.channels:
                notif_id = generate_notification_id()
                
                notification = Notification(
                    id=notif_id,
                    title=notification_data.title,
                    message=notification_data.message,
                    type=notification_data.type,
                    priority=notification_data.priority,
                    channel=channel,
                    status=NotificationStatus.PENDING,
                    user_id=recipient,
                    metadata=notification_data.msg_metadata,
                    expires_at=datetime.now() + timedelta(days=7)  # Expira en 7 días
                )
                
                # Guardar notificación
                notifications_db["notifications"][notif_id] = notification.dict()
                
                # Programar envío
                if notification_data.schedule_at:
                    # En un sistema real, esto se programaría
                    notification.status = NotificationStatus.PENDING
                else:
                    # Envío inmediato en background
                    def send_notification_task(notif_id, channel, recipient):
                        success = simulate_notification_delivery(notif_id, channel)
                        if success:
                            notifications_db["notifications"][notif_id]["status"] = NotificationStatus.SENT
                            notifications_db["notifications"][notif_id]["sent_at"] = datetime.now().isoformat()
                            notifications_db["stats"]["total_sent"] += 1
                        else:
                            notifications_db["notifications"][notif_id]["status"] = NotificationStatus.FAILED
                            notifications_db["stats"]["total_failed"] += 1
                            failed_recipients.append(recipient)
                    
                    background_tasks.add_task(send_notification_task, notif_id, channel, recipient)
                
                results.append({
                    "notification_id": notif_id,
                    "recipient": recipient,
                    "channel": channel,
                    "status": "queued"
                })
        
        bulk_result = BulkNotificationResult(
            total_requested=len(notification_data.recipients) * len(notification_data.channels),
            total_sent=len(results),
            total_failed=0,  # Se actualizará en background
            failed_recipients=[],
            errors=[]
        )
        
        return NotificationResponse(
            message="Notifications queued for sending",
            data={
                "bulk_result": bulk_result,
                "notifications": results
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending notifications: {str(e)}")

@router.put("/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_ids: List[str] = Query(..., description="IDs de notificaciones a marcar como leídas"),
    user_id: Optional[str] = Query(None, description="ID del usuario (para validación)")
):
    """
    ✅ Marcar notificaciones como leídas
    
    Marca una o múltiples notificaciones como leídas:
    - Actualiza timestamp de lectura
    - Valida permisos de usuario
    - Actualiza estadísticas
    """
    try:
        updated_notifications = []
        not_found = []
        
        for notif_id in notification_ids:
            if notif_id not in notifications_db["notifications"]:
                not_found.append(notif_id)
                continue
            
            notification_data = notifications_db["notifications"][notif_id]
            
            # Validar permisos si se proporciona user_id
            if user_id and notification_data.get("user_id") != user_id:
                continue
            
            # Marcar como leída si no estaba leída
            if not notification_data.get("read_at"):
                notification_data["read_at"] = datetime.now().isoformat()
                notification_data["status"] = NotificationStatus.READ
                notifications_db["stats"]["total_read"] += 1
            
            updated_notifications.append(notif_id)
        
        return NotificationResponse(
            message=f"Marked {len(updated_notifications)} notifications as read",
            data={
                "updated": updated_notifications,
                "not_found": not_found,
                "total_updated": len(updated_notifications)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notifications as read: {str(e)}")

@router.delete("/delete", response_model=NotificationResponse)
async def delete_notifications(
    notification_ids: List[str] = Query(..., description="IDs de notificaciones a eliminar"),
    user_id: Optional[str] = Query(None, description="ID del usuario (para validación)"),
    force: bool = Query(False, description="Forzar eliminación sin validaciones")
):
    """
    🗑️ Eliminar notificaciones
    
    Elimina notificaciones del sistema:
    - Validación de permisos
    - Eliminación en lote
    - Opción de forzar eliminación
    - Actualización de estadísticas
    """
    try:
        deleted_notifications = []
        not_found = []
        permission_denied = []
        
        for notif_id in notification_ids:
            if notif_id not in notifications_db["notifications"]:
                not_found.append(notif_id)
                continue
            
            notification_data = notifications_db["notifications"][notif_id]
            
            # Validar permisos si no es forzado
            if not force and user_id and notification_data.get("user_id") != user_id:
                permission_denied.append(notif_id)
                continue
            
            # Eliminar notificación
            del notifications_db["notifications"][notif_id]
            deleted_notifications.append(notif_id)
        
        return NotificationResponse(
            message=f"Deleted {len(deleted_notifications)} notifications",
            data={
                "deleted": deleted_notifications,
                "not_found": not_found,
                "permission_denied": permission_denied,
                "total_deleted": len(deleted_notifications)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notifications: {str(e)}")

@router.put("/settings", response_model=NotificationResponse)
async def update_notification_settings(
    settings: NotificationSettings
):
    """
    ⚙️ Configurar preferencias de notificaciones
    
    Actualiza configuración de notificaciones:
    - Canales habilitados/deshabilitados
    - Tipos de notificación permitidos
    - Horarios silenciosos
    - Umbral de prioridad
    - Zona horaria
    """
    try:
        # Validar horarios silenciosos
        if settings.quiet_hours_start and settings.quiet_hours_end:
            try:
                start_time = datetime.strptime(settings.quiet_hours_start, "%H:%M")
                end_time = datetime.strptime(settings.quiet_hours_end, "%H:%M")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid time format. Use HH:MM format for quiet hours"
                )
        
        # Guardar configuración
        notifications_db["settings"][settings.user_id] = settings.dict()
        
        # Crear preferencias adicionales
        preferences = NotificationPreferences(
            frequency="immediate" if settings.priority_threshold == NotificationPriority.LOW else "digest",
            digest_enabled=not settings.in_app_enabled,
            language="es",
            sound_enabled=settings.push_enabled
        )
        
        return NotificationResponse(
            message="Notification settings updated successfully",
            data={
                "settings": settings,
                "preferences": preferences,
                "updated_at": datetime.now()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification settings: {str(e)}")

# Endpoints adicionales útiles

@router.get("/settings/{user_id}", response_model=NotificationResponse)
async def get_notification_settings(user_id: str):
    """Obtener configuración de notificaciones de un usuario"""
    try:
        if user_id not in notifications_db["settings"]:
            # Crear configuración por defecto
            default_settings = NotificationSettings(user_id=user_id)
            notifications_db["settings"][user_id] = default_settings.dict()
        
        settings = NotificationSettings(**notifications_db["settings"][user_id])
        
        return NotificationResponse(
            message="Notification settings retrieved successfully",
            data=settings
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notification settings: {str(e)}")

@router.get("/stats", response_model=NotificationResponse)
async def get_notification_statistics(
    user_id: Optional[str] = Query(None, description="ID del usuario"),
    days: int = Query(30, ge=1, le=365, description="Días para estadísticas")
):
    """Obtener estadísticas de notificaciones"""
    try:
        # Calcular estadísticas
        total_notifications = len(notifications_db["notifications"])
        
        # Filtrar por usuario si se especifica
        user_notifications = []
        if user_id:
            user_notifications = [
                notif for notif in notifications_db["notifications"].values()
                if notif.get("user_id") == user_id
            ]
            total_notifications = len(user_notifications)
        
        # Estadísticas por canal y tipo
        by_channel = {}
        by_type = {}
        
        notifications_to_analyze = user_notifications if user_id else notifications_db["notifications"].values()
        
        for notif in notifications_to_analyze:
            channel = notif.get("channel", "unknown")
            notif_type = notif.get("type", "unknown")
            
            by_channel[channel] = by_channel.get(channel, 0) + 1
            by_type[notif_type] = by_type.get(notif_type, 0) + 1
        
        stats = NotificationStats(
            total_sent=notifications_db["stats"]["total_sent"],
            total_delivered=notifications_db["stats"]["total_sent"] - notifications_db["stats"]["total_failed"],
            total_read=notifications_db["stats"]["total_read"],
            total_failed=notifications_db["stats"]["total_failed"],
            delivery_rate=95.5,  # Simulado
            read_rate=78.3,      # Simulado
            by_channel=by_channel,
            by_type=by_type
        )
        
        return NotificationResponse(
            message="Notification statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notification statistics: {str(e)}")

@router.get("/unread-count/{user_id}", response_model=NotificationResponse)
async def get_unread_count(user_id: str):
    """Obtener número de notificaciones no leídas"""
    try:
        unread_count = 0
        for notif in notifications_db["notifications"].values():
            if (notif.get("user_id") == user_id and 
                not notif.get("read_at") and 
                notif.get("status") in [NotificationStatus.SENT, NotificationStatus.DELIVERED]):
                unread_count += 1
        
        return NotificationResponse(
            message="Unread count retrieved successfully",
            data={"unread_count": unread_count}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving unread count: {str(e)}")
