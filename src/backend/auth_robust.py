#!/usr/bin/env python3
"""
🔐 Sistema de Autenticación Robusto - VokaFlow Enterprise
Implementación completa con JWT, refresh tokens, rate limiting, y seguridad avanzada
"""

import os
import re
import secrets
import hashlib
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session
import redis
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
import ipaddress

# Configuración de logging
logger = logging.getLogger("vokaflow.auth.robust")

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"

# Configuración de tokens
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Configuración de seguridad
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_MINUTES = int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "15"))

# Redis para cache y sesiones
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

try:
    import redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis conectado para autenticación robusta")
except Exception as e:
    logger.warning(f"⚠️ Redis no disponible, usando almacenamiento en memoria: {e}")
    redis_client = None

# Contexto de encriptación
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Más seguro
)

# Security bearer
security = HTTPBearer()

# Almacenamiento en memoria como fallback
memory_store = {
    "failed_attempts": defaultdict(list),
    "active_sessions": {},
    "blacklisted_tokens": set(),
    "rate_limits": defaultdict(list)
}

@dataclass
class SecurityContext:
    """Contexto de seguridad del usuario"""
    user_id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    permissions: List[str]
    session_id: str
    ip_address: str
    user_agent: str
    last_activity: datetime
    created_at: datetime

class AuthenticationError(Exception):
    """Errores de autenticación personalizados"""
    pass

class AccountLockedError(AuthenticationError):
    """Cuenta bloqueada por intentos fallidos"""
    pass

class TokenExpiredError(AuthenticationError):
    """Token expirado"""
    pass

class InvalidTokenError(AuthenticationError):
    """Token inválido"""
    pass

# Modelos Pydantic
class UserRegister(BaseModel):
    """Modelo para registro de usuario"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    terms_accepted: bool = True
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username debe tener entre 3 y 50 caracteres')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password debe tener al menos {PASSWORD_MIN_LENGTH} caracteres')
        
        # Verificar complejidad
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password debe contener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Password debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password debe contener al menos un carácter especial')
        
        # Verificar patrones comunes
        common_patterns = ['password', '123456', 'qwerty', 'admin']
        if any(pattern in v.lower() for pattern in common_patterns):
            raise ValueError('Password no puede contener patrones comunes')
        
        return v

class UserLogin(BaseModel):
    """Modelo para login de usuario"""
    username: str
    password: str
    remember_me: bool = False
    device_name: Optional[str] = None

class TokenResponse(BaseModel):
    """Respuesta de autenticación con tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]
    permissions: List[str]
    session_id: str

class RefreshTokenRequest(BaseModel):
    """Solicitud de refresh token"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Solicitud de reseteo de contraseña"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Confirmación de reseteo de contraseña"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        # Usar la misma validación que en registro
        return UserRegister.validate_password(v)

class ChangePasswordRequest(BaseModel):
    """Cambio de contraseña"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        return UserRegister.validate_password(v)

class RobustAuthManager:
    """Gestor de autenticación robusto"""
    
    def __init__(self):
        self.redis = redis_client
        self.pwd_context = pwd_context
        
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generar clave de cache"""
        return f"vokaflow:auth:{prefix}:{identifier}"
    
    def _is_rate_limited(self, identifier: str, request_type: str = "login") -> bool:
        """Verificar rate limiting"""
        current_time = time.time()
        window_start = current_time - (RATE_LIMIT_WINDOW_MINUTES * 60)
        
        if self.redis:
            try:
                key = self._get_cache_key("rate_limit", f"{identifier}:{request_type}")
                pipe = self.redis.pipeline()
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(current_time): current_time})
                pipe.expire(key, RATE_LIMIT_WINDOW_MINUTES * 60)
                results = pipe.execute()
                
                current_requests = results[1]
                return current_requests >= RATE_LIMIT_REQUESTS
            except Exception as e:
                logger.error(f"Error en rate limiting: {e}")
        
        # Fallback a memoria
        requests = memory_store["rate_limits"][f"{identifier}:{request_type}"]
        requests = [req for req in requests if req > window_start]
        memory_store["rate_limits"][f"{identifier}:{request_type}"] = requests
        
        if len(requests) >= RATE_LIMIT_REQUESTS:
            return True
        
        requests.append(current_time)
        return False
    
    def _record_failed_attempt(self, username: str, ip_address: str):
        """Registrar intento fallido"""
        current_time = time.time()
        
        if self.redis:
            try:
                key = self._get_cache_key("failed_attempts", username)
                pipe = self.redis.pipeline()
                pipe.lpush(key, json.dumps({
                    "timestamp": current_time,
                    "ip_address": ip_address
                }))
                pipe.expire(key, LOCKOUT_DURATION_MINUTES * 60)
                pipe.execute()
            except Exception as e:
                logger.error(f"Error registrando intento fallido: {e}")
        else:
            # Fallback a memoria
            attempts = memory_store["failed_attempts"][username]
            cutoff_time = current_time - (LOCKOUT_DURATION_MINUTES * 60)
            attempts = [a for a in attempts if a > cutoff_time]
            attempts.append(current_time)
            memory_store["failed_attempts"][username] = attempts
    
    def _is_account_locked(self, username: str) -> bool:
        """Verificar si la cuenta está bloqueada"""
        current_time = time.time()
        cutoff_time = current_time - (LOCKOUT_DURATION_MINUTES * 60)
        
        if self.redis:
            try:
                key = self._get_cache_key("failed_attempts", username)
                attempts = self.redis.lrange(key, 0, -1)
                recent_attempts = []
                
                for attempt_json in attempts:
                    try:
                        attempt = json.loads(attempt_json)
                        if attempt["timestamp"] > cutoff_time:
                            recent_attempts.append(attempt)
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                return len(recent_attempts) >= MAX_LOGIN_ATTEMPTS
            except Exception as e:
                logger.error(f"Error verificando bloqueo de cuenta: {e}")
        
        # Fallback a memoria
        attempts = memory_store["failed_attempts"][username]
        recent_attempts = [a for a in attempts if a > cutoff_time]
        return len(recent_attempts) >= MAX_LOGIN_ATTEMPTS
    
    def _clear_failed_attempts(self, username: str):
        """Limpiar intentos fallidos tras login exitoso"""
        if self.redis:
            try:
                key = self._get_cache_key("failed_attempts", username)
                self.redis.delete(key)
            except Exception as e:
                logger.error(f"Error limpiando intentos fallidos: {e}")
        else:
            memory_store["failed_attempts"][username] = []
    
    def hash_password(self, password: str) -> str:
        """Hash seguro de contraseña"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID único
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crear refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        })
        
        return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verificar token JWT"""
        try:
            secret_key = SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                raise InvalidTokenError("Tipo de token incorrecto")
            
            # Verificar si el token está en la blacklist
            jti = payload.get("jti")
            if jti and self._is_token_blacklisted(jti):
                raise InvalidTokenError("Token revocado")
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token expirado")
        except jwt.JWTError as e:
            raise InvalidTokenError(f"Token inválido: {str(e)}")
    
    def _is_token_blacklisted(self, jti: str) -> bool:
        """Verificar si el token está en la blacklist"""
        if self.redis:
            try:
                key = self._get_cache_key("blacklist", jti)
                return self.redis.exists(key)
            except Exception as e:
                logger.error(f"Error verificando blacklist: {e}")
        
        return jti in memory_store["blacklisted_tokens"]
    
    def blacklist_token(self, jti: str, expire_time: Optional[int] = None):
        """Agregar token a la blacklist"""
        if not expire_time:
            expire_time = ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        if self.redis:
            try:
                key = self._get_cache_key("blacklist", jti)
                self.redis.setex(key, expire_time, "blacklisted")
            except Exception as e:
                logger.error(f"Error agregando a blacklist: {e}")
        else:
            memory_store["blacklisted_tokens"].add(jti)
    
    def create_session(self, user_data: Dict[str, Any], request: Request) -> str:
        """Crear sesión de usuario"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        if self.redis:
            try:
                key = self._get_cache_key("session", session_id)
                self.redis.setex(key, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, json.dumps(session_data))
            except Exception as e:
                logger.error(f"Error creando sesión: {e}")
        else:
            memory_store["active_sessions"][session_id] = session_data
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtener datos de sesión"""
        if self.redis:
            try:
                key = self._get_cache_key("session", session_id)
                session_data = self.redis.get(key)
                if session_data:
                    return json.loads(session_data)
            except Exception as e:
                logger.error(f"Error obteniendo sesión: {e}")
        
        return memory_store["active_sessions"].get(session_id)
    
    def update_session_activity(self, session_id: str):
        """Actualizar actividad de sesión"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data["last_activity"] = datetime.utcnow().isoformat()
            
            if self.redis:
                try:
                    key = self._get_cache_key("session", session_id)
                    self.redis.setex(key, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, json.dumps(session_data))
                except Exception as e:
                    logger.error(f"Error actualizando sesión: {e}")
            else:
                memory_store["active_sessions"][session_id] = session_data
    
    def invalidate_session(self, session_id: str):
        """Invalidar sesión"""
        if self.redis:
            try:
                key = self._get_cache_key("session", session_id)
                self.redis.delete(key)
            except Exception as e:
                logger.error(f"Error invalidando sesión: {e}")
        else:
            memory_store["active_sessions"].pop(session_id, None)
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP del cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Validar dirección IP"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    def generate_password_reset_token(self, user_id: str, email: str) -> str:
        """Generar token para reseteo de contraseña"""
        data = {
            "user_id": user_id,
            "email": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hora de validez
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_password_reset_token(self, token: str) -> Dict[str, Any]:
        """Verificar token de reseteo de contraseña"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "password_reset":
                raise InvalidTokenError("Token de tipo incorrecto")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token de reseteo expirado")
        except jwt.JWTError as e:
            raise InvalidTokenError(f"Token de reseteo inválido: {str(e)}")

# Instancia global del gestor de autenticación
auth_manager = RobustAuthManager()

# Dependencias de FastAPI
async def get_current_user_robust(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> SecurityContext:
    """Obtener usuario actual con autenticación robusta"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar rate limiting
        client_ip = auth_manager._get_client_ip(request) if request else "unknown"
        if auth_manager._is_rate_limited(client_ip, "api"):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
        
        # Verificar token
        payload = auth_manager.verify_token(credentials.credentials, "access")
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        session_id = payload.get("session_id")
        
        if not username or not user_id:
            raise credentials_exception
        
        # Verificar sesión
        session_data = auth_manager.get_session(session_id) if session_id else None
        if not session_data or not session_data.get("is_active"):
            raise credentials_exception
        
        # Actualizar actividad de sesión
        if session_id:
            auth_manager.update_session_activity(session_id)
        
        # Crear contexto de seguridad
        return SecurityContext(
            user_id=str(user_id),
            username=username,
            email=payload.get("email", ""),
            is_active=payload.get("is_active", True),
            is_verified=payload.get("is_verified", False),
            permissions=payload.get("permissions", []),
            session_id=session_id or "",
            ip_address=client_ip,
            user_agent=request.headers.get("User-Agent", "Unknown") if request else "Unknown",
            last_activity=datetime.utcnow(),
            created_at=datetime.fromisoformat(session_data.get("created_at", datetime.utcnow().isoformat()))
        )
        
    except (TokenExpiredError, InvalidTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error en autenticación: {e}")
        raise credentials_exception

async def get_current_active_user_robust(
    current_user: SecurityContext = Depends(get_current_user_robust)
) -> SecurityContext:
    """Verificar que el usuario esté activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def require_permissions(required_permissions: List[str]):
    """Decorador para requerir permisos específicos"""
    def dependency(current_user: SecurityContext = Depends(get_current_active_user_robust)):
        missing_permissions = set(required_permissions) - set(current_user.permissions)
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )
        return current_user
    return dependency

# Funciones de utilidad
def validate_user_registration(user_data: UserRegister, existing_usernames: List[str], existing_emails: List[str]) -> Dict[str, Any]:
    """Validar datos de registro de usuario"""
    errors = []
    
    # Verificar usuario existente
    if user_data.username.lower() in [u.lower() for u in existing_usernames]:
        errors.append("Username already exists")
    
    # Verificar email existente
    if user_data.email.lower() in [e.lower() for e in existing_emails]:
        errors.append("Email already registered")
    
    # Validaciones adicionales
    if len(user_data.username) < 3:
        errors.append("Username too short")
    
    if not user_data.terms_accepted:
        errors.append("Terms and conditions must be accepted")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def generate_secure_token() -> str:
    """Generar token seguro"""
    return secrets.token_urlsafe(32)

def log_security_event(event_type: str, user_id: Optional[str], details: Dict[str, Any]):
    """Registrar evento de seguridad"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "details": details
    }
    
    logger.info(f"Security Event: {json.dumps(event)}")
    
    # Aquí podrías enviar a un sistema de monitoreo externo
    # como Elasticsearch, Splunk, etc.

# Exportar componentes principales
__all__ = [
    "auth_manager",
    "UserRegister",
    "UserLogin", 
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ChangePasswordRequest",
    "SecurityContext",
    "get_current_user_robust",
    "get_current_active_user_robust",
    "require_permissions",
    "validate_user_registration",
    "log_security_event",
    "RobustAuthManager"
] 