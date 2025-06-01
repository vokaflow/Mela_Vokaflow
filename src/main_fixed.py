#!/usr/bin/env python3
"""
🚀 VokaFlow Backend - Sistema Universal de Traducción
Sistema de traducción universal con Vicky AI integrada - VERSIÓN CORREGIDA
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
import multiprocessing
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager
from pathlib import Path

# Configurar logging antes de cualquier otra importación
logs_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(logs_dir, 'vokaflow_backend.log'))
    ]
)
logger = logging.getLogger("vokaflow-backend")

# =============================================================================
# CONFIGURACIÓN DE ENTORNO
# =============================================================================
from dotenv import load_dotenv
load_dotenv()

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

# Pydantic y SQLAlchemy
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from databases import Database

# Autenticación
from passlib.context import CryptContext
from jose import JWTError, jwt

# Utilidades adicionales
import requests
import aiofiles
import psutil
import uuid

# =============================================================================
# IMPORTS DE MÓDULOS INTERNOS SEGUROS
# =============================================================================
# Monitoreo del sistema
from src.backend.core.monitoring import (
    get_api_info, get_performance_monitor, get_system_monitor, get_health_checker
)
from src.backend.core.task_manager import TaskManager

# =============================================================================
# IMPORTS DE ROUTERS SEGUROS
# =============================================================================
# Routers básicos siempre disponibles
from src.backend.routers.health import router as health_router
from src.backend.routers.auth import router as auth_router  
from src.backend.routers.users import router as users_router
from src.backend.routers.translate import router as translate_router
from src.backend.routers.vicky import router as vicky_router_new
from src.backend.routers.dashboard import router as dashboard_router
from src.backend.routers.tasks import router as tasks_router
from src.backend.routers.system import router as system_router

# Routers adicionales con manejo de errores
additional_routers = {}
try:
    from src.backend.routers.translations_dashboard import router as translations_dashboard_router
    additional_routers['translations_dashboard'] = translations_dashboard_router
    
    from src.backend.routers.tts import router as tts_router
    additional_routers['tts'] = tts_router
    
    from src.backend.routers.stt import router as stt_router
    additional_routers['stt'] = stt_router
    
    from src.backend.routers.voice import router as voice_router
    additional_routers['voice'] = voice_router
    
    from src.backend.routers.conversations import router as conversations_router
    additional_routers['conversations'] = conversations_router
    
    from src.backend.routers.models import router as models_router
    additional_routers['models'] = models_router
    
    from src.backend.routers.files import router as files_router
    additional_routers['files'] = files_router
    
    from src.backend.routers.analytics import router as analytics_router
    additional_routers['analytics'] = analytics_router
    
    from src.backend.routers.notifications import router as notifications_router
    additional_routers['notifications'] = notifications_router
    
    from src.backend.routers.admin import router as admin_router
    additional_routers['admin'] = admin_router
    
    from src.backend.routers.api_keys import router as api_keys_router
    additional_routers['api_keys'] = api_keys_router
    
    from src.backend.routers.webhooks import router as webhooks_router
    additional_routers['webhooks'] = webhooks_router
    
    from src.backend.routers.monitoring import router as monitoring_router
    additional_routers['monitoring'] = monitoring_router
    
    from src.backend.routers.kinect_dashboard import router as kinect_dashboard_router
    additional_routers['kinect_dashboard'] = kinect_dashboard_router
    
    logger.info(f"✅ {len(additional_routers)} routers adicionales cargados correctamente")
except Exception as e:
    logger.warning(f"⚠️ Algunos routers adicionales no se pudieron cargar: {e}")

# =============================================================================
# IMPORTS PROBLEMÁTICOS CON MANEJO DE ERRORES
# =============================================================================

# High Scale Tasks Router
try:
    from src.backend.routers.high_scale_tasks import router as high_scale_tasks_router
    logger.info("✅ High Scale Tasks router loaded")
except Exception as e:
    logger.error(f"❌ High Scale Tasks router failed to load: {e}")
    high_scale_tasks_router = None

# WebSocket Manager 
try:
    from src.backend.websocket_manager import websocket_router, connection_manager
    logger.info("✅ WebSocket Manager loaded")
except ImportError as e:
    logger.warning(f"⚠️ WebSocket Manager not available: {e}")
    websocket_router = None
    connection_manager = None

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
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
        # Corregir URL si está en formato postgres://
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
            logger.info("URL de base de datos corregida de postgres:// a postgresql://")

settings = Settings()

# Crear directorios necesarios
os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================
database = Database(settings.DATABASE_URL)
Base = declarative_base()

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

# =============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
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
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================
def get_db():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# LIFESPAN DE LA APLICACIÓN
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización
    logger.info("🚀 Iniciando VokaFlow Backend...")
    
    try:
        # Conectar a la base de datos
        await database.connect()
        logger.info("✅ Base de datos conectada")
        
        # Inicializar TaskManager
        task_manager = TaskManager()
        await task_manager.initialize()
        app.state.task_manager = task_manager
        logger.info("✅ TaskManager inicializado")
        
        # Inicializar High Scale System si está disponible
        if high_scale_tasks_router is not None:
            try:
                from src.backend.core.high_scale_task_manager import initialize_high_scale_system
                await initialize_high_scale_system()
                logger.info("✅ High Scale System inicializado")
            except Exception as e:
                logger.warning(f"⚠️ High Scale System no pudo inicializarse: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")
    
    yield
    
    # Limpieza
    logger.info("🛑 Cerrando VokaFlow Backend...")
    
    try:
        # Detener TaskManager
        if hasattr(app.state, 'task_manager'):
            await app.state.task_manager.shutdown()
            logger.info("✅ TaskManager detenido")
        
        # Detener High Scale System
        if high_scale_tasks_router is not None:
            try:
                from src.backend.core.high_scale_task_manager import shutdown_high_scale_system
                await shutdown_high_scale_system()
                logger.info("✅ High Scale System detenido")
            except Exception as e:
                logger.warning(f"⚠️ Error deteniendo High Scale System: {e}")
        
        # Desconectar base de datos
        await database.disconnect()
        logger.info("✅ Base de datos desconectada")
        
    except Exception as e:
        logger.error(f"❌ Error durante el cierre: {e}")

# =============================================================================
# CREACIÓN DE LA APLICACIÓN FASTAPI
# =============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Sistema Universal de Traducción VokaFlow con Vicky AI",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    lifespan=lifespan
)

# =============================================================================
# MIDDLEWARE
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REGISTRO DE ROUTERS
# =============================================================================

# Routers básicos
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(translate_router, prefix=f"{settings.API_PREFIX}/translate", tags=["Translation"])
app.include_router(vicky_router_new, prefix=f"{settings.API_PREFIX}/vicky", tags=["Vicky AI"])
app.include_router(dashboard_router, prefix=f"{settings.API_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(tasks_router, prefix=f"{settings.API_PREFIX}/tasks", tags=["Tasks"])
app.include_router(system_router, prefix=f"{settings.API_PREFIX}/system", tags=["System"])

# Routers adicionales
for name, router in additional_routers.items():
    try:
        app.include_router(router, prefix=f"{settings.API_PREFIX}/{name.replace('_', '-')}", tags=[name.title()])
        logger.info(f"✅ Router {name} registrado")
    except Exception as e:
        logger.warning(f"⚠️ Error registrando router {name}: {e}")

# High Scale Tasks Router
if high_scale_tasks_router is not None:
    try:
        app.include_router(high_scale_tasks_router, prefix=f"{settings.API_PREFIX}/high-scale-tasks", tags=["High Scale Tasks"])
        logger.info("✅ High Scale Tasks router registrado")
    except Exception as e:
        logger.warning(f"⚠️ Error registrando High Scale Tasks router: {e}")

# WebSocket Router
if websocket_router is not None:
    try:
        app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
        logger.info("✅ WebSocket router registrado")
    except Exception as e:
        logger.warning(f"⚠️ Error registrando WebSocket router: {e}")

# =============================================================================
# ENDPOINTS BÁSICOS
# =============================================================================

@app.get("/")
async def root():
    """Página principal"""
    return {
        "message": "🚀 VokaFlow Backend está funcionando",
        "version": settings.PROJECT_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "status": "✅ Operativo"
    }

@app.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando VokaFlow Backend...")
    uvicorn.run(
        "main_fixed:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="info"
    ) 