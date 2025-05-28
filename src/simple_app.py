from fastapi import FastAPI
import uvicorn
import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vokaflow-api")

# Añadir el directorio de scripts al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el router de Kinect
try:
    from backend.routers.kinect import router as kinect_router
    kinect_available = True
    logger.info("Módulo de Kinect cargado correctamente")
except ImportError as e:
    kinect_available = False
    logger.warning(f"No se pudo importar el módulo de Kinect: {e}")

app = FastAPI(title="VokaFlow API Test")

# Incluir el router de Kinect si está disponible
if kinect_available:
    app.include_router(kinect_router, prefix="/api")
    logger.info("Router de Kinect añadido a la API")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "VokaFlow API está funcionando correctamente"}

@app.get("/")
async def root():
    features = ["API Base"]
    if kinect_available:
        features.append("Kinect Integration")
    
    return {
        "message": "¡Bienvenido a VokaFlow API!",
        "features": features,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    logger.info("Iniciando servidor VokaFlow API en http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)