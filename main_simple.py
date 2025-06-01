#!/usr/bin/env python3
"""
VokaFlow Backend Simplificado - Sistema de Mensajería
"""
import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vokaflow-simple")

# Configuración básica
class Settings:
    PROJECT_NAME: str = "VokaFlow API"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS = ["*"]
    ENVIRONMENT: str = "development"

settings = Settings()

# Crear aplicación
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para el sistema de mensajería VokaFlow",
    version=settings.PROJECT_VERSION,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar y registrar routers
try:
    from src.backend.routers.health import router as health_router
    app.include_router(health_router, prefix=f"{settings.API_PREFIX}/health", tags=["Health"])
    logger.info("✅ Health router cargado")
except ImportError as e:
    logger.warning(f"⚠️ Health router no disponible: {e}")

try:
    from src.backend.routers.conversations import router as conversations_router
    app.include_router(conversations_router, prefix=f"{settings.API_PREFIX}/conversations", tags=["💬 Messaging System"])
    logger.info("✅ Conversations router cargado")
except ImportError as e:
    logger.warning(f"⚠️ Conversations router no disponible: {e}")

try:
    from src.backend.websocket_manager import websocket_router
    app.include_router(websocket_router, tags=["💬 WebSocket Messaging"])
    logger.info("✅ WebSocket router cargado")
except ImportError as e:
    logger.warning(f"⚠️ WebSocket router no disponible: {e}")

try:
    from src.backend.routers.auth_robust import router as auth_robust_router
    app.include_router(auth_robust_router, prefix="/api", tags=["🔐 Auth"])
    logger.info("✅ Auth Robust router cargado")
except ImportError as e:
    logger.warning(f"⚠️ Auth Robust router no disponible: {e}")

@app.get("/")
async def root():
    return {
        "message": "VokaFlow Enterprise Messaging System",
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "endpoints": [
            "/api/health",
            "/api/conversations",
            "/ws/chat",
            "/docs"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "message": "VokaFlow Messaging API funcionando correctamente"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando VokaFlow Messaging System...")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 