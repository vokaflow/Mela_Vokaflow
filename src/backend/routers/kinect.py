from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import sys
import os
import json
import logging
from typing import Dict, List, Optional, Any

# Añadir el directorio de scripts al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "scripts"))

# Importar la API de Kinect
try:
    from kinect_integration import KinectAPI
    kinect_api = KinectAPI()
    kinect_available = True
except ImportError:
    kinect_available = False
    logging.warning("No se pudo importar el módulo de integración de Kinect")

router = APIRouter(
    prefix="/api/kinect",
    tags=["kinect"],
    responses={404: {"description": "No encontrado"}},
)

# Modelos de datos
class KinectStatusResponse(BaseModel):
    connected: bool
    angle: int
    accelerometer: Dict[str, float]
    last_capture: Optional[str]

class LookAtRequest(BaseModel):
    position: float  # Valor entre -1 y 1

class KinectResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# Verificación de disponibilidad como middleware
@router.get("/status", response_model=KinectStatusResponse)
async def get_status():
    """Obtiene el estado actual de la Kinect"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        status = kinect_api.get_status()
        return KinectStatusResponse(
            connected=status["connected"],
            angle=status["angle"],
            accelerometer=status["accelerometer"],
            last_capture=status["last_capture"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el estado de la Kinect: {str(e)}")

@router.post("/initialize", response_model=KinectResponse)
async def initialize():
    """Inicializa la conexión con la Kinect"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        result = kinect_api.initialize()
        if result:
            return KinectResponse(
                success=True,
                message="Kinect inicializada correctamente",
                data={"connected": True}
            )
        else:
            return KinectResponse(
                success=False,
                message="No se pudo inicializar la Kinect",
                data={"connected": False}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al inicializar la Kinect: {str(e)}")

@router.post("/look-at", response_model=KinectResponse)
async def look_at(request: LookAtRequest):
    """Orienta la Kinect hacia una posición horizontal"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        if request.position < -1 or request.position > 1:
            raise HTTPException(status_code=400, detail="La posición debe estar entre -1 y 1")
        
        angle = kinect_api.look_at(request.position)
        if angle is not None:
            return KinectResponse(
                success=True,
                message=f"Kinect orientada correctamente a {angle}°",
                data={"angle": angle}
            )
        else:
            return KinectResponse(
                success=False,
                message="No se pudo orientar la Kinect",
                data=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al orientar la Kinect: {str(e)}")

@router.post("/look-up", response_model=KinectResponse)
async def look_up():
    """Orienta la Kinect hacia arriba"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        result = kinect_api.look_up()
        if result:
            return KinectResponse(
                success=True,
                message="Kinect orientada hacia arriba",
                data={"angle": 25}
            )
        else:
            return KinectResponse(
                success=False,
                message="No se pudo orientar la Kinect hacia arriba",
                data=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al orientar la Kinect: {str(e)}")

@router.post("/look-down", response_model=KinectResponse)
async def look_down():
    """Orienta la Kinect hacia abajo"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        result = kinect_api.look_down()
        if result:
            return KinectResponse(
                success=True,
                message="Kinect orientada hacia abajo",
                data={"angle": -25}
            )
        else:
            return KinectResponse(
                success=False,
                message="No se pudo orientar la Kinect hacia abajo",
                data=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al orientar la Kinect: {str(e)}")

@router.post("/look-center", response_model=KinectResponse)
async def look_center():
    """Orienta la Kinect al centro"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        result = kinect_api.look_center()
        if result:
            return KinectResponse(
                success=True,
                message="Kinect orientada al centro",
                data={"angle": 0}
            )
        else:
            return KinectResponse(
                success=False,
                message="No se pudo orientar la Kinect al centro",
                data=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al orientar la Kinect: {str(e)}")

@router.post("/capture", response_model=KinectResponse)
async def capture_image():
    """Captura una imagen con la Kinect"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        image_path = kinect_api.capture_image()
        if image_path:
            # Convertir ruta absoluta a relativa para la API
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            rel_path = os.path.relpath(image_path, base_dir)
            
            return KinectResponse(
                success=True,
                message="Imagen capturada correctamente",
                data={"image_path": rel_path}
            )
        else:
            return KinectResponse(
                success=False,
                message="No se pudo capturar la imagen",
                data=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al capturar imagen: {str(e)}")

@router.post("/scan", response_model=KinectResponse)
async def scan_room(background_tasks: BackgroundTasks):
    """Escanea la habitación capturando imágenes en diferentes ángulos"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        # Iniciar el escaneo en segundo plano para no bloquear la API
        background_tasks.add_task(kinect_api.scan_room)
        
        return KinectResponse(
            success=True,
            message="Escaneo de habitación iniciado en segundo plano",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar el escaneo: {str(e)}")

@router.get("/scan-results", response_model=KinectResponse)
async def get_scan_results():
    """Obtiene los resultados del último escaneo"""
    if not kinect_available:
        raise HTTPException(status_code=503, detail="El servicio de Kinect no está disponible")
    
    try:
        # En una implementación real, aquí se obtendrían los resultados del último escaneo
        # Por ahora, simplemente devolvemos el estado
        status = kinect_api.get_status()
        
        return KinectResponse(
            success=True,
            message="Estado actual de la Kinect",
            data=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los resultados del escaneo: {str(e)}") 