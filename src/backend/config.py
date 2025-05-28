#!/usr/bin/env python3
"""
Configuración para VokaFlow Backend
"""
import os
from typing import Optional

class Settings:
    """Configuración de la aplicación"""
    
    # API
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "VokaFlow API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API completa para el sistema de comunicación VokaFlow"
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vokaflow.db")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # Archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Servicios externos
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    def __init__(self):
        # Corregir URL de base de datos si es necesario
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Instancia global de configuración
settings = Settings()
