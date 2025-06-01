"""
Punto de entrada principal para la API de VokaFlow.
"""
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .tts_api import router as tts_router
from .voice_cloning_api import router as voice_cloning_router
# Importar otros routers según sea necesario

logger = logging.getLogger("vicky.api.main")

# Crear aplicación FastAPI
app = FastAPI(
    title="VokaFlow API",
    description="API para el sistema VokaFlow",
    version="0.2.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, esto debería ser más restrictivo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(tts_router)
app.include_router(voice_cloning_router)
# Incluir otros routers según sea necesario

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servidor está funcionando"""
    return {"message": "VokaFlow API"}

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    return {"status": "ok", "version": "0.2.0"}
