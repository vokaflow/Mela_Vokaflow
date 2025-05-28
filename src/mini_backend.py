#!/usr/bin/env python3
"""
Backend minimalista de VokaFlow
"""
import os
import sys
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configuración de logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.getcwd(), 'logs/vokaflow_backend.log'))
    ]
)
logger = logging.getLogger("vokaflow-backend")

app = FastAPI(title="VokaFlow API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas básicas
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de VokaFlow"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "VokaFlow API está funcionando correctamente"}

@app.get("/api/system/status")
async def system_status():
    return {
        "status": "online", 
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "uptime": "0h 0m 0s"
    }

if __name__ == "__main__":
    logger.info("Iniciando servidor VokaFlow Backend")
    uvicorn.run(
        "mini_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 