#!/usr/bin/env python3
"""
VokaFlow Backend - Sistema completo de API para servicios de voz, traducción e IA
"""
import os
import sys
import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Annotated
from enum import Enum
from pathlib import Path

# FastAPI y dependencias
from fastapi import (
    FastAPI, HTTPException, Depends, status, Request, Response, 
    BackgroundTasks, UploadFile, File, Form, Query, Path as PathParam,
    Security, Body, Header
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.routing import APIRouter

# Pydantic para validación
from pydantic import BaseModel, Field, EmailStr, validator, root_validator, HttpUrl, constr, confloat, conint, SecretStr

# Autenticación y seguridad
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib

# Base de datos
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from databases import Database

# Utilidades
import uvicorn
import aiofiles
from starlette.concurrency import run_in_threadpool
import uuid
from contextlib import asynccontextmanager

# Componentes personalizados
from system_monitor import get_system_monitor
from api_info import initialize_api_info, get_api_info

# Importaciones de routers
from src.backend.routers.health import router as health_router
from src.backend.routers.vicky import router as vicky_router
from src.backend.routers.auth import router as auth_router
from src.backend.routers.users import router as users_router
from src.backend.routers.translate import router as translate_router
from src.backend.routers.tts import router as tts_router
from src.backend.routers.stt import router as stt_router
from src.backend.routers.voice import router as voice_router
from src.backend.routers.conversations import router as conversations_router
from src.backend.routers.system import router as system_router
from src.backend.routers.models import router as models_router
from src.backend.routers.files import router as files_router
from src.backend.routers.analytics import router as analytics_router
from src.backend.routers.notifications import router as notifications_router
from src.backend.routers.admin import router as admin_router
from src.backend.routers.api_keys import router as api_keys_router
from src.backend.routers.webhooks import router as webhooks_router
from src.backend.routers.monitoring import router as monitoring_router
from src.backend.routers.kinect_dashboard import router as kinect_dashboard_router

# Importaciones de TODOS los routers
from src.backend.routers.health import router as health_router
from src.backend.routers.vicky import router as vicky_router
from src.backend.routers.auth import router as auth_router
from src.backend.routers.users import router as users_router
from src.backend.routers.translate import router as translate_router
from src.backend.routers.tts import router as tts_router
from src.backend.routers.stt import router as stt_router
from src.backend.routers.voice import router as voice_router
from src.backend.routers.conversations import router as conversations_router
from src.backend.routers.system import router as system_router
from src.backend.routers.models import router as models_router
from src.backend.routers.files import router as files_router
from src.backend.routers.analytics import router as analytics_router
from src.backend.routers.notifications import router as notifications_router
from src.backend.routers.admin import router as admin_router
from src.backend.routers.api_keys import router as api_keys_router
from src.backend.routers.webhooks import router as webhooks_router
from src.backend.routers.monitoring import router as monitoring_router
from src.backend.routers.kinect_dashboard import router as kinect_dashboard_router

# Importaciones de routers adicionales
from src.backend.routers.health import router as health_router
from src.backend.routers.vicky import router as vicky_router_new

# Importaciones de routers adicionales
from src.backend.routers.health import router as health_router
from src.backend.routers.vicky import router as vicky_router_new

# Configuración de logging
import os
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

# Configuración de entorno
from dotenv import load_dotenv
load_dotenv()

# Configuración de la aplicación
class Settings:
    PROJECT_NAME: str = "VokaFlow API"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
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
        # Corregir URL si está en formato postgres:// (SQLAlchemy requiere postgresql://)
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
            logging.info("URL de base de datos corregida de postgres:// a postgresql://")

settings = Settings()

# Asegurar que los directorios necesarios existen
os.makedirs("logs", exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.AUDIO_DIR, exist_ok=True)

# Configuración de base de datos
database = Database(settings.DATABASE_URL)
Base = declarative_base()

# Modelos de base de datos
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
    
    translations = relationship("TranslationDB", back_populates="user")
    voice_samples = relationship("VoiceSampleDB", back_populates="user")
    conversations = relationship("ConversationDB", back_populates="user")

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
    
    user = relationship("UserDB", back_populates="translations")

class VoiceSampleDB(Base):
    __tablename__ = "voice_samples"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    file_path = Column(String(255))
    duration = Column(Float)
    sample_rate = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("UserDB", back_populates="voice_samples")

class ConversationDB(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("UserDB", back_populates="conversations")
    messages = relationship("MessageDB", back_populates="conversation")

class MessageDB(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(50))  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    conversation = relationship("ConversationDB", back_populates="messages")

class AudioFileDB(Base):
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(255))
    duration = Column(Float)
    sample_rate = Column(Integer)
    file_size = Column(Integer)
    format = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CustomVoiceDB(Base):
    __tablename__ = "custom_voices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    model_path = Column(String(255))
    sample_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class APIMetricsDB(Base):
    __tablename__ = "api_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time = Column(Float)  # en milisegundos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class SystemEventDB(Base):
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50))  # startup, shutdown, error, warning, info
    component = Column(String(50))
    message = Column(Text)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Crear motor de base de datos y tablas
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic para API
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(User):
    password_hash: str

class Translation(BaseModel):
    id: Optional[int] = None
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

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

class Language(BaseModel):
    code: str
    name: str
    native_name: str
    flag: str
    voice_support: bool

class VoiceSample(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    file_path: str
    duration: float
    sample_rate: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VoiceSampleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CustomVoice(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    model_path: str
    sample_path: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomVoiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sample_id: int

class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: Optional[int] = None
    voice_name: Optional[str] = None
    language: str
    speed: Optional[float] = 1.0
    pitch: Optional[float] = 1.0

class SpeechToTextRequest(BaseModel):
    language: Optional[str] = None

class Message(BaseModel):
    id: Optional[int] = None
    role: str
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Conversation(BaseModel):
    id: Optional[int] = None
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    messages: List[Message] = []

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    role: str
    content: str

class VickyRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class VickyResponse(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class HemisphereBalanceRequest(BaseModel):
    action: str
    technical: float
    emotional: float

class HemisphereBalanceResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    version: str
    uptime: int
    loaded_models: List[str]
    memory_usage: Dict[str, int]
    processing_stats: Dict[str, Any]
    hemisphere_balance: Dict[str, float]

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    uptime: str
    components: Dict[str, Dict[str, Any]]
    system: Dict[str, Any]
    database: Dict[str, Any]
    api: Dict[str, Any]
    resources: Dict[str, Any]
    warnings: List[str] = []
    recommendations: List[str] = []

# Seguridad y autenticación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
api_key_header = APIKeyHeader(name="X-API-Key")
security = HTTPBearer()

def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user

async def validate_api_key(api_key: str = Depends(api_key_header), db: Session = Depends(get_db)):
    # Aquí implementaríamos la validación real de la API key
    # Por ahora, usamos una clave de prueba
    if api_key != "test_api_key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

# Lifespan para inicialización y limpieza
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización
    logger.info("Iniciando servidor VokaFlow Backend")
    await database.connect()
    
    # Registrar evento de inicio
    async with database.transaction():
        query = SystemEventDB.__table__.insert().values(
            event_type="startup",
            component="system",
            message="Sistema iniciado",
            details=json.dumps({
                "version": settings.PROJECT_VERSION,
                "environment": settings.ENVIRONMENT,
                "timestamp": datetime.now().isoformat()
            })
        )
        await database.execute(query)
    
    # Cargar modelos y recursos
    logger.info("Cargando modelos y recursos...")
    # Aquí cargaríamos los modelos de ML, TTS, etc.
    
    yield
    
    # Limpieza
    logger.info("Cerrando servidor VokaFlow Backend")
    
    # Registrar evento de cierre
    async with database.transaction():
        query = SystemEventDB.__table__.insert().values(
            event_type="shutdown",
            component="system",
            message="Sistema detenido",
            details=json.dumps({
                "version": settings.PROJECT_VERSION,
                "environment": settings.ENVIRONMENT,
                "timestamp": datetime.now().isoformat()
            })
        )
        await database.execute(query)
    
    await database.disconnect()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API completa para el sistema de comunicación VokaFlow",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# Inicializar información de API
api_info_instance = initialize_api_info(
    app_name=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API completa para el sistema de comunicación VokaFlow"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware adicionales
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rutas para documentación personalizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/img/favicon.png",
        swagger_ui_parameters={"syntaxHighlight.theme": "agate", "docExpansion": "none"},
        additional_css=["/static/custom.css"],
        additional_js=["/static/js/power_menu.js", "/static/js/power_checker.js"]
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/img/favicon.png",
        with_google_fonts=True,
        additional_css=["/static/custom.css"],
        additional_js=["/static/js/power_menu.js", "/static/js/power_checker.js"]
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="API completa para el sistema de comunicación VokaFlow",
        routes=app.routes,
    )

# Middleware para logging de solicitudes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Generar ID único para la solicitud
    request_id = str(uuid.uuid4())
    logger.info(f"Request {request_id} started: {request.method} {request.url.path}")
    
    # Procesar la solicitud
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = process_time * 1000
        
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Registrar métricas de API
        try:
            # Obtener información del usuario si está autenticado
            user_id = None
            # Aquí iría la lógica para extraer el user_id del token si está disponible
            
            # Obtener IP y User-Agent
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("User-Agent")
            
            # Crear registro de métricas
            async with database.transaction():
                query = APIMetricsDB.__table__.insert().values(
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time=process_time_ms,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                await database.execute(query)
        except Exception as e:
            logger.error(f"Error al registrar métricas de API: {e}")
        
        logger.info(
            f"Request {request_id} completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.4f}s"
        )
        return response
    except Exception as e:
        logger.error(f"Request {request_id} failed: {request.method} {request.url.path} - Error: {str(e)}")
        
        # Registrar evento de error
        try:
            async with database.transaction():
                query = SystemEventDB.__table__.insert().values(
                    event_type="error",
                    component="api",
                    message=f"Error en solicitud: {request.method} {request.url.path}",
                    details=json.dumps({
                        "error": str(e),
                        "request_id": request_id,
                        "timestamp": datetime.now().isoformat()
                    })
                )
                await database.execute(query)
        except Exception as db_error:
            logger.error(f"Error al registrar evento de error: {db_error}")
        
        raise

# Manejador de excepciones personalizado
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Registrar evento de error
    try:
        async with database.transaction():
            query = SystemEventDB.__table__.insert().values(
                event_type="error",
                component="system",
                message=f"Excepción no controlada: {str(exc)}",
                details=json.dumps({
                    "error": str(exc),
                    "path": request.url.path,
                    "method": request.method,
                    "timestamp": datetime.now().isoformat()
                })
            )
            await database.execute(query)
    except Exception as db_error:
        logger.error(f"Error al registrar evento de error: {db_error}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Crear routers
auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])
users_router = APIRouter(prefix="/users", tags=["Usuarios"])
translate_router = APIRouter(prefix="/translate", tags=["Traducción"])
vicky_router = APIRouter(prefix="/vicky", tags=["Vicky"])
tts_router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])
stt_router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])
voice_router = APIRouter(prefix="/voice", tags=["Voces"])
conversation_router = APIRouter(prefix="/conversations", tags=["Conversaciones"])
system_router = APIRouter(prefix="/system", tags=["Sistema"])

# Rutas de autenticación
@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Verificar si el email ya existe
    email_exists = db.query(UserDB).filter(UserDB.email == user.email).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    password_hash = get_password_hash(user.password)
    db_user = UserDB(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Rutas de usuarios
@users_router.get("/me", response_model=User)
async def read_users_me(current_user: UserDB = Depends(get_current_active_user)):
    return current_user

@users_router.put("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Actualizar campos si se proporcionan
    if user_update.email:
        current_user.email = user_update.email
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.password:
        current_user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@users_router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    current_user: UserDB = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Rutas de traducción
@translate_router.post("", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    current_user: Optional[UserDB] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Solicitud de traducción recibida: {request.text[:50]}...")
    
    try:
        # Aquí iría la lógica real para traducir el texto
        # Por ahora, simulamos una traducción
        start_time = time.time()
        
        # Simular detección de idioma si no se proporciona
        source_lang = request.source_lang
        if not source_lang:
            # Lógica simple de detección (en un sistema real sería más complejo)
            if any(c in "áéíóúñ¿¡" for c in request.text.lower()):
                source_lang = "es"
            else:
                source_lang = "en"
        
        # Simular traducción
        await asyncio.sleep(0.3)  # Simular tiempo de procesamiento
        
        # Traducción simulada muy básica
        if source_lang == "es" and request.target_lang == "en":
            translated_text = f"[EN] {request.text}"
        elif source_lang == "en" and request.target_lang == "es":
            translated_text = f"[ES] {request.text}"
        else:
            translated_text = f"[{request.target_lang.upper()}] {request.text}"
        
        processing_time = time.time() - start_time
        
        # Guardar la traducción en la base de datos
        db_translation = TranslationDB(
            user_id=current_user.id,
            source_text=request.text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=request.target_lang,
            confidence=0.85,
            processing_time=processing_time
        )
        db.add(db_translation)
        db.commit()
        
        return {
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": request.target_lang,
            "confidence": 0.85,
            "processing_time": processing_time
        }
    except Exception as e:
        logger.error(f"Error al traducir texto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al traducir el texto"
        )

@translate_router.get("/languages")
async def get_supported_languages():
    """
    Obtiene la lista de idiomas soportados
    """
    try:
        # En un sistema real, esto vendría de una base de datos o configuración
        languages = [
            {"code": "es", "name": "Español", "native_name": "Español", "flag": "🇪🇸", "voice_support": True},
            {"code": "en", "name": "Inglés", "native_name": "English", "flag": "🇬🇧", "voice_support": True},
            {"code": "fr", "name": "Francés", "native_name": "Français", "flag": "🇫🇷", "voice_support": True},
            {"code": "de", "name": "Alemán", "native_name": "Deutsch", "flag": "🇩🇪", "voice_support": True},
            {"code": "it", "name": "Italiano", "native_name": "Italiano", "flag": "🇮🇹", "voice_support": True},
            {"code": "pt", "name": "Portugués", "native_name": "Português", "flag": "🇵🇹", "voice_support": True},
            {"code": "ru", "name": "Ruso", "native_name": "Русский", "flag": "🇷🇺", "voice_support": False},
            {"code": "zh", "name": "Chino", "native_name": "中文", "flag": "🇨🇳", "voice_support": False},
            {"code": "ja", "name": "Japonés", "native_name": "日本語", "flag": "🇯🇵", "voice_support": False},
            {"code": "ko", "name": "Coreano", "native_name": "한국어", "flag": "🇰🇷", "voice_support": False}
        ]
        
        return languages
    except Exception as e:
        logger.error(f"Error al obtener idiomas soportados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la lista de idiomas"
        )

@translate_router.get("/stats")
async def get_translation_stats(current_user: UserDB = Depends(get_current_active_user)):
    """
    Obtiene estadísticas de traducción
    """
    try:
        # En un sistema real, esto vendría de una base de datos
        stats = {
            "totalTranslations": 1250,
            "languagePairs": [
                {"sourceLang": "es", "targetLang": "en", "count": 450},
                {"sourceLang": "en", "targetLang": "es", "count": 380},
                {"sourceLang": "fr", "targetLang": "es", "count": 120},
                {"sourceLang": "es", "targetLang": "fr", "count": 95},
                {"sourceLang": "de", "targetLang": "es", "count": 75}
            ],
            "averageProcessingTime": 0.35,  # segundos
            "mostTranslatedToday": {
                "language": "en",
                "count": 87
            }
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de traducción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas de traducción"
        )

@translate_router.get("/history", response_model=List[Translation])
async def get_translation_history(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de traducciones del usuario
    """
    translations = db.query(TranslationDB).filter(
        TranslationDB.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return translations

# Rutas para Vicky
@vicky_router.post("/process", response_model=VickyResponse)
async def process_vicky_request(
    request: VickyRequest,
    current_user: Optional[UserDB] = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Procesa una solicitud para Vicky
    """
    logger.info(f"Solicitud recibida para Vicky: {request.message[:50]}...")
    
    try:
        # Aquí iría la lógica real para procesar la solicitud con el cerebro de Vicky
        # Por ahora, simulamos una respuesta
        start_time = time.time()
        
        # Simulación de procesamiento
        await asyncio.sleep(0.5)  # Simular tiempo de procesamiento
        
        # Determinar balance de hemisferios basado en el tipo de mensaje
        technical_weight = 0.6
        emotional_weight = 0.4
        
        if "código" in request.message.lower() or "programa" in request.message.lower():
            technical_weight = 0.8
            emotional_weight = 0.2
        elif "siento" in request.message.lower() or "emoción" in request.message.lower():
            technical_weight = 0.3
            emotional_weight = 0.7
        
        processing_time = time.time() - start_time
        
        # Guardar la conversación si no existe
        conversation = None
        if request.session_id:
            conversation = db.query(ConversationDB).filter(
                ConversationDB.id == int(request.session_id)
            ).first()
        
        if not conversation and current_user:
            conversation = ConversationDB(
                user_id=current_user.id,
                title=request.message[:50]
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Guardar el mensaje del usuario
        if conversation:
            user_message = MessageDB(
                conversation_id=conversation.id,
                role="user",
                content=request.message
            )
            db.add(user_message)
            
            # Generar respuesta
            response_text = f"He procesado tu mensaje: '{request.message}'. ¿En qué más puedo ayudarte?"
            
            # Guardar respuesta de Vicky
            assistant_message = MessageDB(
                conversation_id=conversation.id,
                role="assistant",
                content=response_text
            )
            db.add(assistant_message)
            db.commit()
        
        response = {
            "response": f"He procesado tu mensaje: '{request.message}'. ¿En qué más puedo ayudarte?",
            "context": request.context,
            "metadata": {
                "processingTime": processing_time,
                "hemisphere": {
                    "technical": technical_weight,
                    "emotional": emotional_weight
                },
                "confidence": 0.92,
                "sessionId": str(conversation.id) if conversation else None
            }
        }
        
        return response
    except Exception as e:
        logger.error(f"Error al procesar solicitud para Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la solicitud"
        )

@vicky_router.get("/status", response_model=SystemStatus)
async def get_vicky_status():
    """
    Obtiene el estado actual de Vicky
    """
    try:
        # Aquí iría la lógica real para obtener el estado del sistema
        # Por ahora, simulamos una respuesta
        
        return {
            "status": "online",
            "version": "1.0.0",
            "uptime": 3600,  # 1 hora en segundos
            "loaded_models": ["qwen-7b", "nllb-200", "whisper-medium"],
            "memory_usage": {
                "total": 16384,  # MB
                "used": 8192,    # MB
                "free": 8192     # MB
            },
            "processing_stats": {
                "totalRequests": 150,
                "averageResponseTime": 0.8,  # segundos
                "requestsPerMinute": 2.5
            },
            "hemisphere_balance": {
                "technical": 0.6,
                "emotional": 0.4
            }
        }
    except Exception as e:
        logger.error(f"Error al obtener estado de Vicky: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el estado del sistema"
        )

# Rutas del sistema
@system_router.get("/metrics")
async def get_system_metrics(
    component: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    current_user: UserDB = Depends(get_current_active_superuser)
):
    """
    Obtiene métricas detalladas del sistema
    """
    try:
        system_monitor = get_system_monitor()
        return system_monitor.get_detailed_metrics(component, limit)
    except Exception as e:
        logger.error(f"Error al obtener métricas del sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener métricas del sistema"
        )

@system_router.post("/shutdown", status_code=status.HTTP_202_ACCEPTED)
async def shutdown_server():
    """
    Realiza un apagado seguro del servidor
    """
    logger.info("Iniciando apagado seguro del servidor...")
    # Ejecutar en un hilo separado para permitir que la respuesta se envíe
    async def shutdown_app():
        await asyncio.sleep(2)  # Esperar para que la respuesta se envíe
        import os, signal
        logger.info("Servidor apagado correctamente")
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)
    
    # Iniciar el proceso de apagado
    asyncio.create_task(shutdown_app())
    return {"message": "Servidor apagándose...", "status": "shutdown_initiated"}

@system_router.post("/restart", status_code=status.HTTP_202_ACCEPTED)
async def restart_server():
    """
    Reinicia el servidor de forma segura
    """
    logger.info("Iniciando reinicio seguro del servidor...")
    
    # Ejecutar en un hilo separado para permitir que la respuesta se envíe
    async def restart_app():
        await asyncio.sleep(2)  # Esperar para que la respuesta se envíe
        try:
            import os, sys, subprocess, signal
            
            # Guardar el PID actual
            pid = os.getpid()
            
            # Ruta al script actual
            script_path = os.path.abspath(sys.argv[0])
            python_executable = sys.executable
            
            # Directorio actual para el reinicio
            current_dir = os.getcwd()
            
            # Crear script más robusto para reiniciar
            restart_script = f"""#!/bin/bash
# Script para reiniciar VokaFlow Backend
echo "Esperando a que el proceso actual termine..."
sleep 5
cd {current_dir}
export PYTHONPATH={current_dir}
echo "Reiniciando servidor VokaFlow desde {script_path}..."
{python_executable} {script_path} > /tmp/vokaflow_restart.log 2>&1 &
echo "Servidor reiniciado en segundo plano. PID: $!"
"""
            
            # Escribir script de reinicio
            restart_script_path = "/tmp/vokaflow_restart.sh"
            with open(restart_script_path, "w") as f:
                f.write(restart_script)
            
            # Hacer ejecutable el script
            os.chmod(restart_script_path, 0o755)
            
            # Registrar evento de reinicio
            try:
                db = next(get_db())
                event = SystemEventDB(
                    event_type="restart",
                    component="system",
                    message="Servidor reiniciándose",
                    details=f"Reinicio iniciado desde PID {pid}"
                )
                db.add(event)
                db.commit()
                logger.info("Evento de reinicio registrado en la base de datos")
            except Exception as e:
                logger.error(f"Error al registrar evento de reinicio: {e}")
            
            # Ejecutar script de reinicio en segundo plano
            subprocess.Popen(["/bin/bash", restart_script_path], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            start_new_session=True)
            
            # Terminar el proceso actual después de iniciar el script de reinicio
            logger.info(f"Terminando proceso actual (PID: {pid}) para reiniciar...")
            os.kill(pid, signal.SIGTERM)
        except Exception as e:
            logger.error(f"Error durante el reinicio: {e}")
            # Aquí no podemos enviar una respuesta HTTP porque ya hemos enviado la respuesta 202
    
    # Iniciar el proceso de reinicio
    asyncio.create_task(restart_app())
    return {"message": "Servidor reiniciándose. El servicio estará disponible en breve.", "status": "restart_initiated"}

@system_router.post("/hibernate", status_code=status.HTTP_202_ACCEPTED)
async def hibernate_server():
    """
    Pone el servidor en modo hibernación (ahorro de recursos)
    """
    logger.info("Iniciando modo hibernación...")
    
    # En una implementación real, aquí se pausarían servicios no esenciales
    # y se liberarían recursos del sistema
    
    # Para esta simulación, simplemente registramos el evento
    try:
        # Registrar evento de hibernación
        db = next(get_db())
        event = SystemEventDB(
            event_type="hibernate",
            component="system",
            message="Servidor en modo hibernación",
            details="Servicios no esenciales pausados y recursos liberados"
        )
        db.add(event)
        db.commit()
        
        # Simular hibernación (en producción esto iniciaría procesos reales de hibernación)
        return {"message": "Servidor en modo hibernación", "status": "hibernate_success"}
    except Exception as e:
        logger.error(f"Error al hibernar el servidor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al hibernar el servidor"
        )

@system_router.get("/events")
async def get_system_events(
    event_type: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: UserDB = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """
    Obtiene eventos del sistema
    """
    try:
        query = db.query(SystemEventDB)
        
        if event_type:
            query = query.filter(SystemEventDB.event_type == event_type)
        
        if component:
            query = query.filter(SystemEventDB.component == component)
        
        events = query.order_by(SystemEventDB.timestamp.desc()).offset(skip).limit(limit).all()
        
        return events
    except Exception as e:
        logger.error(f"Error al obtener eventos del sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener eventos del sistema"
        )

@system_router.get("/api-metrics")
async def get_api_metrics(
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: UserDB = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """
    Obtiene métricas de la API
    """
    try:
        query = db.query(APIMetricsDB)
        
        if endpoint:
            query = query.filter(APIMetricsDB.endpoint.like(f"%{endpoint}%"))
        
        if method:
            query = query.filter(APIMetricsDB.method == method)
        
        if status_code:
            query = query.filter(APIMetricsDB.status_code == status_code)
        
        metrics = query.order_by(APIMetricsDB.timestamp.desc()).offset(skip).limit(limit).all()
        
        return metrics
    except Exception as e:
        logger.error(f"Error al obtener métricas de API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener métricas de API"
        )

# Registrar routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(translate_router, prefix=f"{settings.API_PREFIX}/translate")
# app.include_router(vicky_router, prefix=f"{settings.API_PREFIX}/vicky")
app.include_router(tts_router, prefix=f"{settings.API_PREFIX}/tts")
app.include_router(stt_router, prefix=f"{settings.API_PREFIX}/stt")
app.include_router(voice_router, prefix=f"{settings.API_PREFIX}/voice")
app.include_router(conversation_router, prefix=f"{settings.API_PREFIX}/conversations")
app.include_router(system_router, prefix=f"{settings.API_PREFIX}/system")
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health")

# Ruta raíz mejorada

# Registrar todos los routers
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
app.include_router(vicky_router, prefix=f"{settings.API_PREFIX}/vicky", tags=["Vicky"])
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(translate_router, prefix=f"{settings.API_PREFIX}/translate", tags=["Translate"])
app.include_router(tts_router, prefix=f"{settings.API_PREFIX}/tts", tags=["TTS"])
app.include_router(stt_router, prefix=f"{settings.API_PREFIX}/stt", tags=["STT"])
app.include_router(voice_router, prefix=f"{settings.API_PREFIX}/voice", tags=["Voice"])
app.include_router(conversations_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["Conversations"])
app.include_router(system_router, prefix=f"{settings.API_PREFIX}/system", tags=["System"])
app.include_router(models_router, prefix=f"{settings.API_PREFIX}/models", tags=["Models"])
app.include_router(files_router, prefix=f"{settings.API_PREFIX}/files", tags=["Files"])
app.include_router(analytics_router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])
app.include_router(api_keys_router, prefix=f"{settings.API_PREFIX}/api-keys", tags=["API Keys"])
app.include_router(webhooks_router, prefix=f"{settings.API_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(monitoring_router, prefix=f"{settings.API_PREFIX}/monitoring", tags=["Monitoring"])
app.include_router(kinect_dashboard_router, prefix=f"{settings.API_PREFIX}/kinect", tags=["Kinect Dashboard"])

@app.get("/")
async def root():
    """Página principal con información detallada sobre la API"""
    api_info_data = get_api_info().get_api_info()
    system_status = get_system_monitor().get_system_status()
    
    # Crear HTML para una página de bienvenida elegante
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{api_info_data['name']} v{api_info_data['version']}</title>
        <link rel="stylesheet" href="/static/custom.css">
        <script src="/static/js/power_menu.js"></script>
        <script src="/static/js/power_checker.js"></script>
        <style>
            :root {{
                --magenta: #D8409F;
                --blue: #0078FF;
                --orange: #FFA700;
                --dark-bg: #121212;
                --darker-bg: #0a0a0a;
                --light-gray: #EDEDED;
                --text-color: #EDEDED;
                --text-light: #CCCCCC;
                --success-color: #4caf50;
                --warning-color: #FFA700;
                --error-color: #D8409F;
                --border-radius: 8px;
                --neon-glow: 0 0 10px rgba(216, 64, 159, 0.8), 0 0 20px rgba(0, 120, 255, 0.4);
                --neon-blue-glow: 0 0 10px rgba(0, 120, 255, 0.8), 0 0 20px rgba(0, 120, 255, 0.4);
                --neon-orange-glow: 0 0 10px rgba(255, 167, 0, 0.8), 0 0 20px rgba(255, 167, 0, 0.4);
                --card-bg: #1E1E1E;
                --box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            }}
            
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Roboto:wght@400;500&family=Inter:wght@400;500;600&display=swap');
            
            body {{
                font-family: 'Montserrat', 'Roboto', sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                background: var(--dark-bg);
                background-image: 
                    radial-gradient(circle at 15% 25%, rgba(216, 64, 159, 0.15) 0%, transparent 35%),
                    radial-gradient(circle at 85% 75%, rgba(0, 120, 255, 0.15) 0%, transparent 35%),
                    radial-gradient(circle at 50% 50%, rgba(255, 167, 0, 0.1) 0%, transparent 45%);
                margin: 0;
                padding: 0;
                position: relative;
                overflow-x: hidden;
            }}
            
            body::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--magenta), var(--blue), var(--orange), transparent);
                box-shadow: var(--neon-glow);
                z-index: 1;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }}
            
            header {{
                text-align: center;
                margin-bottom: 2rem;
                padding: 2rem 1rem;
                background: linear-gradient(135deg, var(--darker-bg), var(--dark-bg));
                color: white;
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                border: 1px solid rgba(216, 64, 159, 0.3);
                position: relative;
                overflow: hidden;
            }}
            
            header::after {{
                content: "";
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, var(--blue), var(--magenta), var(--orange));
                box-shadow: var(--neon-glow);
            }}
            
            h1 {{
                margin: 0;
                font-size: 2.5rem;
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                background: linear-gradient(to right, var(--magenta), var(--blue));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: var(--neon-glow);
                letter-spacing: 0.5px;
            }}
            
            .logo-container {{
                margin-bottom: 1.5rem;
            }}
            
            .main-logo {{
                width: 120px;
                height: auto;
                filter: drop-shadow(0 0 10px var(--magenta)) drop-shadow(0 0 20px var(--blue));
                transition: all 0.5s ease;
            }}
            
            .main-logo:hover {{
                transform: scale(1.05);
                filter: drop-shadow(0 0 15px var(--magenta)) drop-shadow(0 0 30px var(--blue));
            }}
            
            .subtitle {{
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
                font-size: 1.4rem;
                margin-top: 0.75rem;
                color: var(--orange);
                text-shadow: var(--neon-orange-glow);
                letter-spacing: 1px;
            }}
            
            .description {{
                font-family: 'Inter', sans-serif;
                font-size: 1.1rem;
                margin-top: 0.75rem;
                opacity: 0.9;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
                line-height: 1.5;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 0.5rem 1rem;
                border-radius: 50px;
                font-weight: bold;
                margin-top: 1rem;
                background-color: var(--success-color);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            .status-badge.warning {{
                background-color: var(--warning-color);
            }}
            
            .status-badge.error {{
                background-color: var(--error-color);
            }}
            
            .card-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            
            .card {{
                background-color: var(--card-bg);
                border-radius: var(--border-radius);
                padding: 1.5rem;
                box-shadow: var(--box-shadow);
                transition: all 0.3s ease;
                border: 1px solid rgba(216, 64, 159, 0.1);
                position: relative;
                overflow: hidden;
            }}
            
            .card::after {{
                content: "";
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, var(--blue), var(--magenta));
                transform: scaleX(0);
                transform-origin: left;
                transition: transform 0.5s ease;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
                border-color: rgba(216, 64, 159, 0.3);
            }}
            
            .card:hover::after {{
                transform: scaleX(1);
                box-shadow: var(--neon-glow);
            }}
            
            .card h2 {{
                margin-top: 0;
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
                color: var(--magenta);
                border-bottom: 1px solid rgba(216, 64, 159, 0.2);
                padding-bottom: 0.75rem;
                text-shadow: 0 0 5px rgba(216, 64, 159, 0.3);
                letter-spacing: 0.5px;
            }}
            
            .card-content {{
                margin-top: 1rem;
            }}
            
            .stat {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px dashed #eee;
            }}
            
            .stat-label {{
                font-weight: 500;
                color: var(--text-light);
            }}
            
            .stat-value {{
                font-weight: 600;
            }}
            
            .features-section {{
                margin: 3rem 0;
                padding: 0 1rem;
            }}
            
            .features-card {{
                background-color: var(--card-bg);
                border-radius: var(--border-radius);
                padding: 2rem;
                box-shadow: var(--box-shadow);
                border: 1px solid rgba(216, 64, 159, 0.2);
                position: relative;
                overflow: hidden;
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .features-card h2 {{
                text-align: center;
                margin-top: 0;
                margin-bottom: 2rem;
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
                color: var(--magenta);
                text-shadow: 0 0 5px rgba(216, 64, 159, 0.3);
                letter-spacing: 0.5px;
                position: relative;
                display: inline-block;
                left: 50%;
                transform: translateX(-50%);
            }}
            
            .features-card h2::after {{
                content: "";
                position: absolute;
                bottom: -10px;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--magenta), var(--blue), var(--orange), transparent);
                box-shadow: var(--neon-glow);
            }}
            
            .features-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
            }}
            
            .feature-item {{
                display: flex;
                align-items: flex-start;
                padding: 1rem;
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: var(--border-radius);
                transition: all 0.3s ease;
                border: 1px solid rgba(216, 64, 159, 0.1);
            }}
            
            .feature-item:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                border-color: rgba(216, 64, 159, 0.3);
                background-color: rgba(216, 64, 159, 0.05);
            }}
            
            .feature-icon {{
                color: var(--blue);
                font-size: 1.2rem;
                margin-right: 1rem;
                text-shadow: var(--neon-blue-glow);
            }}
            
            .feature-text {{
                font-family: 'Inter', sans-serif;
                color: var(--light-gray);
                font-size: 1rem;
                line-height: 1.5;
            }}
            
            .link-button {{
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: var(--darker-bg);
                color: white;
                text-decoration: none;
                border-radius: var(--border-radius);
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
                margin-right: 1rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
                box-shadow: var(--box-shadow);
                border: 1px solid var(--magenta);
                position: relative;
                overflow: hidden;
                z-index: 1;
            }}
            
            .link-button::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, var(--magenta), var(--blue));
                z-index: -1;
                transition: opacity 0.3s ease;
                opacity: 0;
            }}
            
            .link-button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 0 15px var(--magenta), 0 0 25px rgba(0, 120, 255, 0.3);
            }}
            
            .link-button:hover::before {{
                opacity: 1;
            }}
            
            footer {{
                text-align: center;
                margin-top: 2rem;
                padding: 1rem;
                color: var(--text-light);
                font-size: 0.9rem;
            }}
            
            .warning-list {{
                background-color: #fff3e0;
                border-left: 4px solid var(--warning-color);
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0 var(--border-radius) var(--border-radius) 0;
            }}
            
            .warning-list h3 {{
                color: var(--warning-color);
                margin-top: 0;
            }}
            
            .warning-list ul {{
                margin-bottom: 0;
            }}
            
            @media (max-width: 768px) {{
                .card-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .container {{
                    padding: 1rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo-container">
                    <img src="/static/img/vokaflow-logo.png" alt="VokaFlow" class="main-logo" onerror="this.onerror=null; this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImdyYWQxIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdHlsZT0ic3RvcC1jb2xvcjojRDg0MDlGO3N0b3Atb3BhY2l0eToxIiAvPjxzdG9wIG9mZnNldD0iNTAlIiBzdHlsZT0ic3RvcC1jb2xvcjojMDA3OEZGO3N0b3Atb3BhY2l0eToxIiAvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3R5bGU9InN0b3AtY29sb3I6I0ZGQTM0ODtzdG9wLW9wYWNpdHk6MSIgLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48ZyB0cmFuc2Zvcm09Im1hdHJpeCgxLDAsMCwxLDAsMCkiPjxwYXRoIGQ9Ik05MCwzMCBDNjAsMzAgNDAsNTAgNDAsODAgQzQwLDExMCA2MCwxMzAgOTAsMTMwIEMxMTAsMTMwIDEzMCwxMTAgMTMwLDgwIEMxMzAsNTAgMTEwLDMwIDkwLDMwIFoiIHN0cm9rZT0idXJsKCNncmFkMSkiIHN0cm9rZS13aWR0aD0iNSIgZmlsbD0ibm9uZSIgLz48cGF0aCBkPSJNMTUwLDgwIEMxMjAsODAgMTAwLDEwMCAxMDAsMTMwIEMxMDAsMTYwIDEyMCwxODAgMTUwLDE4MCBDMTY1LDE4MCAxODAsMTYwIDE4MCwxMzAgQzE4MCwxMDAgMTY1LDgwIDE1MCw4MCBaIiBzdHJva2U9InVybCgjZ3JhZDEpIiBzdHJva2Utd2lkdGg9IjUiIGZpbGw9Im5vbmUiIC8+PC9nPjwvc3ZnPg=='">
                </div>
                <h1>{api_info_data['name']}</h1>
                <div class="subtitle">Seamless Communication</div>
                <div class="description">{api_info_data['description']}</div>
                <div class="status-badge {system_status['status']}">
                    Estado: {system_status['status'].upper()} - {system_status['status_message']}
                </div>
            </header>
            
            <div class="card-grid">
                <div class="card">
                    <h2>Información General</h2>
                    <div class="card-content">
                        <div class="stat">
                            <span class="stat-label">Versión:</span>
                            <span class="stat-value">{api_info_data['version']}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Tiempo activo:</span>
                            <span class="stat-value">{system_status['uptime_formatted']}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Entorno:</span>
                            <span class="stat-value">{settings.ENVIRONMENT.capitalize()}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Endpoints:</span>
                            <span class="stat-value">{api_info_data['endpoints_count']}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Servidor:</span>
                            <span class="stat-value">{system_status['hostname']}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Estado del Sistema</h2>
                    <div class="card-content">
                        <div class="stat">
                            <span class="stat-label">CPU:</span>
                            <span class="stat-value">{system_status['current_metrics']['cpu']['percent']}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Memoria:</span>
                            <span class="stat-value">{system_status['current_metrics']['memory']['virtual']['percent']}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Disco:</span>
                            <span class="stat-value">{system_status['current_metrics']['disk']['usage']['percent']}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Python:</span>
                            <span class="stat-value">{system_status['components']['python']['status']}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Base de datos:</span>
                            <span class="stat-value">{system_status['components']['database']['status']}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Documentación</h2>
                    <div class="card-content">
                        <p>Explore nuestra documentación completa para aprender a utilizar la API de VokaFlow:</p>
                        <a href="{api_info_data['documentation']['api_reference']}" class="link-button">Swagger UI</a>
                        <a href="{api_info_data['documentation']['redoc']}" class="link-button">ReDoc</a>
                        <a href="{api_info_data['documentation']['openapi_json']}" class="link-button">OpenAPI JSON</a>
                    </div>
                </div>
                
            </div>
            
            <div class="features-section">
                <div class="features-card">
                    <h2>Características Principales</h2>
                    <div class="features-grid">
                        {''.join(f'<div class="feature-item"><div class="feature-icon">✓</div><div class="feature-text">{feature}</div></div>' for feature in api_info_data['features']['core'])}
                    </div>
                </div>
            </div>
            
            <div class="card-grid">
            </div>
            
            {'<div class="warning-list"><h3>Advertencias</h3><ul>' + ''.join(f"<li>{warning}</li>" for warning in system_status['warnings']) + '</ul></div>' if system_status['warnings'] else ''}
            
            <div class="card">
                <h2>Últimos Cambios</h2>
                <div class="card-content">
                    {''.join(f'<div class="stat"><span class="stat-label">v{change["version"]} ({change["date"]}):</span><span class="stat-value">{change["changes"][0]}</span></div>' for change in api_info_data["changelog"][:3])}
                </div>
            </div>
            
            <footer>
                &copy; {datetime.now().year} VokaFlow - Todos los derechos reservados
                <div>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Ruta de verificación de salud mejorada
@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API
    """
    return {
        "status": "ok",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "message": "VokaFlow API está funcionando correctamente"
    }


# Registrar todos los routers
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
app.include_router(vicky_router, prefix=f"{settings.API_PREFIX}/vicky", tags=["Vicky"])
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(translate_router, prefix=f"{settings.API_PREFIX}/translate", tags=["Translate"])
app.include_router(tts_router, prefix=f"{settings.API_PREFIX}/tts", tags=["TTS"])
app.include_router(stt_router, prefix=f"{settings.API_PREFIX}/stt", tags=["STT"])
app.include_router(voice_router, prefix=f"{settings.API_PREFIX}/voice", tags=["Voice"])
app.include_router(conversations_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["Conversations"])
app.include_router(system_router, prefix=f"{settings.API_PREFIX}/system", tags=["System"])
app.include_router(models_router, prefix=f"{settings.API_PREFIX}/models", tags=["Models"])
app.include_router(files_router, prefix=f"{settings.API_PREFIX}/files", tags=["Files"])
app.include_router(analytics_router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(notifications_router, prefix=f"{settings.API_PREFIX}/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])
app.include_router(api_keys_router, prefix=f"{settings.API_PREFIX}/api-keys", tags=["API Keys"])
app.include_router(webhooks_router, prefix=f"{settings.API_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(monitoring_router, prefix=f"{settings.API_PREFIX}/monitoring", tags=["Monitoring"])
app.include_router(kinect_dashboard_router, prefix=f"{settings.API_PREFIX}/kinect", tags=["Kinect Dashboard"])

# Punto de entrada para ejecución directa

# Registro de routers adicionales
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health")

# Registro de routers adicionales
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health")
if __name__ == "__main__":
    logger.info("Iniciando servidor VokaFlow Backend en modo diagnóstico")
    # Forzar modo HTTP para diagnóstico
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Asegurarse de escuchar en TODAS las interfaces
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

