#!/usr/bin/env python3
"""
🚀 Endpoints de Autenticación Robusta - VokaFlow Enterprise
API completa con registro, login, refresh tokens, reseteo de contraseñas y más
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_

# Importar nuestro sistema de autenticación robusto
from ..auth_robust import (
    auth_manager,
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    ChangePasswordRequest,
    SecurityContext,
    get_current_active_user_robust,
    validate_user_registration,
    log_security_event,
    AccountLockedError,
    TokenExpiredError,
    InvalidTokenError
)

# Importar modelos de base de datos (comentado para evitar importación circular)
# # Removed circular import - using local database setup
# Por ahora usamos cache en memoria para evitar importación circular

# Configuración de logging
logger = logging.getLogger("vokaflow.auth.robust.router")

# Router
router = APIRouter(prefix="/auth-robust", tags=["Autenticación Robusta"])

# Cache en memoria para usuarios (en producción usaríamos base de datos real)
users_cache = {
    "admin": {
        "id": 1,
        "username": "admin", 
        "email": "admin@vokaflow.com",
        "password_hash": auth_manager.hash_password("Admin123!"),
        "full_name": "Administrador VokaFlow",
        "is_active": True,
        "is_verified": True,
        "permissions": ["admin", "user", "translate", "chat", "system"],
        "created_at": "2024-01-01T00:00:00"
    },
    "demo": {
        "id": 2,
        "username": "demo",
        "email": "demo@vokaflow.com", 
        "password_hash": auth_manager.hash_password("Demo123!"),
        "full_name": "Usuario Demo",
        "is_active": True,
        "is_verified": True,
        "permissions": ["user", "translate", "chat"],
        "created_at": "2024-01-01T00:00:00"
    }
}

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por nombre de usuario"""
    return users_cache.get(username.lower())

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por email"""
    for user in users_cache.values():
        if user["email"].lower() == email.lower():
            return user
    return None

def create_user(user_data: UserRegister) -> Dict[str, Any]:
    """Crear nuevo usuario"""
    user_id = len(users_cache) + 1
    username_lower = user_data.username.lower()
    
    new_user = {
        "id": user_id,
        "username": username_lower,
        "email": user_data.email.lower(),
        "password_hash": auth_manager.hash_password(user_data.password),
        "full_name": user_data.full_name or user_data.username,
        "is_active": True,
        "is_verified": False,  # Requiere verificación de email
        "permissions": ["user"],  # Permisos básicos
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_cache[username_lower] = new_user
    return new_user

async def send_verification_email(email: str, token: str):
    """Enviar email de verificación (simulado)"""
    logger.info(f"📧 Enviando email de verificación a {email} con token {token[:20]}...")
    # En producción aquí enviarías un email real
    await asyncio.sleep(0.1)  # Simular envío

async def send_password_reset_email(email: str, token: str):
    """Enviar email de reseteo de contraseña (simulado)"""
    logger.info(f"🔑 Enviando email de reseteo de contraseña a {email}")
    await asyncio.sleep(0.1)

@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    user_data: UserRegister,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    🔐 Registro robusto de usuario
    
    Características:
    - Validación exhaustiva de datos
    - Verificación de usuario/email existente
    - Hash seguro de contraseña
    - Rate limiting
    - Logging de seguridad
    """
    try:
        # Verificar rate limiting
        client_ip = auth_manager._get_client_ip(request)
        if auth_manager._is_rate_limited(client_ip, "register"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many registration attempts. Please try again later."
            )
        
        logger.info(f"🔐 Intento de registro para usuario: {user_data.username}")
        
        # Validar datos de registro
        existing_usernames = list(users_cache.keys())
        existing_emails = [user["email"] for user in users_cache.values()]
        
        validation_result = validate_user_registration(user_data, existing_usernames, existing_emails)
        if not validation_result["valid"]:
            log_security_event("registration_failed", None, {
                "username": user_data.username,
                "email": user_data.email,
                "errors": validation_result["errors"],
                "ip_address": client_ip
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Registration validation failed", "errors": validation_result["errors"]}
            )
        
        # Crear usuario
        new_user = create_user(user_data)
        
        # Generar token de verificación
        verification_token = auth_manager.generate_password_reset_token(
            str(new_user["id"]), 
            new_user["email"]
        )
        
        # Enviar email de verificación en background
        background_tasks.add_task(send_verification_email, new_user["email"], verification_token)
        
        # Log evento de seguridad
        log_security_event("user_registered", str(new_user["id"]), {
            "username": new_user["username"],
            "email": new_user["email"],
            "ip_address": client_ip
        })
        
        logger.info(f"✅ Usuario {user_data.username} registrado exitosamente")
        
        return {
            "success": True,
            "message": "User registered successfully. Please check your email for verification.",
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "email": new_user["email"],
                "full_name": new_user["full_name"],
                "is_verified": new_user["is_verified"]
            },
            "verification_required": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al registrar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_data: UserLogin,
    request: Request
):
    """
    🔐 Login robusto con protección contra ataques
    
    Características:
    - Rate limiting por IP y usuario
    - Bloqueo de cuenta tras intentos fallidos
    - Sesiones seguras
    - Logging de seguridad
    - Tokens JWT con expiración
    """
    try:
        client_ip = auth_manager._get_client_ip(request)
        
        # Verificar rate limiting
        if auth_manager._is_rate_limited(client_ip, "login"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )
        
        logger.info(f"🔐 Intento de login para usuario: {user_data.username}")
        
        # Verificar si la cuenta está bloqueada
        if auth_manager._is_account_locked(user_data.username):
            log_security_event("login_blocked", None, {
                "username": user_data.username,
                "ip_address": client_ip,
                "reason": "account_locked"
            })
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked due to too many failed attempts. Please try again later."
            )
        
        # Buscar usuario
        user = get_user_by_username(user_data.username)
        if not user:
            auth_manager._record_failed_attempt(user_data.username, client_ip)
            log_security_event("login_failed", None, {
                "username": user_data.username,
                "ip_address": client_ip,
                "reason": "user_not_found"
            })
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar contraseña
        if not auth_manager.verify_password(user_data.password, user["password_hash"]):
            auth_manager._record_failed_attempt(user_data.username, client_ip)
            log_security_event("login_failed", str(user["id"]), {
                "username": user_data.username,
                "ip_address": client_ip,
                "reason": "invalid_password"
            })
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el usuario esté activo
        if not user["is_active"]:
            log_security_event("login_failed", str(user["id"]), {
                "username": user_data.username,
                "ip_address": client_ip,
                "reason": "user_inactive"
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )
        
        # Limpiar intentos fallidos tras login exitoso
        auth_manager._clear_failed_attempts(user_data.username)
        
        # Crear sesión
        session_id = auth_manager.create_session({
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }, request)
        
        # Configurar expiración de tokens
        access_token_expires = timedelta(minutes=30 if not user_data.remember_me else 480)  # 8h si "remember me"
        
        # Datos del token
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "email": user["email"],
            "is_active": user["is_active"],
            "is_verified": user["is_verified"],
            "permissions": user["permissions"],
            "session_id": session_id,
            "device_name": user_data.device_name or "Unknown Device"
        }
        
        # Crear tokens
        access_token = auth_manager.create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        refresh_token = auth_manager.create_refresh_token(data=token_data)
        
        # Log evento de seguridad
        log_security_event("login_successful", str(user["id"]), {
            "username": user["username"],
            "ip_address": client_ip,
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "remember_me": user_data.remember_me,
            "session_id": session_id
        })
        
        logger.info(f"✅ Usuario {user_data.username} autenticado exitosamente")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user_info={
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "is_verified": user["is_verified"]
            },
            permissions=user["permissions"],
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al autenticar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """
    🔐 Endpoint compatible con OAuth2 para obtener token de acceso
    """
    user_data = UserLogin(username=form_data.username, password=form_data.password)
    return await login_user(user_data, request)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    request: Request
):
    """
    🔄 Renovar token de acceso usando refresh token
    """
    try:
        client_ip = auth_manager._get_client_ip(request)
        
        # Verificar rate limiting
        if auth_manager._is_rate_limited(client_ip, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many refresh attempts"
            )
        
        # Verificar refresh token
        payload = auth_manager.verify_token(refresh_request.refresh_token, "refresh")
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        # Verificar que el usuario aún exista y esté activo
        user = get_user_by_username(username)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer active"
            )
        
        # Verificar sesión
        session_data = auth_manager.get_session(session_id)
        if not session_data or not session_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid"
            )
        
        # Crear nuevo token de acceso
        token_data = {
            "sub": user["username"],
            "user_id": user["id"],
            "email": user["email"],
            "is_active": user["is_active"],
            "is_verified": user["is_verified"],
            "permissions": user["permissions"],
            "session_id": session_id
        }
        
        access_token = auth_manager.create_access_token(data=token_data)
        new_refresh_token = auth_manager.create_refresh_token(data=token_data)
        
        # Blacklist el refresh token anterior
        old_jti = payload.get("jti")
        if old_jti:
            auth_manager.blacklist_token(old_jti, 7 * 24 * 60 * 60)  # 7 días
        
        # Log evento de seguridad
        log_security_event("token_refreshed", str(user["id"]), {
            "username": user["username"],
            "ip_address": client_ip,
            "session_id": session_id
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutos
            user_info={
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "is_verified": user["is_verified"]
            },
            permissions=user["permissions"],
            session_id=session_id
        )
        
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error al renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/logout")
async def logout_user(
    current_user: SecurityContext = Depends(get_current_active_user_robust),
    request: Request = None
):
    """
    🚪 Logout seguro del usuario
    """
    try:
        # Invalidar sesión
        if current_user.session_id:
            auth_manager.invalidate_session(current_user.session_id)
        
        # Log evento de seguridad
        log_security_event("logout", current_user.user_id, {
            "username": current_user.username,
            "ip_address": current_user.ip_address,
            "session_id": current_user.session_id
        })
        
        logger.info(f"🚪 Usuario {current_user.username} cerró sesión")
        
        return {
            "success": True,
            "message": "Successfully logged out"
        }
        
    except Exception as e:
        logger.error(f"❌ Error al cerrar sesión: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

@router.post("/password-reset-request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    🔑 Solicitar reseteo de contraseña
    """
    try:
        client_ip = auth_manager._get_client_ip(request)
        
        # Verificar rate limiting
        if auth_manager._is_rate_limited(client_ip, "password_reset"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many password reset attempts"
            )
        
        # Buscar usuario por email
        user = get_user_by_email(reset_request.email)
        
        # Siempre devolver éxito para evitar enumeration attacks
        message = "If the email exists in our system, you will receive a password reset link."
        
        if user and user["is_active"]:
            # Generar token de reseteo
            reset_token = auth_manager.generate_password_reset_token(
                str(user["id"]), 
                user["email"]
            )
            
            # Enviar email en background
            background_tasks.add_task(send_password_reset_email, user["email"], reset_token)
            
            # Log evento de seguridad
            log_security_event("password_reset_requested", str(user["id"]), {
                "email": user["email"],
                "ip_address": client_ip
            })
        
        return {
            "success": True,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"❌ Error al solicitar reseteo de contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/password-reset-confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    request: Request
):
    """
    🔑 Confirmar reseteo de contraseña
    """
    try:
        client_ip = auth_manager._get_client_ip(request)
        
        # Verificar token de reseteo
        payload = auth_manager.verify_password_reset_token(reset_confirm.token)
        
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        # Buscar usuario
        user = get_user_by_email(email)
        if not user or str(user["id"]) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Actualizar contraseña
        user["password_hash"] = auth_manager.hash_password(reset_confirm.new_password)
        
        # Log evento de seguridad
        log_security_event("password_reset_completed", str(user["id"]), {
            "email": user["email"],
            "ip_address": client_ip
        })
        
        logger.info(f"🔑 Contraseña reseteada para usuario {user['username']}")
        
        return {
            "success": True,
            "message": "Password has been reset successfully"
        }
        
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error al confirmar reseteo de contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/change-password")
async def change_password(
    password_change: ChangePasswordRequest,
    current_user: SecurityContext = Depends(get_current_active_user_robust),
    request: Request = None
):
    """
    🔐 Cambiar contraseña del usuario autenticado
    """
    try:
        # Buscar usuario actual
        user = get_user_by_username(current_user.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verificar contraseña actual
        if not auth_manager.verify_password(password_change.current_password, user["password_hash"]):
            log_security_event("password_change_failed", current_user.user_id, {
                "username": current_user.username,
                "reason": "invalid_current_password",
                "ip_address": current_user.ip_address
            })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Actualizar contraseña
        user["password_hash"] = auth_manager.hash_password(password_change.new_password)
        
        # Log evento de seguridad
        log_security_event("password_changed", current_user.user_id, {
            "username": current_user.username,
            "ip_address": current_user.ip_address
        })
        
        logger.info(f"🔐 Contraseña cambiada para usuario {current_user.username}")
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al cambiar contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me")
async def get_current_user_info(
    current_user: SecurityContext = Depends(get_current_active_user_robust)
):
    """
    👤 Obtener información del usuario actual
    """
    user = get_user_by_username(current_user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_active": user["is_active"],
        "is_verified": user["is_verified"],
        "permissions": user["permissions"],
        "created_at": user["created_at"],
        "session_info": {
            "session_id": current_user.session_id,
            "ip_address": current_user.ip_address,
            "user_agent": current_user.user_agent,
            "last_activity": current_user.last_activity.isoformat()
        }
    }

@router.get("/sessions")
async def get_user_sessions(
    current_user: SecurityContext = Depends(get_current_active_user_robust)
):
    """
    📱 Obtener sesiones activas del usuario
    """
    # En una implementación real, buscarías en la base de datos
    # Por ahora, devolvemos la sesión actual
    return {
        "active_sessions": [
            {
                "session_id": current_user.session_id,
                "ip_address": current_user.ip_address,
                "user_agent": current_user.user_agent,
                "created_at": current_user.created_at.isoformat(),
                "last_activity": current_user.last_activity.isoformat(),
                "is_current": True
            }
        ]
    }

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: SecurityContext = Depends(get_current_active_user_robust)
):
    """
    🚫 Revocar sesión específica
    """
    try:
        # Verificar que la sesión pertenezca al usuario
        session_data = auth_manager.get_session(session_id)
        if not session_data or session_data.get("user_id") != int(current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Invalidar sesión
        auth_manager.invalidate_session(session_id)
        
        # Log evento de seguridad
        log_security_event("session_revoked", current_user.user_id, {
            "username": current_user.username,
            "revoked_session_id": session_id,
            "ip_address": current_user.ip_address
        })
        
        return {
            "success": True,
            "message": "Session revoked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al revocar sesión: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/security-events")
async def get_security_events(
    current_user: SecurityContext = Depends(get_current_active_user_robust),
    limit: int = 50
):
    """
    🔒 Obtener eventos de seguridad del usuario (solo para demostración)
    """
    # En una implementación real, buscarías en logs de seguridad
    return {
        "events": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "login_successful",
                "ip_address": current_user.ip_address,
                "user_agent": current_user.user_agent
            }
        ],
        "total": 1
    } 