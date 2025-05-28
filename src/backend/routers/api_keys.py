from fastapi import APIRouter, HTTPException, Depends, Query, Path, Security, status
from typing import List, Dict, Any, Optional
import uuid
import secrets
import string
import random
from datetime import datetime, timedelta

from ..models.api_keys_model import (
    ApiKeyCreate, ApiKey, ApiKeyPublic, ApiKeyUpdate, ApiKeyUsage,
    ApiKeyUsageSummary, ApiKeyResponse, ApiKeyCreateResponse,
    ApiKeyScope, ApiKeyStatus, ApiKeyEnvironment, ApiKeyType
)

router = APIRouter(tags=["API Keys"])

# Simulación de base de datos en memoria
api_keys_db = {
    "keys": {},
    "usage": []
}

def generate_api_key(prefix: str = None, length: int = 32) -> tuple:
    """Genera una nueva API key con prefijo opcional"""
    if not prefix:
        # Generar prefijo basado en entorno y tipo
        prefix = "sk_live"
    
    # Generar parte aleatoria de la clave
    alphabet = string.ascii_letters + string.digits
    key_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Combinar prefijo y parte aleatoria
    full_key = f"{prefix}_{key_part}"
    
    # Crear prefijo visible (primeros 8 caracteres)
    visible_prefix = f"{prefix}_{key_part[:5]}"
    
    return full_key, visible_prefix

def initialize_sample_api_keys():
    """Inicializa algunas API keys de ejemplo si la base de datos está vacía"""
    if not api_keys_db["keys"]:
        # Crear algunas API keys de ejemplo
        environments = list(ApiKeyEnvironment)
        types = list(ApiKeyType)
        scopes_options = [
            [ApiKeyScope.READ],
            [ApiKeyScope.READ, ApiKeyScope.WRITE],
            [ApiKeyScope.READ, ApiKeyScope.WRITE, ApiKeyScope.TRANSLATE],
            [ApiKeyScope.ADMIN]
        ]
        
        for i in range(5):
            key_id = f"ak_{uuid.uuid4().hex[:8]}"
            env = random.choice(environments)
            key_type = random.choice(types)
            prefix = f"sk_{env.value[:3]}_{key_type.value[:3]}"
            
            full_key, visible_prefix = generate_api_key(prefix)
            
            api_key = ApiKey(
                id=key_id,
                key=full_key,
                prefix=visible_prefix,
                name=f"Sample API Key {i+1}",
                user_id=f"user_{random.randint(1, 10)}",
                scopes=random.choice(scopes_options),
                status=ApiKeyStatus.ACTIVE if random.random() > 0.2 else ApiKeyStatus.REVOKED,
                environment=env,
                type=key_type,
                created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                expires_at=datetime.now() + timedelta(days=random.randint(30, 365)) if random.random() > 0.3 else None,
                last_used_at=datetime.now() - timedelta(hours=random.randint(1, 168)) if random.random() > 0.3 else None,
                rate_limit=random.choice([None, 60, 100, 1000]),
                metadata={
                    "created_by": "system",
                    "project": f"project_{random.randint(1, 5)}",
                    "description": f"Sample API key for testing purposes #{i+1}"
                }
            )
            
            api_keys_db["keys"][key_id] = api_key.dict()
    
    # Generar datos de uso si no hay
    if len(api_keys_db["usage"]) < 100:
        generate_sample_usage_data()

def generate_sample_usage_data():
    """Genera datos de uso de ejemplo para las API keys"""
    if not api_keys_db["keys"]:
        return
    
    endpoints = [
        "/api/vicky/process", 
        "/api/translate", 
        "/api/tts/synthesize", 
        "/api/stt/transcribe",
        "/api/voice/samples",
        "/api/files/upload"
    ]
    
    methods = ["GET", "POST", "PUT", "DELETE"]
    status_codes = [200, 201, 400, 401, 403, 404, 429, 500]
    
    # Generar 100 registros de uso
    for _ in range(100):
        key_id = random.choice(list(api_keys_db["keys"].keys()))
        
        usage = ApiKeyUsage(
            api_key_id=key_id,
            endpoint=random.choice(endpoints),
            method=random.choice(methods),
            status_code=random.choice(status_codes),
            response_time=random.uniform(50, 2000),
            timestamp=datetime.now() - timedelta(hours=random.randint(1, 168)),
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            user_agent="API Client/1.0",
            request_size=random.randint(100, 10000),
            response_size=random.randint(100, 50000),
            error=None if random.random() > 0.2 else "Rate limit exceeded"
        )
        
        api_keys_db["usage"].append(usage.dict())
        
        # Actualizar last_used_at en la API key
        if usage.timestamp > api_keys_db["keys"][key_id].get("last_used_at", datetime.min):
            api_keys_db["keys"][key_id]["last_used_at"] = usage.timestamp

def get_api_key_public(api_key: dict) -> ApiKeyPublic:
    """Convierte una API key en su versión pública"""
    # Calcular días hasta expiración
    days_until_expiry = None
    is_expired = False
    
    if api_key.get("expires_at"):
        expires_at = api_key["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        
        now = datetime.now()
        if expires_at > now:
            days_until_expiry = (expires_at - now).days
        else:
            is_expired = True
    
    # Contar usos
    usage_count = len([u for u in api_keys_db["usage"] if u["api_key_id"] == api_key["id"]])
    
    return ApiKeyPublic(
        id=api_key["id"],
        prefix=api_key["prefix"],
        name=api_key["name"],
        scopes=api_key["scopes"],
        status=api_key["status"],
        environment=api_key["environment"],
        type=api_key["type"],
        created_at=api_key["created_at"],
        expires_at=api_key["expires_at"],
        last_used_at=api_key["last_used_at"],
        rate_limit=api_key["rate_limit"],
        metadata=api_key["metadata"],
        usage_count=usage_count,
        is_expired=is_expired,
        days_until_expiry=days_until_expiry
    )

@router.get("/list", response_model=ApiKeyResponse)
async def list_api_keys(
    environment: Optional[ApiKeyEnvironment] = Query(None, description="Filtrar por entorno"),
    status: Optional[ApiKeyStatus] = Query(None, description="Filtrar por estado"),
    type: Optional[ApiKeyType] = Query(None, description="Filtrar por tipo"),
    search: Optional[str] = Query(None, description="Buscar por nombre o prefijo"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    🔑 Lista todas las API keys
    
    Devuelve una lista paginada de API keys con opciones de filtrado.
    Las API keys se devuelven en formato seguro (sin la clave completa).
    """
    try:
        initialize_sample_api_keys()
        
        # Filtrar API keys
        filtered_keys = []
        for key_data in api_keys_db["keys"].values():
            # Aplicar filtros
            if environment and key_data["environment"] != environment:
                continue
            if status and key_data["status"] != status:
                continue
            if type and key_data["type"] != type:
                continue
            if search and search.lower() not in key_data["name"].lower() and search.lower() not in key_data["prefix"].lower():
                continue
            
            # Convertir a versión pública
            public_key = get_api_key_public(key_data)
            filtered_keys.append(public_key)
        
        # Ordenar por fecha de creación (más recientes primero)
        filtered_keys.sort(key=lambda x: x.created_at, reverse=True)
        
        # Aplicar paginación
        total_filtered = len(filtered_keys)
        paginated_keys = filtered_keys[offset:offset + limit]
        
        # Estadísticas
        active_keys = len([k for k in filtered_keys if k.status == ApiKeyStatus.ACTIVE])
        expired_keys = len([k for k in filtered_keys if k.is_expired])
        
        return ApiKeyResponse(
            message=f"Retrieved {len(paginated_keys)} API keys",
            data={
                "api_keys": paginated_keys,
                "total": total_filtered,
                "active_keys": active_keys,
                "expired_keys": expired_keys,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_filtered
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving API keys: {str(e)}")

@router.post("/create", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(api_key_create: ApiKeyCreate):
    """
    🔑 Crear una nueva API key
    
    Crea una nueva API key con los parámetros especificados.
    IMPORTANTE: La API key completa solo se muestra una vez en la respuesta.
    """
    try:
        # Generar ID único
        key_id = f"ak_{uuid.uuid4().hex[:8]}"
        
        # Generar prefijo basado en entorno y tipo
        prefix = f"sk_{api_key_create.environment.value[:3]}_{api_key_create.type.value[:3]}"
        
        # Generar API key
        full_key, visible_prefix = generate_api_key(prefix)
        
        # Crear objeto API key
        api_key = ApiKey(
            id=key_id,
            key=full_key,
            prefix=visible_prefix,
            name=api_key_create.name,
            user_id="current_user_id",  # En producción sería el usuario actual
            scopes=api_key_create.scopes,
            status=ApiKeyStatus.ACTIVE,
            environment=api_key_create.environment,
            type=api_key_create.type,
            created_at=datetime.now(),
            expires_at=api_key_create.expires_at,
            last_used_at=None,
            rate_limit=api_key_create.rate_limit,
            metadata=api_key_create.metadata or {
                "created_by": "api",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Guardar en la base de datos
        api_keys_db["keys"][key_id] = api_key.dict()
        
        return ApiKeyCreateResponse(
            message="API key created successfully",
            api_key=api_key,
            important_notice="IMPORTANTE: Esta es la única vez que verás la API key completa. Guárdala en un lugar seguro."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating API key: {str(e)}")

@router.delete("/{api_key_id}", response_model=ApiKeyResponse)
async def delete_api_key(api_key_id: str = Path(..., description="ID de la API key a eliminar")):
    """
    🗑️ Eliminar API key
    
    Elimina permanentemente una API key. Esta acción no puede deshacerse.
    Para desactivar temporalmente una API key, use el endpoint de actualización para cambiar su estado.
    """
    try:
        # Verificar que la API key existe
        if api_key_id not in api_keys_db["keys"]:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Obtener datos de la API key antes de eliminarla
        api_key_data = api_keys_db["keys"][api_key_id]
        api_key = get_api_key_public(api_key_data)
        
        # Eliminar la API key
        del api_keys_db["keys"][api_key_id]
        
        # Eliminar datos de uso asociados
        api_keys_db["usage"] = [u for u in api_keys_db["usage"] if u["api_key_id"] != api_key_id]
        
        return ApiKeyResponse(
            message="API key deleted successfully",
            data={
                "deleted_key": api_key,
                "deleted_at": datetime.now(),
                "usage_records_deleted": len([u for u in api_keys_db["usage"] if u["api_key_id"] == api_key_id])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting API key: {str(e)}")

@router.put("/{api_key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    api_key_update: ApiKeyUpdate,
    api_key_id: str = Path(..., description="ID de la API key a actualizar")
):
    """
    ✏️ Actualizar API key
    
    Actualiza los atributos de una API key existente.
    No se puede modificar la clave en sí, solo sus metadatos y configuración.
    """
    try:
        # Verificar que la API key existe
        if api_key_id not in api_keys_db["keys"]:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Obtener datos actuales
        api_key_data = api_keys_db["keys"][api_key_id]
        
        # Aplicar actualizaciones
        update_dict = api_key_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                api_key_data[field] = value
        
        # Actualizar timestamp
        api_key_data["updated_at"] = datetime.now().isoformat()
        
        # Guardar cambios
        api_keys_db["keys"][api_key_id] = api_key_data
        
        # Obtener versión pública actualizada
        updated_key = get_api_key_public(api_key_data)
        
        return ApiKeyResponse(
            message="API key updated successfully",
            data={
                "api_key": updated_key,
                "updated_fields": list(update_dict.keys()),
                "updated_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating API key: {str(e)}")

@router.get("/usage", response_model=ApiKeyResponse)
async def get_api_key_usage(
    api_key_id: Optional[str] = Query(None, description="ID de la API key específica"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    group_by: str = Query("day", description="Agrupar por: day, hour, endpoint")
):
    """
    📊 Uso de API keys
    
    Obtiene estadísticas de uso de las API keys.
    Permite filtrar por API key específica y rango de fechas.
    """
    try:
        initialize_sample_api_keys()
        
        # Establecer fechas por defecto si no se proporcionan
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Filtrar datos de uso
        filtered_usage = []
        for usage_data in api_keys_db["usage"]:
            # Convertir timestamp a datetime si es string
            timestamp = usage_data["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            
            # Aplicar filtros
            if api_key_id and usage_data["api_key_id"] != api_key_id:
                continue
            if timestamp < start_date or timestamp > end_date:
                continue
            
            filtered_usage.append(usage_data)
        
        # Si se especificó una API key, generar resumen detallado
        if api_key_id:
            if api_key_id not in api_keys_db["keys"]:
                raise HTTPException(status_code=404, detail="API key not found")
            
            api_key_data = api_keys_db["keys"][api_key_id]
            
            # Calcular estadísticas
            total_requests = len(filtered_usage)
            successful_requests = len([u for u in filtered_usage if u["status_code"] < 400])
            failed_requests = total_requests - successful_requests
            
            avg_response_time = 0
            if filtered_usage:
                avg_response_time = sum(u["response_time"] for u in filtered_usage) / total_requests
            
            total_data = sum((u.get("request_size", 0) or 0) + (u.get("response_size", 0) or 0) for u in filtered_usage)
            
            # Top endpoints
            endpoints = {}
            for usage in filtered_usage:
                endpoint = usage["endpoint"]
                endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
            
            top_endpoints = [{"endpoint": e, "count": c} for e, c in sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:5]]
            
            # Uso por día
            usage_by_day = {}
            for usage in filtered_usage:
                timestamp = usage["timestamp"]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                
                day_key = timestamp.strftime("%Y-%m-%d")
                usage_by_day[day_key] = usage_by_day.get(day_key, 0) + 1
            
            # Último uso
            last_used = max([u["timestamp"] for u in filtered_usage]) if filtered_usage else None
            
            # Tasa de error
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Crear resumen
            summary = ApiKeyUsageSummary(
                api_key_id=api_key_id,
                api_key_name=api_key_data["name"],
                api_key_prefix=api_key_data["prefix"],
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                avg_response_time=avg_response_time,
                total_data_transferred=total_data,
                top_endpoints=top_endpoints,
                usage_by_day=usage_by_day,
                last_used=last_used,
                error_rate=error_rate
            )
            
            return ApiKeyResponse(
                message=f"Usage statistics for API key {api_key_id}",
                data={
                    "summary": summary,
                    "period": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "days": (end_date - start_date).days
                    },
                    "api_key": get_api_key_public(api_key_data)
                }
            )
        
        # Si no se especificó una API key, generar resumen global
        else:
            # Agrupar por API key
            usage_by_key = {}
            for usage in filtered_usage:
                key_id = usage["api_key_id"]
                usage_by_key[key_id] = usage_by_key.get(key_id, 0) + 1
            
            # Top API keys por uso
            top_keys = []
            for key_id, count in sorted(usage_by_key.items(), key=lambda x: x[1], reverse=True)[:10]:
                if key_id in api_keys_db["keys"]:
                    key_data = api_keys_db["keys"][key_id]
                    top_keys.append({
                        "id": key_id,
                        "name": key_data["name"],
                        "prefix": key_data["prefix"],
                        "count": count,
                        "environment": key_data["environment"]
                    })
            
            # Uso por día
            usage_by_day = {}
            for usage in filtered_usage:
                timestamp = usage["timestamp"]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                
                day_key = timestamp.strftime("%Y-%m-%d")
                usage_by_day[day_key] = usage_by_day.get(day_key, 0) + 1
            
            # Uso por endpoint
            usage_by_endpoint = {}
            for usage in filtered_usage:
                endpoint = usage["endpoint"]
                usage_by_endpoint[endpoint] = usage_by_endpoint.get(endpoint, 0) + 1
            
            top_endpoints = [{"endpoint": e, "count": c} for e, c in sorted(usage_by_endpoint.items(), key=lambda x: x[1], reverse=True)]
            
            # Estadísticas globales
            total_requests = len(filtered_usage)
            successful_requests = len([u for u in filtered_usage if u["status_code"] < 400])
            failed_requests = total_requests - successful_requests
            
            avg_response_time = 0
            if filtered_usage:
                avg_response_time = sum(u["response_time"] for u in filtered_usage) / total_requests
            
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            return ApiKeyResponse(
                message="Global API key usage statistics",
                data={
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests,
                    "avg_response_time": avg_response_time,
                    "error_rate": error_rate,
                    "top_api_keys": top_keys,
                    "usage_by_day": usage_by_day,
                    "top_endpoints": top_endpoints[:5],
                    "period": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "days": (end_date - start_date).days
                    }
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving API key usage: {str(e)}")

# Endpoints adicionales útiles

@router.post("/{api_key_id}/revoke", response_model=ApiKeyResponse)
async def revoke_api_key(api_key_id: str = Path(..., description="ID de la API key a revocar")):
    """Revoca una API key"""
    try:
        # Verificar que la API key existe
        if api_key_id not in api_keys_db["keys"]:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Obtener datos actuales
        api_key_data = api_keys_db["keys"][api_key_id]
        
        # Cambiar estado a revocado
        api_key_data["status"] = ApiKeyStatus.REVOKED
        api_key_data["revoked_at"] = datetime.now().isoformat()
        
        # Guardar cambios
        api_keys_db["keys"][api_key_id] = api_key_data
        
        # Obtener versión pública actualizada
        updated_key = get_api_key_public(api_key_data)
        
        return ApiKeyResponse(
            message="API key revoked successfully",
            data={
                "api_key": updated_key,
                "revoked_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error revoking API key: {str(e)}")

@router.post("/{api_key_id}/regenerate", response_model=ApiKeyCreateResponse)
async def regenerate_api_key(api_key_id: str = Path(..., description="ID de la API key a regenerar")):
    """Regenera una API key manteniendo su configuración"""
    try:
        # Verificar que la API key existe
        if api_key_id not in api_keys_db["keys"]:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Obtener datos actuales
        api_key_data = api_keys_db["keys"][api_key_id]
        
        # Generar nueva clave
        prefix = f"sk_{api_key_data['environment'][:3]}_{api_key_data['type'][:3]}"
        full_key, visible_prefix = generate_api_key(prefix)
        
        # Actualizar datos
        api_key_data["key"] = full_key
        api_key_data["prefix"] = visible_prefix
        api_key_data["regenerated_at"] = datetime.now().isoformat()
        
        # Guardar cambios
        api_keys_db["keys"][api_key_id] = api_key_data
        
        # Crear objeto API key para respuesta
        api_key = ApiKey(**api_key_data)
        
        return ApiKeyCreateResponse(
            message="API key regenerated successfully",
            api_key=api_key,
            important_notice="IMPORTANTE: Esta es la única vez que verás la API key regenerada completa. Guárdala en un lugar seguro."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating API key: {str(e)}")
