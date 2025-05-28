#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import logging
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db-test-app")

# Cargar variables de entorno
load_dotenv("env.development")

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # Corregir URL para SQLAlchemy
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info("URL corregida a formato postgresql://")

# Crear aplicación FastAPI
app = FastAPI(title="Test DB Connection")

# Crear motor de SQLAlchemy
try:
    engine = create_engine(DATABASE_URL) if DATABASE_URL else None
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Motor de base de datos inicializado")
except Exception as e:
    logger.error(f"Error al inicializar el motor de base de datos: {e}")
    engine = None

# Endpoints
@app.get("/")
async def root():
    return {"message": "API de prueba de conexión a Neon DB"}

@app.get("/health")
async def health():
    return {
        "status": "online",
        "database_url": DATABASE_URL.split("@")[1] if DATABASE_URL else "No configurada",
        "engine_initialized": engine is not None
    }

@app.get("/test-db")
async def test_db():
    if not engine:
        raise HTTPException(status_code=500, detail="Motor de base de datos no inicializado")
    
    try:
        # Probar conexión
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            version = connection.execute(text("SELECT version()")).scalar()
            
            # Listar tablas
            tables = connection.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            
            table_list = [table[0] for table in tables]
            
            return {
                "connection": "success",
                "result": result,
                "postgres_version": version,
                "tables": table_list,
                "tables_count": len(table_list)
            }
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")

# Para ejecutar directamente (no a través de uvicorn)
if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor de prueba de DB")
    uvicorn.run(app, host="0.0.0.0", port=8001) 