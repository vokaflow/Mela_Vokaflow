#!/usr/bin/env python3
"""
Configuración de Base de Datos - VokaFlow Backend
===============================================

Configuración centralizada de la base de datos y dependencias.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from databases import Database
import logging

logger = logging.getLogger("vokaflow.database")

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # URL por defecto para desarrollo
    DATABASE_URL = "postgresql://vokaflow:vokaflow@localhost/vokaflow"
    logger.warning("DATABASE_URL no configurada, usando URL de desarrollo")

# Corregir URL si está en formato postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Motor de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Instancia de databases para operaciones async
database = Database(DATABASE_URL)

def get_db() -> Session:
    """
    Dependencia para obtener sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_database():
    """Inicializa la conexión a la base de datos"""
    await database.connect()
    logger.info("✅ Conexión a base de datos establecida")

async def close_database():
    """Cierra la conexión a la base de datos"""
    await database.disconnect()
    logger.info("🔒 Conexión a base de datos cerrada")
