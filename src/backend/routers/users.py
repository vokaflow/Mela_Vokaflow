#!/usr/bin/env python3
"""
VokaFlow - Router de Usuarios
Maneja gestión de usuarios, perfiles, preferencias y administración
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from pydantic import BaseModel, EmailStr, validator
import secrets

# Configuración de logging
logger = logging.getLogger("vokaflow.users")

# Router
router = APIRouter()

# Modelos Pydantic
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

class UserPreferences(BaseModel):
    language: str = "es"
    theme: str = "dark"
    notifications_email: bool = True
    notifications_push: bool = True
    timezone: str = "America/Mexico_City"
    voice_speed: float = 1.0
    voice_pitch: float = 1.0

class UserStats(BaseModel):
    total_translations: int
    total_voice_generations: int
    total_conversations: int
    account_age_days: int
    last_activity: datetime

# Dependencias simuladas
async def get_current_user():
    """Simulación de obtener usuario actual"""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@vokaflow.com",
        "is_active": True,
        "is_verified": True
    }

# Endpoints
@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Obtiene el perfil completo del usuario actual"""
    try:
        profile = {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": f"Usuario {current_user['username'].title()}",
            "bio": "Desarrollador apasionado por la tecnología",
            "location": "Ciudad de México, México",
            "website": "https://vokaflow.com",
            "is_active": current_user["is_active"],
            "is_verified": current_user["is_verified"],
            "created_at": datetime.now() - timedelta(days=30),
            "last_login": datetime.now() - timedelta(hours=1)
        }
        
        return profile
        
    except Exception as e:
        logger.error(f"Error al obtener perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener perfil"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza el perfil del usuario actual"""
    try:
        updated_fields = {}
        
        if profile_data.full_name is not None:
            updated_fields["full_name"] = profile_data.full_name
        
        if profile_data.email is not None:
            updated_fields["email"] = profile_data.email
        
        if profile_data.bio is not None:
            updated_fields["bio"] = profile_data.bio
        
        logger.info(f"Perfil actualizado para usuario {current_user['username']}")
        
        return {
            "message": "Perfil actualizado exitosamente",
            "updated_fields": updated_fields
        }
        
    except Exception as e:
        logger.error(f"Error al actualizar perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar perfil"
        )

@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(current_user: dict = Depends(get_current_user)):
    """Obtiene las preferencias del usuario"""
    try:
        preferences = UserPreferences(
            language="es",
            theme="dark",
            notifications_email=True,
            notifications_push=True,
            timezone="America/Mexico_City",
            voice_speed=1.0,
            voice_pitch=1.0
        )
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error al obtener preferencias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener preferencias"
        )

@router.get("/stats", response_model=UserStats)
async def get_user_statistics(current_user: dict = Depends(get_current_user)):
    """Obtiene estadísticas del usuario"""
    try:
        stats = UserStats(
            total_translations=150,
            total_voice_generations=75,
            total_conversations=25,
            account_age_days=30,
            last_activity=datetime.now() - timedelta(hours=2)
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas"
        )

@router.get("/status")
async def users_service_status():
    """Verifica el estado del servicio de usuarios"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "components": {
            "profile_management": "operational",
            "preferences": "operational",
            "user_search": "operational"
        },
        "metrics": {
            "total_users": 3,
            "active_users_24h": 2
        }
    }

@router.get("/list")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, min_length=2),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    role: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|username|email|last_login)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos los usuarios (solo para administradores)
    """
    try:
        # Verificar permisos de administrador
        if not current_user.get("is_superuser", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requieren permisos de administrador."
            )
        
        # En producción, esto consultaría la base de datos real
        # Simulamos una lista de usuarios para demostración
        all_users = [
            {
                "id": 1,
                "username": "capitan",
                "email": "capitan@vokaflow.com",
                "full_name": "Capitán VokaFlow",
                "is_active": True,
                "is_verified": True,
                "is_superuser": True,
                "role": "admin",
                "created_at": datetime.now() - timedelta(days=100),
                "last_login": datetime.now() - timedelta(hours=1),
                "total_translations": 500,
                "total_conversations": 150,
                "storage_used": 1024 * 1024 * 50  # 50MB
            },
            {
                "id": 2,
                "username": "usuario_demo",
                "email": "demo@vokaflow.com",
                "full_name": "Usuario Demo",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "role": "user",
                "created_at": datetime.now() - timedelta(days=30),
                "last_login": datetime.now() - timedelta(hours=6),
                "total_translations": 75,
                "total_conversations": 25,
                "storage_used": 1024 * 1024 * 10  # 10MB
            },
            {
                "id": 3,
                "username": "test_user",
                "email": "test@vokaflow.com",
                "full_name": "Usuario de Prueba",
                "is_active": False,
                "is_verified": False,
                "is_superuser": False,
                "role": "user",
                "created_at": datetime.now() - timedelta(days=7),
                "last_login": datetime.now() - timedelta(days=3),
                "total_translations": 5,
                "total_conversations": 2,
                "storage_used": 1024 * 1024 * 1  # 1MB
            },
            {
                "id": 4,
                "username": "moderador",
                "email": "mod@vokaflow.com",
                "full_name": "Moderador Sistema",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "role": "moderator",
                "created_at": datetime.now() - timedelta(days=60),
                "last_login": datetime.now() - timedelta(hours=12),
                "total_translations": 200,
                "total_conversations": 80,
                "storage_used": 1024 * 1024 * 25  # 25MB
            },
            {
                "id": 5,
                "username": "analista",
                "email": "analyst@vokaflow.com",
                "full_name": "Analista de Datos",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "role": "analyst",
                "created_at": datetime.now() - timedelta(days=45),
                "last_login": datetime.now() - timedelta(hours=2),
                "total_translations": 300,
                "total_conversations": 120,
                "storage_used": 1024 * 1024 * 35  # 35MB
            }
        ]
        
        # Aplicar filtros
        filtered_users = all_users.copy()
        
        # Filtro por búsqueda
        if search:
            search_lower = search.lower()
            filtered_users = [
                user for user in filtered_users
                if (search_lower in user["username"].lower() or
                    search_lower in user["email"].lower() or
                    search_lower in user["full_name"].lower())
            ]
        
        # Filtro por estado activo
        if is_active is not None:
            filtered_users = [user for user in filtered_users if user["is_active"] == is_active]
        
        # Filtro por verificación
        if is_verified is not None:
            filtered_users = [user for user in filtered_users if user["is_verified"] == is_verified]
        
        # Filtro por rol
        if role:
            filtered_users = [user for user in filtered_users if user["role"] == role]
        
        # Ordenamiento
        reverse_order = sort_order == "desc"
        if sort_by == "created_at":
            filtered_users.sort(key=lambda x: x["created_at"], reverse=reverse_order)
        elif sort_by == "username":
            filtered_users.sort(key=lambda x: x["username"], reverse=reverse_order)
        elif sort_by == "email":
            filtered_users.sort(key=lambda x: x["email"], reverse=reverse_order)
        elif sort_by == "last_login":
            filtered_users.sort(key=lambda x: x["last_login"], reverse=reverse_order)
        
        # Paginación
        total_users = len(filtered_users)
        paginated_users = filtered_users[skip:skip + limit]
        
        # Formatear fechas para respuesta
        for user in paginated_users:
            user["created_at"] = user["created_at"].isoformat()
            user["last_login"] = user["last_login"].isoformat()
        
        # Estadísticas generales
        stats = {
            "total_users": len(all_users),
            "active_users": len([u for u in all_users if u["is_active"]]),
            "verified_users": len([u for u in all_users if u["is_verified"]]),
            "admin_users": len([u for u in all_users if u["is_superuser"]]),
            "users_by_role": {
                "admin": len([u for u in all_users if u["role"] == "admin"]),
                "moderator": len([u for u in all_users if u["role"] == "moderator"]),
                "analyst": len([u for u in all_users if u["role"] == "analyst"]),
                "user": len([u for u in all_users if u["role"] == "user"])
            },
            "total_storage_used": sum(u["storage_used"] for u in all_users),
            "avg_translations_per_user": sum(u["total_translations"] for u in all_users) / len(all_users)
        }
        
        return {
            "users": paginated_users,
            "pagination": {
                "total": total_users,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_users,
                "has_prev": skip > 0
            },
            "filters_applied": {
                "search": search,
                "is_active": is_active,
                "is_verified": is_verified,
                "role": role,
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de usuarios"
        )

@router.put("/{user_id}/admin-update")
@router.delete("/{user_id}/admin-delete")
async def admin_delete_user(
    user_id: int,
    force: bool = Query(False, description="Forzar eliminación sin verificaciones adicionales"),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un usuario (solo administradores)
    """
    try:
        # Verificar permisos de administrador
        if not current_user.get("is_superuser", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requieren permisos de administrador."
            )
        
        # Validar que el usuario existe
        if user_id not in [1, 2, 3, 4, 5]:  # IDs simulados
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Prevenir auto-eliminación
        if user_id == current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu propia cuenta"
            )
        
        # Verificaciones adicionales si no es forzado
        if not force:
            # En producción, verificar si el usuario tiene datos importantes
            has_important_data = user_id in [1, 4]  # Simular usuarios con datos importantes
            
            if has_important_data:
                return {
                    "warning": True,
                    "message": "El usuario tiene datos importantes. Use force=true para confirmar eliminación.",
                    "data_summary": {
                        "translations": 100,
                        "conversations": 50,
                        "files": 25
                    }
                }
        
        # En producción, aquí se eliminaría el usuario de la base de datos
        logger.warning(f"Usuario {user_id} eliminado por administrador {current_user['username']}")
        
        return {
            "success": True,
            "message": f"Usuario {user_id} eliminado correctamente",
            "deleted_by": current_user["username"],
            "timestamp": datetime.now().isoformat(),
            "force_used": force
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el usuario"
        )

