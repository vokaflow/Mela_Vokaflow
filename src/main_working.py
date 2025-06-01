#!/usr/bin/env python3
"""
🚀 VokaFlow Backend - Versión Simplificada
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
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from databases import Database

# =============================================================================
# IMPORTS DE ROUTERS SEGUROS (solo los que existen y funcionan)
# =============================================================================
safe_routers = {}

# Intentar cargar routers uno por uno
router_imports = [
    ("health", "src.backend.routers.health"),
    ("auth", "src.backend.routers.auth"),
    ("users", "src.backend.routers.users"),
    ("translate", "src.backend.routers.translate"),
    ("vicky", "src.backend.routers.vicky"),
    ("dashboard", "src.backend.routers.dashboard"),
    ("tasks", "src.backend.routers.tasks"),
    ("system", "src.backend.routers.system"),
]

for router_name, module_path in router_imports:
    try:
        module = __import__(module_path, fromlist=['router'])
        safe_routers[router_name] = module.router
        logger.info(f"✅ Router {router_name} cargado")
    except Exception as e:
        logger.warning(f"⚠️ Router {router_name} no disponible: {e}")

# =============================================================================
# IMPORTS PROBLEMÁTICOS CON MANEJO DE ERRORES
# =============================================================================

# High Scale Tasks Router
high_scale_tasks_router = None
try:
    from src.backend.routers.high_scale_tasks import router as high_scale_tasks_router
    logger.info("✅ High Scale Tasks router loaded")
except Exception as e:
    logger.error(f"❌ High Scale Tasks router failed to load: {e}")

# =============================================================================
# CONFIGURACIÓN SIMPLE
# =============================================================================

class Settings:
    PROJECT_NAME: str = "VokaFlow API"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vokaflow.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()

# =============================================================================
# BASE DE DATOS SIMPLE
# =============================================================================
database = Database(settings.DATABASE_URL)

# =============================================================================
# LIFESPAN SIMPLIFICADO
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización
    logger.info("🚀 Iniciando VokaFlow Backend Simplificado...")
    
    try:
        # Conectar a la base de datos
        await database.connect()
        logger.info("✅ Base de datos conectada")
        
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
    description="Sistema Universal de Traducción VokaFlow con Vicky AI - Versión Simplificada",
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
# REGISTRO DE ROUTERS SEGUROS
# =============================================================================
for router_name, router in safe_routers.items():
    try:
        app.include_router(router, prefix=f"{settings.API_PREFIX}/{router_name}", tags=[router_name.title()])
        logger.info(f"✅ Router {router_name} registrado")
    except Exception as e:
        logger.warning(f"⚠️ Error registrando router {router_name}: {e}")

# High Scale Tasks Router
if high_scale_tasks_router is not None:
    try:
        app.include_router(high_scale_tasks_router, prefix=f"{settings.API_PREFIX}/high-scale-tasks", tags=["High Scale Tasks"])
        logger.info("✅ High Scale Tasks router registrado")
    except Exception as e:
        logger.warning(f"⚠️ Error registrando High Scale Tasks router: {e}")

# =============================================================================
# ENDPOINTS BÁSICOS
# =============================================================================

@app.get("/")
async def root():
    """Página principal"""
    return {
        "message": "🚀 VokaFlow Backend Simplificado está funcionando",
        "version": settings.PROJECT_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "status": "✅ Operativo",
        "routers_loaded": list(safe_routers.keys()),
        "high_scale_available": high_scale_tasks_router is not None
    }

@app.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "routers": len(safe_routers),
        "high_scale": high_scale_tasks_router is not None
    }

@app.get("/api/v1/status")
async def api_status():
    """Estado de la API"""
    return {
        "api_status": "operational",
        "version": settings.PROJECT_VERSION,
        "routers_available": list(safe_routers.keys()),
        "high_scale_system": {
            "available": high_scale_tasks_router is not None,
            "status": "active" if high_scale_tasks_router is not None else "disabled"
        },
        "endpoints": {
            "health": "/health",
            "docs": f"{settings.API_PREFIX}/docs",
            "openapi": f"{settings.API_PREFIX}/openapi.json"
        }
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando VokaFlow Backend Simplificado...")
    uvicorn.run(
        "main_simple:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="info"
    ) 