import os
import time
import json
import logging
import datetime
import platform
import numpy as np
import cv2  # Importar cv2 directamente
from typing import Dict, List, Optional, Any

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('kinect_integration')

class KinectAPI:
    """
    Clase para la integración con dispositivos Kinect
    Soporta diferentes backends:
    - libfreenect (si está disponible)
    - PyKinect2 (para Windows)
    - Modo de simulación (para desarrollo y pruebas)
    """
    
    def __init__(self, simulation_mode=False):
        """
        Inicializa la API de Kinect
        
        Args:
            simulation_mode: Si es True, usa el modo de simulación sin hardware real
        """
        self.connected = False
        self.angle = 0  # Ángulo actual del motor, entre -27 y 27 grados
        self.accelerometer = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.last_capture = None
        self.simulation_mode = simulation_mode
        self.captures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "kinect_captures")
        
        # Detectar el sistema operativo
        self.system = platform.system()
        logger.info(f"Sistema operativo detectado: {self.system}")
        
        # Crear el directorio de capturas si no existe
        if not os.path.exists(self.captures_dir):
            os.makedirs(self.captures_dir, exist_ok=True)
            
        # Si estamos en modo de simulación, no intentamos cargar bibliotecas
        if simulation_mode:
            logger.info("Inicializado en modo de simulación. No se utilizará hardware real.")
            self.backend = "simulation"
            self.lib_available = True
            self.cv2_available = True
            self.cv2 = cv2  # Asignar cv2 en modo simulación
            return
            
        # Intentar importar OpenCV (necesario para procesar imágenes)
        try:
            self.cv2 = cv2  # Usar el cv2 importado globalmente
            logger.info("OpenCV cargado correctamente")
            self.cv2_available = True
        except Exception as e:
            logger.warning(f"No se pudo importar OpenCV: {str(e)}")
            self.cv2 = None
            self.cv2_available = False
            
        # En Linux intentamos usar libfreenect
        if self.system == "Linux":
            try:
                import freenect
                self.freenect = freenect
                logger.info("Biblioteca libfreenect cargada correctamente")
                self.backend = "freenect"
                self.lib_available = True
                return
            except ImportError:
                logger.warning("No se pudo importar libfreenect.")
                self.freenect = None
        
        # En Windows intentamos usar PyKinect2
        elif self.system == "Windows":
            try:
                from pykinect2 import PyKinectV2
                from pykinect2 import PyKinectRuntime
                self.PyKinectV2 = PyKinectV2
                self.PyKinectRuntime = PyKinectRuntime
                logger.info("Biblioteca PyKinect2 cargada correctamente")
                self.backend = "pykinect2"
                self.lib_available = True
                return
            except ImportError:
                logger.warning("No se pudo importar PyKinect2.")
        
        # Si no se pudo cargar ninguna biblioteca, usamos el modo de simulación
        logger.warning(f"No se encontró ninguna biblioteca compatible para {self.system}. Usando modo de simulación.")
        self.backend = "simulation"
        self.lib_available = True
        self.simulation_mode = True
            
    def initialize(self) -> bool:
        """Inicializa la conexión con el dispositivo Kinect"""
        if self.simulation_mode:
            logger.info("Inicialización en modo de simulación")
            self.connected = True
            return True
            
        if not self.lib_available:
            logger.error("No se puede inicializar: ninguna biblioteca disponible")
            return False
            
        try:
            if self.backend == "freenect":
                # Inicializar libfreenect
                context, device = self.freenect.init()
                if not device:
                    logger.error("No se detectó ningún dispositivo Kinect")
                    return False
                    
                self.connected = True
                self.context = context
                self.device = device
                
                # Establecer el LED en verde para indicar que está listo
                self.freenect.set_led(self.device, self.freenect.LED_GREEN)
                
            elif self.backend == "pykinect2":
                # Inicializar PyKinect2
                self.kinect = self.PyKinectRuntime.PyKinectRuntime(
                    self.PyKinectV2.FrameSourceTypes_Color |
                    self.PyKinectV2.FrameSourceTypes_Depth
                )
                self.connected = True
            
            # Obtener el ángulo y datos del acelerómetro
            self.update_state()
            
            logger.info(f"Kinect inicializada correctamente usando backend: {self.backend}")
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Kinect: {str(e)}")
            self.connected = False
            return False
            
    def update_state(self) -> None:
        """Actualiza el estado del dispositivo (ángulo y acelerómetro)"""
        if self.simulation_mode:
            # En modo simulación no hacemos nada
            return
            
        if not self.connected or not self.lib_available:
            return
            
        try:
            if self.backend == "freenect":
                # Obtener el ángulo actual
                self.angle = self.freenect.get_tilt_degs(self.device)
                
                # Obtener datos del acelerómetro
                ax, ay, az = self.freenect.get_accel(self.device)
                self.accelerometer = {"x": ax, "y": ay, "z": az}
                
            elif self.backend == "pykinect2":
                # PyKinect2 no proporciona información de ángulo o acelerómetro
                # Mantener los valores predeterminados
                pass
                
        except Exception as e:
            logger.error(f"Error al actualizar el estado: {str(e)}")
            
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del dispositivo"""
        self.update_state()
        return {
            "connected": self.connected,
            "angle": self.angle,
            "accelerometer": self.accelerometer,
            "last_capture": self.last_capture,
            "backend": self.backend,
            "simulation_mode": self.simulation_mode
        }
        
    def look_at(self, position: float) -> Optional[int]:
        """
        Orienta la Kinect hacia una posición horizontal
        
        Args:
            position: Valor entre -1 y 1 donde:
                -1 = ángulo mínimo (-27 grados)
                0 = centro (0 grados)
                1 = ángulo máximo (27 grados)
        
        Returns:
            El ángulo establecido o None si falló
        """
        if self.simulation_mode:
            # En modo simulación, simplemente actualizamos el ángulo
            target_angle = int(position * 27)
            self.angle = target_angle
            logger.info(f"[SIMULACIÓN] Kinect orientada a {self.angle} grados")
            return self.angle
            
        if not self.connected or not self.lib_available:
            logger.error("No se puede orientar: dispositivo no conectado")
            return None
            
        try:
            # Convertir la posición (-1 a 1) a ángulo (-27 a 27)
            target_angle = int(position * 27)
            
            if self.backend == "freenect":
                # Establecer el ángulo
                self.freenect.set_tilt_degs(self.device, target_angle)
                time.sleep(1)  # Esperar a que el motor se mueva
                
                # Actualizar el estado
                self.update_state()
                
            elif self.backend == "pykinect2":
                # PyKinect2 no soporta cambio de ángulo
                logger.warning("PyKinect2 no soporta cambio de ángulo")
                self.angle = target_angle  # Simular el cambio
                
            logger.info(f"Kinect orientada a {self.angle} grados")
            return self.angle
        except Exception as e:
            logger.error(f"Error al orientar Kinect: {str(e)}")
            return None
            
    def look_up(self) -> bool:
        """Orienta la Kinect hacia arriba (25 grados)"""
        return self.look_at(25/27) is not None
        
    def look_down(self) -> bool:
        """Orienta la Kinect hacia abajo (-25 grados)"""
        return self.look_at(-25/27) is not None
        
    def look_center(self) -> bool:
        """Orienta la Kinect al centro (0 grados)"""
        return self.look_at(0) is not None
        
    def capture_image(self) -> Optional[str]:
        """
        Captura una imagen RGB y de profundidad con la Kinect
        
        Returns:
            Ruta de la imagen guardada o None si falló
        """
        if self.simulation_mode:
            # En modo simulación, generamos una imagen de prueba
            if not self.cv2_available:
                logger.error("No se puede capturar: OpenCV no disponible")
                return None
                
            # Crear imágenes de prueba
            width, height = 640, 480
            rgb_frame = np.zeros((height, width, 3), dtype=np.uint8)
            depth_frame = np.zeros((height, width), dtype=np.uint16)
            
            # Dibujar algunos patrones para simular una imagen
            for i in range(0, height, 10):
                rgb_frame[i:i+5, :] = [0, 0, 255]  # Líneas azules horizontales
                
            for i in range(0, width, 10):
                rgb_frame[:, i:i+5] = [0, 255, 0]  # Líneas verdes verticales
                
            # Dibujar un gradiente en la imagen de profundidad
            for i in range(height):
                depth_frame[i, :] = i * 65535 // height
                
            # Normalizar el mapa de profundidad para visualización
            depth_visual = self.cv2.normalize(depth_frame, None, 0, 255, self.cv2.NORM_MINMAX, dtype=self.cv2.CV_8U)
            depth_colormap = self.cv2.applyColorMap(depth_visual, self.cv2.COLORMAP_JET)
            
            # Crear timestamp para el nombre de archivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Guardar las imágenes
            rgb_path = os.path.join(self.captures_dir, f"kinect_rgb_{timestamp}.jpg")
            depth_path = os.path.join(self.captures_dir, f"kinect_depth_{timestamp}.jpg")
            
            self.cv2.imwrite(rgb_path, rgb_frame)
            self.cv2.imwrite(depth_path, depth_colormap)
            
            # Actualizar último timestamp de captura
            self.last_capture = timestamp
            
            logger.info(f"[SIMULACIÓN] Imágenes capturadas y guardadas: {rgb_path}, {depth_path}")
            return rgb_path
            
        if not self.connected or not self.lib_available:
            logger.error("No se puede capturar: dispositivo no conectado")
            return None
            
        if not self.cv2_available:
            logger.error("No se puede capturar: OpenCV no disponible")
            return None
            
        try:
            if self.backend == "freenect":
                # Capturar frame RGB
                rgb_frame, _ = self.freenect.sync_get_video()
                
                # Capturar frame de profundidad
                depth_frame, _ = self.freenect.sync_get_depth()
                
                # Convertir el formato de color si es necesario
                rgb_frame = self.cv2.cvtColor(rgb_frame, self.cv2.COLOR_RGB2BGR)
                
            elif self.backend == "pykinect2":
                # Esperar a que haya un nuevo frame disponible
                if self.kinect.has_new_color_frame():
                    rgb_frame = self.kinect.get_last_color_frame()
                    rgb_frame = rgb_frame.reshape((self.kinect.color_frame_desc.Height, 
                                               self.kinect.color_frame_desc.Width, 4))
                    rgb_frame = rgb_frame[:,:,:3]  # Eliminar canal alfa
                else:
                    logger.error("No se pudo obtener el frame de color")
                    return None
                    
                if self.kinect.has_new_depth_frame():
                    depth_frame = self.kinect.get_last_depth_frame()
                    depth_frame = depth_frame.reshape((self.kinect.depth_frame_desc.Height, 
                                                   self.kinect.depth_frame_desc.Width))
                else:
                    logger.error("No se pudo obtener el frame de profundidad")
                    return None
            
            # Normalizar el mapa de profundidad para visualización
            depth_visual = self.cv2.normalize(depth_frame, None, 0, 255, self.cv2.NORM_MINMAX, dtype=self.cv2.CV_8U)
            depth_colormap = self.cv2.applyColorMap(depth_visual, self.cv2.COLORMAP_JET)
            
            # Crear timestamp para el nombre de archivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Guardar las imágenes
            rgb_path = os.path.join(self.captures_dir, f"kinect_rgb_{timestamp}.jpg")
            depth_path = os.path.join(self.captures_dir, f"kinect_depth_{timestamp}.jpg")
            
            self.cv2.imwrite(rgb_path, rgb_frame)
            self.cv2.imwrite(depth_path, depth_colormap)
            
            # Actualizar último timestamp de captura
            self.last_capture = timestamp
            
            logger.info(f"Imágenes capturadas y guardadas: {rgb_path}, {depth_path}")
            return rgb_path
        except Exception as e:
            logger.error(f"Error al capturar imagen: {str(e)}")
            return None
            
    def scan_room(self) -> List[str]:
        """
        Escanea la habitación capturando imágenes en diferentes ángulos
        
        Returns:
            Lista de rutas de las imágenes capturadas
        """
        captured_images = []
        
        # Definir los ángulos para el escaneo
        angles = [-25, -15, -5, 0, 5, 15, 25]
        
        for angle in angles:
            try:
                # Orientar la Kinect al ángulo específico
                self.look_at(angle/27)
                
                # Esperar a que el motor se estabilice
                time.sleep(1.5)
                
                # Capturar la imagen
                image_path = self.capture_image()
                
                if image_path:
                    captured_images.append(image_path)
                    
            except Exception as e:
                logger.error(f"Error durante el escaneo en ángulo {angle}: {str(e)}")
                
        # Volver a la posición central
        self.look_center()
        
        logger.info(f"Escaneo completado: {len(captured_images)} imágenes capturadas")
        return captured_images 