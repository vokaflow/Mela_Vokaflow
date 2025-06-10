#!/usr/bin/env python3
"""
VickyAI - Servicio Independiente
Sistema Cognitivo Revolucionario con 40+ Personalidades
Puerto: 8001
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# FastAPI y dependencias
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('vicky_ai.log')
    ]
)
logger = logging.getLogger("vicky-ai")

# Importar el router de VickyAI
from VickyAI.api.router import router as vicky_router

# Configuración
class VickyAISettings:
    PROJECT_NAME: str = "VickyAI"
    PROJECT_VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    BACKEND_CORS_ORIGINS: list = ["*"]
    DEBUG: bool = os.getenv("VICKY_DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("VICKY_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("VICKY_PORT", "8001"))

settings = VickyAISettings()

# Lifespan para inicialización
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización
    logger.info("🧠 Iniciando VickyAI como servicio independiente")
    logger.info(f"🎭 Sistema Cognitivo Revolucionario - Puerto {settings.PORT}")
    
    yield
    
    # Limpieza
    logger.info("🔄 Cerrando VickyAI")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema Cognitivo Revolucionario con 40+ Personalidades - Servicio Independiente",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
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

# Registrar el router de VickyAI
app.include_router(vicky_router, prefix=settings.API_PREFIX, tags=["VickyAI"])

# Ruta raíz
@app.get("/")
async def root():
    """Página principal de VickyAI"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VickyAI - Sistema Cognitivo Independiente</title>
        <style>
            :root {{
                --magenta: #D8409F;
                --blue: #0078FF;
                --orange: #FFA700;
                --dark-bg: #121212;
                --text-color: #EDEDED;
                --neon-glow: 0 0 10px rgba(216, 64, 159, 0.8);
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                background: var(--dark-bg);
                color: var(--text-color);
                margin: 0;
                padding: 2rem;
                text-align: center;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                border: 1px solid var(--magenta);
                border-radius: 10px;
                background: linear-gradient(135deg, rgba(216, 64, 159, 0.1), rgba(0, 120, 255, 0.1));
                box-shadow: var(--neon-glow);
            }}
            
            h1 {{
                font-size: 3rem;
                background: linear-gradient(to right, var(--magenta), var(--blue));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
            }}
            
            .status {{
                font-size: 1.5rem;
                color: var(--orange);
                margin: 1rem 0;
            }}
            
            .info {{
                background: rgba(0, 0, 0, 0.3);
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                text-align: left;
            }}
            
            .links {{
                margin-top: 2rem;
            }}
            
            .link {{
                display: inline-block;
                margin: 0.5rem;
                padding: 0.75rem 1.5rem;
                background: var(--magenta);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: all 0.3s ease;
            }}
            
            .link:hover {{
                background: var(--blue);
                box-shadow: var(--neon-glow);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 VickyAI</h1>
            <div class="status">✅ Sistema Cognitivo Activo</div>
            
            <div class="info">
                <h3>🎭 Información del Sistema:</h3>
                <p><strong>Versión:</strong> {settings.PROJECT_VERSION}</p>
                <p><strong>Puerto:</strong> {settings.PORT}</p>
                <p><strong>Estado:</strong> Servicio Independiente</p>
                <p><strong>Personalidades:</strong> 40+ Disponibles</p>
                <p><strong>Motores Cognitivos:</strong> 14 Activos</p>
                <p><strong>Inicio:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
            
            <div class="links">
                <a href="/docs" class="link">📚 Documentación API</a>
                <a href="/api/vicky/status" class="link">📊 Estado del Sistema</a>
                <a href="/api/vicky/personalities" class="link">🎭 Personalidades</a>
                <a href="/api/vicky/metrics" class="link">📈 Métricas</a>
            </div>
            
            <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;">
                VickyAI - Sistema Cognitivo Revolucionario Independiente
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Endpoint de salud específico para VickyAI
@app.get("/health")
async def vicky_health():
    """Estado de salud de VickyAI"""
    return {
        "service": "VickyAI",
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "port": settings.PORT,
        "timestamp": datetime.now().isoformat(),
        "cognitive_system": "active",
        "personalities_count": 40,
        "independent_service": True
    }

# Punto de entrada
if __name__ == "__main__":
    logger.info(f"🚀 Iniciando VickyAI en puerto {settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
