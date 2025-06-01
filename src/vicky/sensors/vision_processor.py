"""
Procesador de visión para Vicky - VISTA
Capacidades de análisis visual, detección de gestos y procesamiento de imágenes
"""

import os
import time
import logging
import threading
import queue
import numpy as np
import cv2
from typing import Dict, Any, Optional, Callable, List, Tuple
import asyncio

logger = logging.getLogger("vicky.sensors.vision")

class VickyVisionProcessor:
    """
    Procesador de visión para Vicky con capacidades de:
    - Detección y seguimiento de caras
    - Análisis de gestos y movimientos
    - Reconocimiento de expresiones faciales
    - Análisis de profundidad usando Kinect
    - Detección de presencia humana
    """
    
    def __init__(self, kinect_integration=None):
        self.kinect = kinect_integration
        self.is_processing = False
        self.frame_queue = queue.Queue(maxsize=10)  # Buffer limitado
        
        # Configuración de video
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        
        # Detectores de OpenCV
        self.face_cascade = None
        self.eye_cascade = None
        self.smile_cascade = None
        
        # Estado de detección
        self.current_faces = []
        self.current_gestures = []
        self.person_present = False
        self.last_person_detected = 0
        
        # Callbacks
        self.on_face_detected = None
        self.on_gesture_detected = None
        self.on_person_presence_changed = None
        self.on_expression_detected = None
        
        # Inicializar detectores
        self._initialize_detectors()
        
        logger.info("VickyVisionProcessor inicializado")
    
    def _initialize_detectors(self):
        """Inicializa los detectores de OpenCV"""
        try:
            # Intentar cargar clasificadores Haar pre-entrenados
            haar_face = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            haar_eye = cv2.data.haarcascades + 'haarcascade_eye.xml'
            haar_smile = cv2.data.haarcascades + 'haarcascade_smile.xml'
            
            if os.path.exists(haar_face):
                self.face_cascade = cv2.CascadeClassifier(haar_face)
                logger.info("✅ Detector de caras cargado")
            
            if os.path.exists(haar_eye):
                self.eye_cascade = cv2.CascadeClassifier(haar_eye)
                logger.info("✅ Detector de ojos cargado")
                
            if os.path.exists(haar_smile):
                self.smile_cascade = cv2.CascadeClassifier(haar_smile)
                logger.info("✅ Detector de sonrisas cargado")
                
        except Exception as e:
            logger.warning(f"Error cargando detectores OpenCV: {e}")
            logger.info("Usando detección simulada")
    
    def start_processing(self):
        """Inicia el procesamiento de video"""
        if self.is_processing:
            logger.warning("Ya se está procesando video")
            return
            
        self.is_processing = True
        logger.info("📹 Iniciando procesamiento de video...")
        
        # Iniciar hilos de procesamiento
        self.capture_thread = threading.Thread(target=self._video_capture_loop, daemon=True)
        self.processing_thread = threading.Thread(target=self._video_processing_loop, daemon=True)
        
        self.capture_thread.start()
        self.processing_thread.start()
        
        logger.info("✅ Procesamiento de video iniciado")
    
    def stop_processing(self):
        """Detiene el procesamiento de video"""
        self.is_processing = False
        logger.info("📷 Deteniendo procesamiento de video...")
    
    def _video_capture_loop(self):
        """Loop principal de captura de video"""
        while self.is_processing:
            try:
                # Capturar frame del Kinect
                if self.kinect and self.kinect.connected:
                    frame, depth_frame = self._capture_kinect_video()
                else:
                    # Simular captura de video
                    frame, depth_frame = self._simulate_video_capture()
                
                if frame is not None:
                    # Añadir frame a la cola si hay espacio
                    if not self.frame_queue.full():
                        self.frame_queue.put({
                            "frame": frame,
                            "depth": depth_frame,
                            "timestamp": time.time(),
                            "source": "kinect" if self.kinect and self.kinect.connected else "simulated"
                        })
                
                time.sleep(1/self.fps)  # Controlar FPS
                
            except Exception as e:
                logger.error(f"Error en captura de video: {e}")
                time.sleep(1)
    
    def _video_processing_loop(self):
        """Loop principal de procesamiento de video"""
        while self.is_processing:
            try:
                # Obtener frame de la cola
                if not self.frame_queue.empty():
                    frame_item = self.frame_queue.get()
                    self._process_frame(frame_item)
                else:
                    time.sleep(0.033)  # ~30 FPS
                    
            except Exception as e:
                logger.error(f"Error en procesamiento de video: {e}")
                time.sleep(1)
    
    def _process_frame(self, frame_item: Dict[str, Any]):
        """Procesa un frame de video"""
        frame = frame_item["frame"]
        depth_frame = frame_item["depth"]
        timestamp = frame_item["timestamp"]
        
        # 1. Detección de caras
        faces = self._detect_faces(frame)
        if faces != self.current_faces:
            self.current_faces = faces
            if self.on_face_detected:
                self.on_face_detected(faces, timestamp)
        
        # 2. Detección de presencia humana
        person_detected = len(faces) > 0 or self._detect_movement(frame, depth_frame)
        if person_detected != self.person_present:
            self.person_present = person_detected
            self.last_person_detected = timestamp if person_detected else self.last_person_detected
            
            if self.on_person_presence_changed:
                self.on_person_presence_changed(person_detected, timestamp)
        
        # 3. Análisis de gestos y expresiones
        if faces:
            gestures = self._analyze_gestures(frame, faces)
            expressions = self._analyze_expressions(frame, faces)
            
            if gestures and self.on_gesture_detected:
                self.on_gesture_detected(gestures, timestamp)
                
            if expressions and self.on_expression_detected:
                self.on_expression_detected(expressions, timestamp)
    
    def _capture_kinect_video(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Captura video del Kinect"""
        if not self.kinect or not self.kinect.connected:
            return None, None
            
        try:
            # En un sistema real, aquí capturaríamos video del Kinect
            # Por ahora simulamos
            frame = np.random.randint(0, 255, (self.frame_height, self.frame_width, 3), dtype=np.uint8)
            depth = np.random.randint(0, 4096, (self.frame_height, self.frame_width), dtype=np.uint16)
            
            return frame, depth
            
        except Exception as e:
            logger.error(f"Error capturando video del Kinect: {e}")
            return None, None
    
    def _simulate_video_capture(self) -> Tuple[np.ndarray, np.ndarray]:
        """Simula captura de video para desarrollo"""
        # Crear frame simulado con ocasionalmente una "cara"
        frame = np.random.randint(50, 200, (self.frame_height, self.frame_width, 3), dtype=np.uint8)
        
        # Ocasionalmente simular una cara
        if np.random.random() < 0.1:  # 10% de probabilidad
            # Dibujar un rectángulo que simule una cara
            x, y, w, h = 250, 150, 140, 180
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 200, 150), -1)
            cv2.circle(frame, (x+35, y+50), 10, (0, 0, 0), -1)  # Ojo izquierdo
            cv2.circle(frame, (x+105, y+50), 10, (0, 0, 0), -1)  # Ojo derecho
            cv2.ellipse(frame, (x+70, y+120), (30, 15), 0, 0, 180, (255, 100, 100), 2)  # Sonrisa
        
        # Simular depth frame
        depth = np.random.randint(500, 2000, (self.frame_height, self.frame_width), dtype=np.uint16)
        
        return frame, depth
    
    def _detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detecta caras en el frame"""
        faces = []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.face_cascade is not None:
                # Usar detector Haar real
                face_rects = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                
                for (x, y, w, h) in face_rects:
                    faces.append({
                        "x": int(x), "y": int(y), "width": int(w), "height": int(h),
                        "confidence": 0.9,
                        "center": (int(x + w/2), int(y + h/2))
                    })
            else:
                # Detección simulada basada en colores
                # Buscar regiones con color similar a piel
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_skin = np.array([0, 48, 80], dtype=np.uint8)
                upper_skin = np.array([20, 255, 255], dtype=np.uint8)
                
                mask = cv2.inRange(hsv, lower_skin, upper_skin)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 1000:  # Filtrar por área mínima
                        x, y, w, h = cv2.boundingRect(contour)
                        if w > 50 and h > 50:  # Tamaño mínimo de cara
                            faces.append({
                                "x": x, "y": y, "width": w, "height": h,
                                "confidence": 0.7,
                                "center": (x + w//2, y + h//2)
                            })
            
        except Exception as e:
            logger.error(f"Error detectando caras: {e}")
        
        return faces
    
    def _detect_movement(self, frame: np.ndarray, depth_frame: Optional[np.ndarray]) -> bool:
        """Detecta movimiento en el frame"""
        try:
            # Análisis simple de movimiento basado en varianza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Si hay mucha varianza, probablemente hay movimiento
            return variance > 100
            
        except Exception as e:
            logger.error(f"Error detectando movimiento: {e}")
            return False
    
    def _analyze_gestures(self, frame: np.ndarray, faces: List[Dict]) -> List[Dict[str, Any]]:
        """Analiza gestos en el frame"""
        gestures = []
        
        try:
            # Análisis básico de gestos basado en posición de las caras
            for face in faces:
                x, y = face["center"]
                
                # Determinar posición relativa en la pantalla
                if x < self.frame_width * 0.3:
                    gesture_type = "looking_left"
                elif x > self.frame_width * 0.7:
                    gesture_type = "looking_right"
                elif y < self.frame_height * 0.3:
                    gesture_type = "looking_up"
                elif y > self.frame_height * 0.7:
                    gesture_type = "looking_down"
                else:
                    gesture_type = "looking_center"
                
                gestures.append({
                    "type": gesture_type,
                    "face_id": id(face),
                    "confidence": 0.8,
                    "position": (x, y)
                })
                
        except Exception as e:
            logger.error(f"Error analizando gestos: {e}")
        
        return gestures
    
    def _analyze_expressions(self, frame: np.ndarray, faces: List[Dict]) -> List[Dict[str, Any]]:
        """Analiza expresiones faciales"""
        expressions = []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            for face in faces:
                x, y, w, h = face["x"], face["y"], face["width"], face["height"]
                face_region = gray[y:y+h, x:x+w]
                
                # Detectar sonrisa si tenemos el clasificador
                if self.smile_cascade is not None:
                    smiles = self.smile_cascade.detectMultiScale(
                        face_region, scaleFactor=1.8, minNeighbors=20
                    )
                    
                    if len(smiles) > 0:
                        expressions.append({
                            "type": "smile",
                            "face_id": id(face),
                            "confidence": 0.9,
                            "intensity": min(len(smiles) * 0.3, 1.0)
                        })
                else:
                    # Análisis simulado de expresiones
                    # Basado en variaciones en la región de la cara
                    face_variance = cv2.Laplacian(face_region, cv2.CV_64F).var()
                    
                    if face_variance > 150:
                        expressions.append({
                            "type": "animated",
                            "face_id": id(face),
                            "confidence": 0.7,
                            "intensity": min(face_variance / 200, 1.0)
                        })
                    elif face_variance < 50:
                        expressions.append({
                            "type": "calm",
                            "face_id": id(face),
                            "confidence": 0.6,
                            "intensity": 0.8
                        })
                
        except Exception as e:
            logger.error(f"Error analizando expresiones: {e}")
        
        return expressions
    
    def look_at_person(self, face_center: Tuple[int, int]):
        """Orienta el Kinect hacia una persona detectada"""
        if not self.kinect:
            return
            
        try:
            # Calcular posición relativa
            center_x = self.frame_width // 2
            offset_x = face_center[0] - center_x
            
            # Convertir a posición normalizada (-1 a 1)
            normalized_position = offset_x / center_x
            
            # Limitar el rango
            normalized_position = max(-1, min(1, normalized_position))
            
            # Orientar Kinect
            angle = self.kinect.look_at(normalized_position)
            if angle is not None:
                logger.info(f"👀 Kinect orientado hacia persona en ángulo {angle}°")
                
        except Exception as e:
            logger.error(f"Error orientando Kinect: {e}")
    
    def set_face_callback(self, callback: Callable[[List[Dict], float], None]):
        """Establece callback para detección de caras"""
        self.on_face_detected = callback
    
    def set_gesture_callback(self, callback: Callable[[List[Dict], float], None]):
        """Establece callback para detección de gestos"""
        self.on_gesture_detected = callback
    
    def set_presence_callback(self, callback: Callable[[bool, float], None]):
        """Establece callback para cambios de presencia"""
        self.on_person_presence_changed = callback
    
    def set_expression_callback(self, callback: Callable[[List[Dict], float], None]):
        """Establece callback para detección de expresiones"""
        self.on_expression_detected = callback
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del procesador de visión"""
        return {
            "is_processing": self.is_processing,
            "person_present": self.person_present,
            "faces_detected": len(self.current_faces),
            "last_person_detected": self.last_person_detected,
            "queue_size": self.frame_queue.qsize(),
            "kinect_connected": self.kinect.connected if self.kinect else False,
            "detectors_loaded": {
                "face_cascade": self.face_cascade is not None,
                "eye_cascade": self.eye_cascade is not None,
                "smile_cascade": self.smile_cascade is not None
            }
        } 