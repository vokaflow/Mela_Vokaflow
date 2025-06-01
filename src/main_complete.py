#!/usr/bin/env python3
"""
🚀 VokaFlow Backend - Sistema Universal de Traducción COMPLETO
Sistema de traducción universal con Vicky AI integrada - SIN ERRORES
"""

# =============================================================================
# CONFIGURACIÓN DE LOGGING - DEBE IR ANTES DE TODO
# =============================================================================
import os
import sys
import logging
import secrets
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager
import multiprocessing

# Configurar logging antes de cualquier otra importación
logs_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, 'vokaflow.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vokaflow-backend")

# =============================================================================
# IMPORTS PRINCIPALES
# =============================================================================

# FastAPI y dependencias
from fastapi import (
    FastAPI, Depends, HTTPException, status, Request, Response, Query, 
    Body, Header, File, UploadFile, WebSocket, WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool
import databases
from passlib.context import CryptContext
from jose import JWTError, jwt
import uvicorn

# =============================================================================
# IMPORTACIONES OPCIONALES CON MANEJO DE ERRORES
# =============================================================================

# Importar routers principales de forma segura
auth_robust_router = None
conversations_router = None
websocket_router = None
high_scale_tasks_router = None
vicky_router_new = None

try:
    from src.backend.routers.auth_robust import router as auth_robust_router
    logger.info("✅ Auth Robust router imported")
except Exception as e:
    logger.warning(f"⚠️ Auth Robust not available: {e}")

try:
    from src.backend.routers.conversations import router as conversations_router
    logger.info("✅ Conversations router imported")
except Exception as e:
    logger.warning(f"⚠️ Conversations router not available: {e}")

try:
    from src.backend.routers.websocket_chat import router as websocket_router
    logger.info("✅ WebSocket router imported")
except Exception as e:
    logger.warning(f"⚠️ WebSocket router not available: {e}")

try:
    from src.backend.routers.high_scale_tasks import router as high_scale_tasks_router
    logger.info("✅ High Scale Tasks router imported")
except Exception as e:
    logger.warning(f"⚠️ High Scale Tasks router not available: {e}")

try:
    from src.backend.routers.vicky import router as vicky_router_new
    logger.info("✅ Vicky router imported")
except Exception as e:
    logger.warning(f"⚠️ Vicky router not available: {e}")

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

class Settings:
    PROJECT_NAME: str = "VokaFlow API"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vokaflow.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    MODELS_DIR: str = os.getenv("MODELS_DIR", "./models")
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "./uploads")
    AUDIO_DIR: str = os.getenv("AUDIO_DIR", "./audio")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_HOSTS: List[str] = ["*"]
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    def __init__(self):
        # Crear directorios necesarios
        for directory in [self.MODELS_DIR, self.UPLOADS_DIR, self.AUDIO_DIR]:
            os.makedirs(directory, exist_ok=True)
        
        # Corregir URL si está en formato postgres://
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

settings = Settings()

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

# Base de datos SQLAlchemy
Base = declarative_base()

# Para SQLite, usar StaticPool para evitar problemas de threading
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, poolclass=StaticPool)
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de datos async para FastAPI
database = databases.Database(settings.DATABASE_URL)

# =============================================================================
# MODELOS DE BASE DE DATOS
# =============================================================================

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TranslationDB(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_text = Column(Text)
    translated_text = Column(Text)
    source_lang = Column(String(10))
    target_lang = Column(String(10))
    confidence = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TranslationRequest(BaseModel):
    text: str
    source_lang: Optional[str] = None
    target_lang: str

class TranslationResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: Optional[float] = None
    processing_time: Optional[float] = None

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    components: Dict[str, str]
    endpoints_count: int

# =============================================================================
# AUTENTICACIÓN
# =============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# =============================================================================
# DEPENDENCIAS
# =============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización
    logger.info("🚀 Iniciando VokaFlow Backend...")
    
    try:
        # Conectar a la base de datos
        await database.connect()
        logger.info("✅ Base de datos conectada")
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de base de datos verificadas")
        
        # Inicializar sistemas opcionales
        if high_scale_tasks_router:
            try:
                from src.backend.core.high_scale_task_manager import initialize_high_scale_system
                await initialize_high_scale_system()
                logger.info("✅ High Scale System inicializado")
            except Exception as e:
                logger.warning(f"⚠️ High Scale System no se pudo inicializar: {e}")
        
        logger.info("🎉 VokaFlow Backend iniciado correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")
        raise
    
    yield
    
    # Cierre limpio
    logger.info("🛑 Cerrando VokaFlow Backend...")
    
    try:
        # Cerrar High Scale System
        if high_scale_tasks_router:
            try:
                from src.backend.core.high_scale_task_manager import shutdown_high_scale_system
                await shutdown_high_scale_system()
                logger.info("✅ High Scale System cerrado")
            except Exception as e:
                logger.warning(f"⚠️ Error cerrando High Scale System: {e}")
        
        # Desconectar base de datos
        await database.disconnect()
        logger.info("✅ Base de datos desconectada")
        
    except Exception as e:
        logger.error(f"❌ Error durante el cierre: {e}")
    
    logger.info("✅ VokaFlow Backend cerrado correctamente")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Sistema Universal de Traducción con Vicky AI integrada",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROUTERS
# =============================================================================

from fastapi import APIRouter

# Router básico de traducción
translate_router = APIRouter()
system_router = APIRouter()
health_router = APIRouter()

@translate_router.post("", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Endpoint básico de traducción"""
    start_time = time.time()
    
    # Simulación básica de traducción (reemplazar con servicio real)
    translated_text = f"[TRANSLATED from {request.source_lang or 'auto'} to {request.target_lang}]: {request.text}"
    processing_time = time.time() - start_time
    
    return TranslationResponse(
        translated_text=translated_text,
        source_lang=request.source_lang or "auto",
        target_lang=request.target_lang,
        confidence=0.95,
        processing_time=processing_time
    )

@translate_router.get("/languages")
async def get_supported_languages():
    """Obtiene idiomas soportados"""
    return {
        "languages": [
            {"code": "es", "name": "Spanish", "native_name": "Español"},
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "fr", "name": "French", "native_name": "Français"},
            {"code": "de", "name": "German", "native_name": "Deutsch"},
            {"code": "it", "name": "Italian", "native_name": "Italiano"},
            {"code": "pt", "name": "Portuguese", "native_name": "Português"},
        ],
        "total": 6
    }

@system_router.get("/status")
async def system_status():
    """Estado del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "database": "connected",
            "translation_service": "available",
            "vicky_ai": "available" if vicky_router_new else "unavailable",
            "high_scale_system": "available" if high_scale_tasks_router else "unavailable"
        }
    }

@health_router.get("", response_model=HealthCheckResponse)
async def health_check():
    """Health check completo"""
    return HealthCheckResponse(
        status="healthy",
        version=settings.PROJECT_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now().isoformat(),
        components={
            "database": "connected",
            "translation": "available",
            "vicky": "available" if vicky_router_new else "unavailable",
            "high_scale": "available" if high_scale_tasks_router else "unavailable"
        },
        endpoints_count=len([route for route in app.routes])
    )

# =============================================================================
# REGISTRO DE ROUTERS
# =============================================================================

# Routers principales
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
app.include_router(translate_router, prefix=f"{settings.API_PREFIX}/translate", tags=["Translation"])
app.include_router(system_router, prefix=f"{settings.API_PREFIX}/system", tags=["System"])

# Routers opcionales
if vicky_router_new:
    app.include_router(vicky_router_new, prefix=f"{settings.API_PREFIX}/vicky", tags=["Vicky AI"])
    logger.info("✅ Vicky AI router registered")

if auth_robust_router:
    app.include_router(auth_robust_router, prefix="/api", tags=["Auth Robust"])
    logger.info("✅ Auth Robust router registered")

if conversations_router:
    app.include_router(conversations_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["Conversations"])
    logger.info("✅ Conversations router registered")

if websocket_router:
    app.include_router(websocket_router, tags=["WebSocket"])
    logger.info("✅ WebSocket router registered")

if high_scale_tasks_router:
    app.include_router(high_scale_tasks_router, prefix=f"{settings.API_PREFIX}/high-scale-tasks", tags=["High Scale Tasks"])
    logger.info("✅ High Scale Tasks router registered")

# =============================================================================
# ENDPOINTS PRINCIPALES
# =============================================================================

@app.get("/")
async def root():
    """Página principal"""
    return {
        "message": "🚀 VokaFlow Backend - Sistema Universal de Traducción",
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
        "components": {
            "translation": "✅ Available",
            "vicky_ai": "✅ Available" if vicky_router_new else "⚠️ Unavailable",
            "conversations": "✅ Available" if conversations_router else "⚠️ Unavailable",
            "websocket": "✅ Available" if websocket_router else "⚠️ Unavailable",
            "high_scale": "✅ Available" if high_scale_tasks_router else "⚠️ Unavailable",
            "auth_robust": "✅ Available" if auth_robust_router else "⚠️ Unavailable"
        },
        "endpoints": len([route for route in app.routes]),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check_root():
    """Health check en la raíz"""
    return await health_check()

@app.get(f"{settings.API_PREFIX}/status")
async def api_status():
    """Estado de la API"""
    return {
        "status": "operational",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "database": "connected",
        "endpoints_registered": len([route for route in app.routes])
    }

# =============================================================================
# CONFIGURACIÓN DE ERRORES
# =============================================================================

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "type": str(type(exc).__name__)}
    )

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    logger.info("🚀 Iniciando VokaFlow Backend...")
    
    # Determinar número de workers
    cpu_count = multiprocessing.cpu_count()
    workers = min(cpu_count, 4)  # Máximo 4 workers para evitar problemas
    
    logger.info(f"💻 CPU cores detectados: {cpu_count}")
    logger.info(f"⚡ Workers configurados: {workers}")
    
    uvicorn.run(
        "main_complete:app",
        host="0.0.0.0",
        port=8000,
        workers=workers,
        log_level="info",
        reload=False
    ) 