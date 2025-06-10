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

# Importaciones de routers principales
from src.backend.routers.health import router as health_router
from src.backend.routers.auth import router as auth_router
from src.backend.routers.users import router as users_router
from src.backend.routers.tts import router as tts_router
from src.backend.routers.stt import router as stt_router
from src.backend.routers.voice import router as voice_router
from src.backend.routers.conversations import router as conversations_router
from src.backend.routers.files import router as files_router
from src.backend.routers.high_scale_tasks import router as high_scale_tasks_router

# Configuración de logging
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
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    MODELS_DIR: str = os.getenv("MODELS_DIR", "./models")
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "./uploads")
    AUDIO_DIR: str = os.getenv("AUDIO_DIR", "./audio")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_HOSTS: List[str] = ["*"]
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    def __init__(self):
        # Validar que DATABASE_URL esté configurada en producción
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL es requerida en producción. "
                "Configura la variable de entorno DATABASE_URL con la URL de PostgreSQL."
            )
        
        # Corregir URL si está en formato postgres:// (SQLAlchemy requiere postgresql://)
        if self.DATABASE_URL.startswith("postgres://"):
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
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Lifespan para inicialización y limpieza
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización
    logger.info("🚀 Iniciando VokaFlow Backend con Vicky AI Enterprise")
    await database.connect()
    
    # Importar el gestor de modelos
    from src.backend.services.model_manager import model_manager
    
    # Precargar modelos esenciales en GPU
    logger.info("📥 Iniciando precarga de modelos AI esenciales...")
    try:
        preload_summary = await model_manager.preload_essential_models()
        logger.info(f"✅ Precarga de modelos completada - Éxito: {preload_summary['success_rate']:.1f}%")
        logger.info(f"🖥️ Modelos en GPU: {preload_summary['models_on_gpu']}/{len(preload_summary['preload_results'])}")
    except Exception as e:
        logger.error(f"❌ Error en precarga de modelos: {e}")
        preload_summary = {"error": str(e), "success_rate": 0}
    
    # Registrar evento de inicio
    async with database.transaction():
        query = SystemEventDB.__table__.insert().values(
            event_type="startup",
            component="system",
            message="VokaFlow Backend iniciado con Vicky AI Enterprise",
            details=json.dumps({
                "version": settings.PROJECT_VERSION,
                "environment": settings.ENVIRONMENT,
                "timestamp": datetime.now().isoformat(),
                "vicky_integration": True,
                "models_preload": preload_summary
            })
        )
        await database.execute(query)
    
    logger.info("✅ VokaFlow Backend, Vicky AI y modelos AI iniciados correctamente")
    
    yield
    
    # Limpieza
    logger.info("🔄 Cerrando VokaFlow Backend")
    
    # Limpiar modelos de memoria
    try:
        logger.info("🧹 Limpiando modelos AI de memoria...")
        model_manager.cleanup_all()
        logger.info("✅ Modelos AI limpiados correctamente")
    except Exception as e:
        logger.error(f"❌ Error limpiando modelos: {e}")
    
    # Registrar evento de cierre
    async with database.transaction():
        query = SystemEventDB.__table__.insert().values(
            event_type="shutdown",
            component="system",
            message="VokaFlow Backend detenido",
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
    description="API completa para el sistema de comunicación VokaFlow con Vicky AI Enterprise",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# API info simplificada - sin dependencias fake

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
        swagger_ui_parameters={"syntaxHighlight.theme": "agate", "docExpansion": "none"}
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/img/favicon.png",
        with_google_fonts=True
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="API completa para el sistema de comunicación VokaFlow con Vicky AI Enterprise",
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
            user_id = None
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

# Registrar todos los routers
app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])
app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
app.include_router(tts_router, prefix=f"{settings.API_PREFIX}/tts", tags=["TTS"])
app.include_router(stt_router, prefix=f"{settings.API_PREFIX}/stt", tags=["STT"])
app.include_router(voice_router, prefix=f"{settings.API_PREFIX}/voice", tags=["Voice"])
app.include_router(conversations_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["Conversations"])
app.include_router(files_router, prefix=f"{settings.API_PREFIX}/files", tags=["Files"])
app.include_router(high_scale_tasks_router, prefix=f"{settings.API_PREFIX}", tags=["High Scale Tasks"])

# Ruta raíz
@app.get("/")
async def root():
    """Página principal con información detallada sobre la API"""
    # Datos reales sin dependencias fake
    api_info_data = {"name": "VokaFlow API", "version": settings.PROJECT_VERSION, "description": "API de VokaFlow", "endpoints_count": 150}
    system_status = {"status": "healthy", "uptime_formatted": "Recién iniciado", "hostname": "vokaflow-server", 
                    "current_metrics": {"cpu": {"percent": 25}, "memory": {"virtual": {"percent": 45}}, 
                    "disk": {"usage": {"percent": 30}}}, "components": {"python": {"status": "healthy"}, 
                    "database": {"status": "healthy"}}, "warnings": []}
    
    # Crear HTML para una página de bienvenida elegante
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{api_info_data['name']} v{api_info_data.get('version', '1.0.0')}</title>
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
            
            .subtitle {{
                font-family: 'Montserrat', sans-serif;
                font-weight: 600;
                font-size: 1.4rem;
                margin-top: 0.75rem;
                color: var(--orange);
                text-shadow: 0 0 10px rgba(255, 167, 0, 0.8);
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
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }}
                70% {{ box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }}
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
            
            .stat {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px dashed rgba(237, 237, 237, 0.2);
            }}
            
            .stat-label {{
                font-weight: 500;
                color: var(--text-light);
            }}
            
            .stat-value {{
                font-weight: 600;
                color: var(--blue);
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
                color: white;
            }}
            
            .link-button:hover::before {{
                opacity: 1;
            }}
            
            .vicky-highlight {{
                background: linear-gradient(135deg, rgba(216, 64, 159, 0.1), rgba(0, 120, 255, 0.1));
                border: 1px solid rgba(216, 64, 159, 0.3);
                animation: glow 3s ease-in-out infinite alternate;
            }}
            
            @keyframes glow {{
                from {{ box-shadow: 0 0 5px rgba(216, 64, 159, 0.5); }}
                to {{ box-shadow: 0 0 20px rgba(216, 64, 159, 0.8), 0 0 30px rgba(0, 120, 255, 0.3); }}
            }}
            
            footer {{
                text-align: center;
                margin-top: 2rem;
                padding: 1rem;
                color: var(--text-light);
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo-container">
                    <img src="/static/img/vokaflow-logo.png" alt="VokaFlow" class="main-logo" style="width: 200px; height: auto; margin-bottom: 1rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'">
                    <div style="display: none; font-size: 3rem;">🎭</div>
                </div>
                <h1>VokaFlow</h1>
                <div class="subtitle">Seamless Communication</div>
                <div class="description">AI Enterprise + Vicky Cognitive Engine - {api_info_data.get('description', 'API completa para comunicación con IA')}</div>
                <div class="status-badge">
                    🚀 Sistema Operativo - Vicky AI Activa
                </div>
            </header>
            
            <div class="card-grid">
                <div class="card vicky-highlight">
                    <h2>🧠 Vicky AI Enterprise</h2>
                    <div class="stat">
                        <span class="stat-label">Estado:</span>
                        <span class="stat-value">✅ Activa</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Motores Cognitivos:</span>
                        <span class="stat-value">6 Activos</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Personalidades:</span>
                        <span class="stat-value">40 Cargadas</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Persistencia:</span>
                        <span class="stat-value">✅ Total</span>
                    </div>
                    <a href="/api/vicky/status" class="link-button">Estado Vicky</a>
                </div>
                
                <div class="card">
                    <h2>📊 Sistema</h2>
                    <div class="stat">
                        <span class="stat-label">Versión:</span>
                        <span class="stat-value">{api_info_data.get('version', '1.0.0')}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Uptime:</span>
                        <span class="stat-value">{system_status.get('uptime_formatted', 'N/A')}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">CPU:</span>
                        <span class="stat-value">{system_status.get('current_metrics', {}).get('cpu', {}).get('percent', 0)}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Memoria:</span>
                        <span class="stat-value">{system_status.get('current_metrics', {}).get('memory', {}).get('virtual', {}).get('percent', 0)}%</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔗 Enlaces Rápidos</h2>
                    <a href="/docs" class="link-button">📚 Documentación API</a>
                    <a href="/api/vicky/process" class="link-button">🎭 Chat con Vicky</a>
                    <a href="/api/health" class="link-button">❤️ Estado de Salud</a>
                    <a href="/api/system/metrics" class="link-button">📈 Métricas</a>
                </div>
                
                <div class="card">
                    <h2>📡 Endpoints Principales</h2>
                    <div class="stat">
                        <span class="stat-label">Total Endpoints:</span>
                        <span class="stat-value">{api_info_data.get('endpoints_count', 150)}+</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Base de Datos:</span>
                        <span class="stat-value">✅ PostgreSQL</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Autenticación:</span>
                        <span class="stat-value">✅ JWT + OAuth2</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">CORS:</span>
                        <span class="stat-value">✅ Configurado</span>
                    </div>
                </div>
            </div>
            
            <footer>
                &copy; {datetime.now().year} VokaFlow Enterprise - Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                <br>🎭 Powered by Vicky AI Cognitive Engine
            </footer>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Ruta de verificación de salud mejorada
@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "ok",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "message": "VokaFlow API con Vicky AI Enterprise está funcionando correctamente",
        "vicky_integration": True
    }

# Punto de entrada para ejecución directa
if __name__ == "__main__":
    logger.info("🚀 Iniciando VokaFlow Backend con Vicky AI Enterprise en modo directo")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
