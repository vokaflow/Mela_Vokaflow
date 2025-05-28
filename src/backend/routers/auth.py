#!/usr/bin/env python3
"""
VokaFlow - Router de Autenticación
Maneja registro, login, tokens JWT y gestión de sesiones
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import asyncio
import json

# Configuración de logging
logger = logging.getLogger("vokaflow.auth")

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Configuración de Redis para sesiones
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = None

try:
    import redis
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Conexión a Redis establecida para gestión de sesiones")
except Exception as e:
    logger.warning(f"Redis no disponible, usando almacenamiento en memoria: {e}")
    redis_client = None

# Configuración de email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@vokaflow.com")

# Contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth-new/token")

# Router
router = APIRouter()

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]

class TokenRefresh(BaseModel):
    refresh_token: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    accept_terms: bool = True
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
        if not v.isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras y números')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: bool = False

# Funciones de utilidad
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crea un token de actualización"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoints básicos
@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    user_data: UserRegister,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Registra un nuevo usuario en el sistema"""
    try:
        logger.info(f"Intento de registro para usuario: {user_data.username}")
        
        # Verificar si el usuario ya existe (simulado)
        existing_users = ["admin", "test", "demo"]
        if user_data.username in existing_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Crear hash de contraseña
        password_hash = get_password_hash(user_data.password)
        
        # Simular creación de usuario
        user_id = hash(user_data.username) % 10000
        
        logger.info(f"Usuario {user_data.username} registrado exitosamente")
        
        return {
            "message": "Usuario registrado exitosamente",
            "user_id": user_id,
            "username": user_data.username,
            "email": user_data.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_data: UserLogin,
    request: Request
):
    """Autentica un usuario y devuelve tokens JWT"""
    try:
        logger.info(f"Intento de login para usuario: {user_data.username}")
        
        # Simular verificación de credenciales
        valid_users = {
            "admin": {"password": "Admin123!", "email": "admin@vokaflow.com", "id": 1},
            "test": {"password": "Test123!", "email": "test@vokaflow.com", "id": 2},
            "demo": {"password": "Demo123!", "email": "demo@vokaflow.com", "id": 3}
        }
        
        user_info = valid_users.get(user_data.username)
        if not user_info or not verify_password(user_data.password, get_password_hash(user_info["password"])):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        token_data = {
            "sub": user_data.username,
            "user_id": user_info["id"],
            "email": user_info["email"],
            "is_verified": True
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(data=token_data)
        
        logger.info(f"Usuario {user_data.username} autenticado exitosamente")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "user_info": {
                "id": user_info["id"],
                "username": user_data.username,
                "email": user_info["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al autenticar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """Endpoint compatible con OAuth2 para obtener token de acceso"""
    user_data = UserLogin(username=form_data.username, password=form_data.password)
    return await login_user(user_data, request)

@router.get("/status")
async def auth_service_status():
    """Verifica el estado del servicio de autenticación"""
    redis_status = "connected" if redis_client else "disconnected"
    smtp_status = "configured" if SMTP_USER and SMTP_PASSWORD else "not_configured"
    
    return {
        "status": "operational",
        "version": "1.0.0",
        "components": {
            "jwt": "operational",
            "password_hashing": "operational",
            "redis_sessions": redis_status,
            "email_service": smtp_status
        },
        "metrics": {
            "active_sessions": 0,
            "total_users": 3,
            "verified_users": 3
        }
    }
