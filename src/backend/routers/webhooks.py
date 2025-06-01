from fastapi import APIRouter, HTTPException, Depends, Query, Path, BackgroundTasks
from typing import List, Dict, Any, Optional
import uuid
import random
import json
import hmac
import hashlib
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta

from ..models.webhooks_model import (
    WebhookCreate, Webhook, WebhookUpdate, WebhookDelivery, WebhookTest,
    WebhookTestResult, WebhookResponse, WebhookStats, WebhookEventPayload,
    WebhookEvent, WebhookStatus, WebhookMethod, WebhookDeliveryStatus,
    WebhookFilter, WebhookSecurityConfig
)

router = APIRouter(tags=["Webhooks"])

# Simulación de base de datos en memoria
webhooks_db = {
    "webhooks": {},
    "deliveries": [],
    "events": []
}

def generate_webhook_signature(payload: str, secret: str, timestamp: str) -> str:
    """Genera una firma HMAC para el webhook"""
    message = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def create_sample_payload(event_type: WebhookEvent) -> Dict[str, Any]:
    """Crea un payload de ejemplo para un tipo de evento"""
    base_payload = {
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "event_type": event_type.value,
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "source": "vokaflow_api",
            "version": "1.0"
        }
    }
    
    # Datos específicos por tipo de evento
    if event_type == WebhookEvent.USER_CREATED:
        base_payload["data"] = {
            "user_id": f"user_{random.randint(1000, 9999)}",
            "username": f"user{random.randint(100, 999)}",
            "email": f"user{random.randint(100, 999)}@example.com",
            "created_at": datetime.now().isoformat()
        }
    elif event_type == WebhookEvent.TRANSLATION_COMPLETED:
        base_payload["data"] = {
            "translation_id": f"trans_{uuid.uuid4().hex[:8]}",
            "source_text": "Hello world",
            "translated_text": "Hola mundo",
            "source_lang": "en",
            "target_lang": "es",
            "confidence": 0.95,
            "processing_time": 0.25
        }
    elif event_type == WebhookEvent.TTS_COMPLETED:
        base_payload["data"] = {
            "tts_id": f"tts_{uuid.uuid4().hex[:8]}",
            "text": "Hello, this is a test",
            "voice": "female_voice_1",
            "language": "en",
            "audio_url": f"https://api.vokaflow.com/audio/{uuid.uuid4().hex}.mp3",
            "duration": 2.5
        }
    elif event_type == WebhookEvent.SYSTEM_ALERT:
        base_payload["data"] = {
            "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "title": "System Alert",
            "message": "High CPU usage detected",
            "component": "api_server",
            "metrics": {
                "cpu_usage": random.uniform(80, 95),
                "memory_usage": random.uniform(70, 90)
            }
        }
    else:
        base_payload["data"] = {
            "resource_id": f"res_{uuid.uuid4().hex[:8]}",
            "action": "created",
            "timestamp": datetime.now().isoformat()
        }
    
    return base_payload

def initialize_sample_webhooks():
    """Inicializa webhooks de ejemplo si la base de datos está vacía"""
    if not webhooks_db["webhooks"]:
        # Crear algunos webhooks de ejemplo
        sample_events = [
            [WebhookEvent.USER_CREATED, WebhookEvent.USER_UPDATED],
            [WebhookEvent.TRANSLATION_COMPLETED],
            [WebhookEvent.TTS_COMPLETED, WebhookEvent.STT_COMPLETED],
            [WebhookEvent.SYSTEM_ALERT],
            [WebhookEvent.FILE_UPLOADED, WebhookEvent.VOICE_SAMPLE_CREATED]
        ]
        
        sample_urls = [
            "https://api.example.com/webhooks/users",
            "https://webhook.site/unique-id-1",
            "https://myapp.com/api/webhooks/vokaflow",
            "https://alerts.company.com/webhooks",
            "https://integration.service.com/webhook"
        ]
        
        for i in range(5):
            webhook_id = f"wh_{uuid.uuid4().hex[:8]}"
            
            webhook = Webhook(
                id=webhook_id,
                name=f"Webhook {i+1}",
                url=sample_urls[i],
                events=sample_events[i],
                method=WebhookMethod.POST,
                headers={
                    "Authorization": f"Bearer token_{i+1}",
                    "Content-Type": "application/json",
                    "X-API-Key": f"key_{uuid.uuid4().hex[:16]}"
                },
                secret=f"webhook_secret_{uuid.uuid4().hex[:16]}",
                timeout=30,
                retry_attempts=3,
                retry_delay=60,
                status=WebhookStatus.ACTIVE if random.random() > 0.2 else WebhookStatus.INACTIVE,
                created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                updated_at=datetime.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.5 else None,
                last_triggered_at=datetime.now() - timedelta(hours=random.randint(1, 168)) if random.random() > 0.3 else None,
                total_deliveries=random.randint(0, 500),
                successful_deliveries=random.randint(0, 450),
                failed_deliveries=random.randint(0, 50),
                user_id=f"user_{random.randint(1, 10)}",
                metadata={
                    "created_by": "api",
                    "environment": random.choice(["development", "staging", "production"]),
                    "project": f"project_{random.randint(1, 5)}"
                }
            )
            
            webhooks_db["webhooks"][webhook_id] = webhook.dict()
    
    # Generar entregas de ejemplo
    if len(webhooks_db["deliveries"]) < 50:
        generate_sample_deliveries()

def generate_sample_deliveries():
    """Genera entregas de ejemplo para los webhooks"""
    if not webhooks_db["webhooks"]:
        return
    
    webhook_ids = list(webhooks_db["webhooks"].keys())
    events = list(WebhookEvent)
    statuses = list(WebhookDeliveryStatus)
    
    for _ in range(50):
        webhook_id = random.choice(webhook_ids)
        event_type = random.choice(events)
        
        delivery = WebhookDelivery(
            id=f"del_{uuid.uuid4().hex[:8]}",
            webhook_id=webhook_id,
            event_type=event_type,
            payload=create_sample_payload(event_type),
            status=random.choice(statuses),
            http_status=random.choice([200, 201, 400, 401, 403, 404, 500, 502, 503]) if random.random() > 0.1 else None,
            response_body='{"success": true}' if random.random() > 0.3 else '{"error": "Internal server error"}',
            response_headers={"Content-Type": "application/json", "Server": "nginx/1.18.0"},
            attempt_count=random.randint(1, 3),
            duration_ms=random.randint(50, 5000),
            error_message=None if random.random() > 0.3 else "Connection timeout",
            created_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
            delivered_at=datetime.now() - timedelta(hours=random.randint(0, 167)) if random.random() > 0.2 else None,
            next_retry_at=datetime.now() + timedelta(minutes=random.randint(1, 60)) if random.random() > 0.7 else None
        )
        
        webhooks_db["deliveries"].append(delivery.dict())

async def send_webhook_request(webhook: Webhook, payload: Dict[str, Any]) -> WebhookTestResult:
    """Envía una petición de webhook real"""
    try:
        # Preparar headers
        headers = webhook.headers.copy() if webhook.headers else {}
        headers["Content-Type"] = "application/json"
        
        # Agregar firma si hay secreto
        if webhook.secret:
            timestamp = str(int(time.time()))
            payload_str = json.dumps(payload, separators=(',', ':'))
            signature = generate_webhook_signature(payload_str, webhook.secret, timestamp)
            headers["X-Webhook-Signature"] = signature
            headers["X-Webhook-Timestamp"] = timestamp
        
        # Medir tiempo de inicio
        start_time = time.time()
        
        # Realizar petición HTTP
        timeout = aiohttp.ClientTimeout(total=webhook.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method=webhook.method.value,
                url=str(webhook.url),
                json=payload,
                headers=headers
            ) as response:
                duration_ms = int((time.time() - start_time) * 1000)
                response_body = await response.text()
                response_headers = dict(response.headers)
                
                return WebhookTestResult(
                    success=200 <= response.status < 300,
                    http_status=response.status,
                    response_body=response_body,
                    response_headers=response_headers,
                    duration_ms=duration_ms,
                    payload_sent=payload,
                    error_message=None if 200 <= response.status < 300 else f"HTTP {response.status}"
                )
    
    except asyncio.TimeoutError:
        duration_ms = webhook.timeout * 1000
        return WebhookTestResult(
            success=False,
            http_status=0,
            response_body="",
            response_headers={},
            duration_ms=duration_ms,
            payload_sent=payload,
            error_message="Request timeout"
        )
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        return WebhookTestResult(
            success=False,
            http_status=0,
            response_body="",
            response_headers={},
            duration_ms=duration_ms,
            payload_sent=payload,
            error_message=str(e)
        )

@router.get("/list", response_model=WebhookResponse)
async def list_webhooks(
    status: Optional[WebhookStatus] = Query(None, description="Filtrar por estado"),
    event_type: Optional[WebhookEvent] = Query(None, description="Filtrar por tipo de evento"),
    search: Optional[str] = Query(None, description="Buscar en nombre o URL"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    🪝 Lista todos los webhooks
    
    Devuelve una lista paginada de webhooks con opciones de filtrado.
    Incluye estadísticas de entrega y estado de cada webhook.
    """
    try:
        initialize_sample_webhooks()
        
        # Filtrar webhooks
        filtered_webhooks = []
        for webhook_data in webhooks_db["webhooks"].values():
            webhook = Webhook(**webhook_data)
            
            # Aplicar filtros
            if status and webhook.status != status:
                continue
            if event_type and event_type not in webhook.events:
                continue
            if search and search.lower() not in webhook.name.lower() and search.lower() not in str(webhook.url).lower():
                continue
            
            filtered_webhooks.append(webhook)
        
        # Ordenar por fecha de creación (más recientes primero)
        filtered_webhooks.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginación
        total_filtered = len(filtered_webhooks)
        paginated_webhooks = filtered_webhooks[offset:offset + limit]
        
        # Agregar estadísticas de entrega para cada webhook
        webhooks_with_stats = []
        for webhook in paginated_webhooks:
            # Calcular estadísticas de entrega
            webhook_deliveries = [d for d in webhooks_db["deliveries"] if d["webhook_id"] == webhook.id]
            
            success_rate = 0
            if webhook.total_deliveries > 0:
                success_rate = (webhook.successful_deliveries / webhook.total_deliveries) * 100
            
            avg_response_time = 0
            if webhook_deliveries:
                response_times = [d["duration_ms"] for d in webhook_deliveries if d["duration_ms"]]
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
            
            webhook_dict = webhook.dict()
            webhook_dict["success_rate"] = round(success_rate, 2)
            webhook_dict["avg_response_time"] = round(avg_response_time, 2)
            webhook_dict["recent_deliveries_count"] = len([d for d in webhook_deliveries if 
                datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")) > datetime.now() - timedelta(days=7)])
            
            webhooks_with_stats.append(webhook_dict)
        
        # Estadísticas globales
        total_webhooks = len(webhooks_db["webhooks"])
        active_webhooks = len([w for w in webhooks_db["webhooks"].values() if w["status"] == "active"])
        
        return WebhookResponse(
            message=f"Retrieved {len(paginated_webhooks)} webhooks",
            data={
                "webhooks": webhooks_with_stats,
                "total": total_filtered,
                "total_webhooks": total_webhooks,
                "active_webhooks": active_webhooks,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_filtered
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving webhooks: {str(e)}")

@router.post("/create", response_model=WebhookResponse, status_code=201)
async def create_webhook(webhook_create: WebhookCreate):
    """
    🪝 Crear un nuevo webhook
    
    Crea un nuevo webhook con la configuración especificada.
    El webhook se activará automáticamente para los eventos seleccionados.
    """
    try:
        # Generar ID único
        webhook_id = f"wh_{uuid.uuid4().hex[:8]}"
        
        # Crear objeto webhook
        webhook = Webhook(
            id=webhook_id,
            name=webhook_create.name,
            url=webhook_create.url,
            events=webhook_create.events,
            method=webhook_create.method,
            headers=webhook_create.headers,
            secret=webhook_create.secret,
            timeout=webhook_create.timeout,
            retry_attempts=webhook_create.retry_attempts,
            retry_delay=webhook_create.retry_delay,
            status=WebhookStatus.ACTIVE if webhook_create.active else WebhookStatus.INACTIVE,
            created_at=datetime.now(),
            updated_at=None,
            last_triggered_at=None,
            total_deliveries=0,
            successful_deliveries=0,
            failed_deliveries=0,
            user_id="current_user_id",  # En producción sería el usuario actual
            metadata=webhook_create.msg_metadata or {
                "created_by": "api",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Guardar en la base de datos
        webhooks_db["webhooks"][webhook_id] = webhook.dict()
        
        return WebhookResponse(
            message="Webhook created successfully",
            data={
                "webhook": webhook,
                "events_subscribed": len(webhook.events),
                "status": "active" if webhook_create.active else "inactive"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating webhook: {str(e)}")

@router.delete("/{webhook_id}", response_model=WebhookResponse)
async def delete_webhook(webhook_id: str = Path(..., description="ID del webhook a eliminar")):
    """
    🗑️ Eliminar webhook
    
    Elimina permanentemente un webhook y todos sus datos de entrega asociados.
    Esta acción no puede deshacerse.
    """
    try:
        # Verificar que el webhook existe
        if webhook_id not in webhooks_db["webhooks"]:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Obtener datos del webhook antes de eliminarlo
        webhook_data = webhooks_db["webhooks"][webhook_id]
        webhook = Webhook(**webhook_data)
        
        # Contar entregas asociadas
        associated_deliveries = len([d for d in webhooks_db["deliveries"] if d["webhook_id"] == webhook_id])
        
        # Eliminar el webhook
        del webhooks_db["webhooks"][webhook_id]
        
        # Eliminar entregas asociadas
        webhooks_db["deliveries"] = [d for d in webhooks_db["deliveries"] if d["webhook_id"] != webhook_id]
        
        return WebhookResponse(
            message="Webhook deleted successfully",
            data={
                "deleted_webhook": webhook,
                "deleted_at": datetime.now(),
                "deliveries_deleted": associated_deliveries
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting webhook: {str(e)}")

@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_update: WebhookUpdate,
    webhook_id: str = Path(..., description="ID del webhook a actualizar")
):
    """
    ✏️ Actualizar webhook
    
    Actualiza la configuración de un webhook existente.
    Los cambios se aplicarán a las próximas entregas.
    """
    try:
        # Verificar que el webhook existe
        if webhook_id not in webhooks_db["webhooks"]:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Obtener datos actuales
        webhook_data = webhooks_db["webhooks"][webhook_id]
        
        # Aplicar actualizaciones
        update_dict = webhook_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                webhook_data[field] = value
        
        # Actualizar timestamp
        webhook_data["updated_at"] = datetime.now().isoformat()
        
        # Actualizar estado si se cambió active
        if "active" in update_dict:
            webhook_data["status"] = WebhookStatus.ACTIVE if update_dict["active"] else WebhookStatus.INACTIVE
        
        # Guardar cambios
        webhooks_db["webhooks"][webhook_id] = webhook_data
        
        # Obtener webhook actualizado
        updated_webhook = Webhook(**webhook_data)
        
        return WebhookResponse(
            message="Webhook updated successfully",
            data={
                "webhook": updated_webhook,
                "updated_fields": list(update_dict.keys()),
                "updated_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating webhook: {str(e)}")

@router.post("/test", response_model=WebhookResponse)
async def test_webhook(webhook_test: WebhookTest, background_tasks: BackgroundTasks):
    """
    🧪 Probar webhook
    
    Envía una petición de prueba a un webhook para verificar su funcionamiento.
    Puede probar un webhook existente o una URL personalizada.
    """
    try:
        # Si se especifica un webhook_id, usar su configuración
        if webhook_test.webhook_id:
            if webhook_test.webhook_id not in webhooks_db["webhooks"]:
                raise HTTPException(status_code=404, detail="Webhook not found")
            
            webhook_data = webhooks_db["webhooks"][webhook_test.webhook_id]
            webhook = Webhook(**webhook_data)
            
            # Usar configuración del webhook existente
            test_url = webhook.url
            test_method = webhook.method
            test_headers = webhook.headers
            test_timeout = webhook.timeout
        else:
            # Usar configuración de la petición de prueba
            test_url = webhook_test.url
            test_method = webhook_test.method
            test_headers = webhook_test.headers
            test_timeout = webhook_test.timeout
            
            # Crear webhook temporal para la prueba
            webhook = Webhook(
                id="test_webhook",
                name="Test Webhook",
                url=test_url,
                events=[webhook_test.event_type],
                method=test_method,
                headers=test_headers,
                secret=None,
                timeout=test_timeout,
                retry_attempts=0,
                retry_delay=0,
                status=WebhookStatus.ACTIVE,
                created_at=datetime.now(),
                total_deliveries=0,
                successful_deliveries=0,
                failed_deliveries=0,
                user_id="test_user"
            )
        
        # Crear payload de prueba
        if webhook_test.custom_payload:
            test_payload = webhook_test.custom_payload
        else:
            test_payload = create_sample_payload(webhook_test.event_type)
        
        # Agregar metadatos de prueba
        test_payload["test_mode"] = True
        test_payload["test_timestamp"] = datetime.now().isoformat()
        
        # Enviar petición de prueba
        try:
            result = await send_webhook_request(webhook, test_payload)
            
            # Registrar la prueba como una entrega
            test_delivery = WebhookDelivery(
                id=f"test_{uuid.uuid4().hex[:8]}",
                webhook_id=webhook_test.webhook_id or "test_webhook",
                event_type=webhook_test.event_type,
                payload=test_payload,
                status=WebhookDeliveryStatus.SUCCESS if result.success else WebhookDeliveryStatus.FAILED,
                http_status=result.http_status,
                response_body=result.response_body,
                response_headers=result.response_headers,
                attempt_count=1,
                duration_ms=result.duration_ms,
                error_message=result.error_message,
                created_at=datetime.now(),
                delivered_at=datetime.now() if result.success else None
            )
            
            # Guardar la entrega de prueba
            webhooks_db["deliveries"].append(test_delivery.dict())
            
            return WebhookResponse(
                message="Webhook test completed",
                data={
                    "test_result": result,
                    "delivery_record": test_delivery,
                    "webhook_config": {
                        "url": str(test_url),
                        "method": test_method.value,
                        "timeout": test_timeout,
                        "headers_count": len(test_headers) if test_headers else 0
                    }
                }
            )
            
        except Exception as e:
            # Crear resultado de error
            error_result = WebhookTestResult(
                success=False,
                http_status=0,
                response_body="",
                response_headers={},
                duration_ms=0,
                payload_sent=test_payload,
                error_message=str(e)
            )
            
            return WebhookResponse(
                message="Webhook test failed",
                data={
                    "test_result": error_result,
                    "error_details": str(e)
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing webhook: {str(e)}")

# Endpoints adicionales útiles

@router.get("/{webhook_id}/stats", response_model=WebhookResponse)
async def get_webhook_stats(webhook_id: str = Path(..., description="ID del webhook")):
    """Obtener estadísticas detalladas de un webhook"""
    try:
        # Verificar que el webhook existe
        if webhook_id not in webhooks_db["webhooks"]:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        webhook_data = webhooks_db["webhooks"][webhook_id]
        webhook = Webhook(**webhook_data)
        
        # Obtener entregas del webhook
        webhook_deliveries = [d for d in webhooks_db["deliveries"] if d["webhook_id"] == webhook_id]
        
        # Calcular estadísticas
        total_deliveries = len(webhook_deliveries)
        successful_deliveries = len([d for d in webhook_deliveries if d["status"] == "success"])
        failed_deliveries = total_deliveries - successful_deliveries
        
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Tiempo de respuesta promedio
        response_times = [d["duration_ms"] for d in webhook_deliveries if d["duration_ms"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Última entrega
        last_delivery = None
        if webhook_deliveries:
            last_delivery = max(webhook_deliveries, key=lambda x: x["created_at"])["created_at"]
        
        # Evento más común
        events_count = {}
        for delivery in webhook_deliveries:
            event = delivery["event_type"]
            events_count[event] = events_count.get(event, 0) + 1
        
        most_common_event = max(events_count.items(), key=lambda x: x[1])[0] if events_count else None
        
        # Entregas por estado
        deliveries_by_status = {}
        for delivery in webhook_deliveries:
            status = delivery["status"]
            deliveries_by_status[status] = deliveries_by_status.get(status, 0) + 1
        
        # Entregas por evento
        deliveries_by_event = events_count
        
        # Entregas recientes (últimas 10)
        recent_deliveries = sorted(webhook_deliveries, key=lambda x: x["created_at"], reverse=True)[:10]
        recent_deliveries_objects = [WebhookDelivery(**d) for d in recent_deliveries]
        
        # Crear estadísticas
        stats = WebhookStats(
            webhook_id=webhook_id,
            webhook_name=webhook.name,
            total_deliveries=total_deliveries,
            successful_deliveries=successful_deliveries,
            failed_deliveries=failed_deliveries,
            success_rate=round(success_rate, 2),
            avg_response_time=round(avg_response_time, 2),
            last_delivery=last_delivery,
            most_common_event=most_common_event,
            deliveries_by_status=deliveries_by_status,
            deliveries_by_event=deliveries_by_event,
            recent_deliveries=recent_deliveries_objects
        )
        
        return WebhookResponse(
            message="Webhook statistics retrieved successfully",
            data={
                "webhook": webhook,
                "statistics": stats
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving webhook stats: {str(e)}")

@router.get("/{webhook_id}/deliveries", response_model=WebhookResponse)
async def get_webhook_deliveries(
    webhook_id: str = Path(..., description="ID del webhook"),
    status: Optional[WebhookDeliveryStatus] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """Obtener entregas de un webhook específico"""
    try:
        # Verificar que el webhook existe
        if webhook_id not in webhooks_db["webhooks"]:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Filtrar entregas
        webhook_deliveries = [d for d in webhooks_db["deliveries"] if d["webhook_id"] == webhook_id]
        
        if status:
            webhook_deliveries = [d for d in webhook_deliveries if d["status"] == status]
        
        # Ordenar por fecha (más recientes primero)
        webhook_deliveries.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Aplicar paginación
        total_deliveries = len(webhook_deliveries)
        paginated_deliveries = webhook_deliveries[offset:offset + limit]
        
        # Convertir a objetos Pydantic
        delivery_objects = [WebhookDelivery(**d) for d in paginated_deliveries]
        
        return WebhookResponse(
            message=f"Retrieved {len(delivery_objects)} deliveries",
            data={
                "deliveries": delivery_objects,
                "total": total_deliveries,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_deliveries
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving webhook deliveries: {str(e)}")

@router.post("/{webhook_id}/retry", response_model=WebhookResponse)
async def retry_failed_deliveries(webhook_id: str = Path(..., description="ID del webhook")):
    """Reintentar entregas fallidas de un webhook"""
    try:
        # Verificar que el webhook existe
        if webhook_id not in webhooks_db["webhooks"]:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Encontrar entregas fallidas
        failed_deliveries = [d for d in webhooks_db["deliveries"] 
                           if d["webhook_id"] == webhook_id and d["status"] == "failed"]
        
        if not failed_deliveries:
            return WebhookResponse(
                message="No failed deliveries found to retry",
                data={
                    "retried_count": 0,
                    "webhook_id": webhook_id
                }
            )
        
        # Simular reintento (en producción esto sería asíncrono)
        retried_count = 0
        for delivery in failed_deliveries:
            # Actualizar estado a "retrying"
            delivery["status"] = "retrying"
            delivery["next_retry_at"] = (datetime.now() + timedelta(minutes=1)).isoformat()
            delivery["attempt_count"] += 1
            retried_count += 1
        
        return WebhookResponse(
            message=f"Retrying {retried_count} failed deliveries",
            data={
                "retried_count": retried_count,
                "webhook_id": webhook_id,
                "estimated_completion": datetime.now() + timedelta(minutes=5)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrying webhook deliveries: {str(e)}")
