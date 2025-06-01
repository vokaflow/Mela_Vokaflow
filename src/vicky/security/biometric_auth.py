"""
Módulo de autenticación biométrica para VokaFlow.

Este módulo proporciona funcionalidades para autenticación mediante
factores biométricos como voz, huella dactilar o reconocimiento facial.
"""

import os
import time
import json
import logging
import hashlib
import base64
from typing import Dict, Any, Optional, List, Tuple, Union

# Configuración de logging
logger = logging.getLogger("vicky.security.biometric")

class BiometricAuthenticator:
    """
    Autenticador basado en factores biométricos.
    
    Soporta múltiples modalidades biométricas y proporciona una interfaz
    unificada para el registro y verificación de identidades.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.modalities = config.get("modalities", ["voice"])
        self.min_confidence = config.get("min_confidence", 0.85)
        self.storage_path = config.get("storage_path", "data/biometric")
        self.liveness_detection = config.get("liveness_detection", True)
        
        # Asegurar que el directorio de almacenamiento existe
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Inicializar proveedores biométricos según modalidades configuradas
        self.providers = {}
        
        for modality in self.modalities:
            provider = self._initialize_provider(modality)
            if provider:
                self.providers[modality] = provider
        
        if not self.providers:
            logger.warning("No se pudo inicializar ningún proveedor biométrico")
    
    def _initialize_provider(self, modality: str) -> Optional[Any]:
        """Inicializa un proveedor biométrico según la modalidad."""
        if modality == "voice":
            try:
                from .biometric_providers.voice_recognition import VoiceRecognitionProvider
                return VoiceRecognitionProvider(self.config.get("voice_config", {}))
            except ImportError:
                logger.error("No se pudo cargar el proveedor de reconocimiento de voz")
                return None
        
        elif modality == "fingerprint":
            try:
                from .biometric_providers.fingerprint import FingerprintProvider
                return FingerprintProvider(self.config.get("fingerprint_config", {}))
            except ImportError:
                logger.error("No se pudo cargar el proveedor de huella dactilar")
                return None
        
        elif modality == "face":
            try:
                from .biometric_providers.facial_recognition import FacialRecognitionProvider
                return FacialRecognitionProvider(self.config.get("face_config", {}))
            except ImportError:
                logger.error("No se pudo cargar el proveedor de reconocimiento facial")
                return None
        
        logger.error(f"Modalidad biométrica no soportada: {modality}")
        return None
    
    def enroll(self, user_id: str, biometric_data: Dict[str, bytes]) -> Dict[str, bool]:
        """
        Registra datos biométricos para un usuario.
        
        Args:
            user_id: Identificador del usuario
            biometric_data: Diccionario con datos biométricos por modalidad
            
        Returns:
            Dict[str, bool]: Resultado del registro por modalidad
        """
        results = {}
        
        for modality, data in biometric_data.items():
            if modality in self.providers:
                try:
                    # Verificar liveness si está habilitado
                    if self.liveness_detection and not self._check_liveness(modality, data):
                        logger.warning(f"Detección de liveness fallida durante registro para usuario {user_id}, modalidad {modality}")
                        results[modality] = False
                        continue
                    
                    # Procesar y almacenar datos biométricos
                    provider = self.providers[modality]
                    template = provider.process_enrollment(data)
                    
                    # Guardar template
                    self._save_template(user_id, modality, template)
                    
                    results[modality] = True
                    logger.info(f"Registro biométrico exitoso para usuario {user_id}, modalidad {modality}")
                    
                except Exception as e:
                    logger.error(f"Error en registro biométrico para usuario {user_id}, modalidad {modality}: {str(e)}")
                    results[modality] = False
            else:
                logger.warning(f"Modalidad biométrica no disponible: {modality}")
                results[modality] = False
        
        return results
    
    def verify(self, user_id: str, biometric_data: Union[bytes, Dict[str, bytes]]) -> bool:
        """
        Verifica la identidad de un usuario mediante datos biométricos.
        
        Args:
            user_id: Identificador del usuario
            biometric_data: Datos biométricos o diccionario con datos por modalidad
            
        Returns:
            bool: True si la verificación es exitosa, False en caso contrario
        """
        # Si se proporciona un solo conjunto de datos, determinar la modalidad
        if isinstance(biometric_data, bytes):
            # Intentar determinar la modalidad automáticamente
            modality = self._detect_modality(biometric_data)
            if not modality:
                logger.error("No se pudo determinar la modalidad biométrica")
                return False
            
            biometric_data = {modality: biometric_data}
        
        # Verificar cada modalidad proporcionada
        results = []
        
        for modality, data in biometric_data.items():
            if modality in self.providers:
                try:
                    # Verificar liveness si está habilitado
                    if self.liveness_detection and not self._check_liveness(modality, data):
                        logger.warning(f"Detección de liveness fallida durante verificación para usuario {user_id}, modalidad {modality}")
                        results.append(False)
                        continue
                    
                    # Cargar template almacenado
                    template = self._load_template(user_id, modality)
                    if not template:
                        logger.warning(f"No se encontró template para usuario {user_id}, modalidad {modality}")
                        results.append(False)
                        continue
                    
                    # Verificar contra template
                    provider = self.providers[modality]
                    confidence = provider.verify(data, template)
                    
                    result = confidence >= self.min_confidence
                    results.append(result)
                    
                    logger.info(f"Verificación biométrica para usuario {user_id}, modalidad {modality}: {'exitosa' if result else 'fallida'} (confianza: {confidence:.2f})")
                    
                except Exception as e:
                    logger.error(f"Error en verificación biométrica para usuario {user_id}, modalidad {modality}: {str(e)}")
                    results.append(False)
            else:
                logger.warning(f"Modalidad biométrica no disponible: {modality}")
                results.append(False)
        
        # La verificación es exitosa si al menos una modalidad es verificada correctamente
        return any(results) if results else False
    
    def _detect_modality(self, data: bytes) -> Optional[str]:
        """Intenta determinar la modalidad biométrica a partir de los datos."""
        # Esta es una implementación simplificada
        # En un sistema real, se analizarían los datos para determinar el tipo
        
        # Intentar con cada proveedor disponible
        for modality, provider in self.providers.items():
            if hasattr(provider, "detect_format") and provider.detect_format(data):
                return modality
        
        return None
    
    def _check_liveness(self, modality: str, data: bytes) -> bool:
        """Verifica que los datos biométricos provienen de una persona viva."""
        if modality not in self.providers:
            return False
        
        provider = self.providers[modality]
        
        if hasattr(provider, "check_liveness"):
            try:
                return provider.check_liveness(data)
            except Exception as e:
                logger.error(f"Error en detección de liveness para modalidad {modality}: {str(e)}")
                return False
        
        # Si el proveedor no soporta detección de liveness, asumir verdadero
        return True
    
    def _save_template(self, user_id: str, modality: str, template: bytes) -> bool:
        """Guarda un template biométrico para un usuario."""
        try:
            # Crear directorio para el usuario si no existe
            user_dir = os.path.join(self.storage_path, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Guardar template
            template_path = os.path.join(user_dir, f"{modality}_template.dat")
            with open(template_path, 'wb') as f:
                f.write(template)
            
            return True
        except Exception as e:
            logger.error(f"Error al guardar template biométrico: {str(e)}")
            return False
    
    def _load_template(self, user_id: str, modality: str) -> Optional[bytes]:
        """Carga un template biométrico para un usuario."""
        try:
            template_path = os.path.join(self.storage_path, user_id, f"{modality}_template.dat")
            
            if not os.path.exists(template_path):
                return None
            
            with open(template_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error al cargar template biométrico: {str(e)}")
            return None
    
    def delete_user_data(self, user_id: str) -> bool:
        """Elimina todos los datos biométricos de un usuario."""
        try:
            import shutil
            user_dir = os.path.join(self.storage_path, user_id)
            
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
                logger.info(f"Datos biométricos eliminados para usuario {user_id}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error al eliminar datos biométricos: {str(e)}")
            return False


# Clase base para proveedores biométricos
class BaseBiometricProvider:
    """Clase base para proveedores de autenticación biométrica."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def process_enrollment(self, data: bytes) -> bytes:
        """Procesa datos biométricos para registro y genera un template."""
        raise NotImplementedError("Método no implementado")
    
    def verify(self, data: bytes, template: bytes) -> float:
        """Verifica datos biométricos contra un template y devuelve nivel de confianza."""
        raise NotImplementedError("Método no implementado")
    
    def check_liveness(self, data: bytes) -> bool:
        """Verifica que los datos biométricos provienen de una persona viva."""
        raise NotImplementedError("Método no implementado")
    
    def detect_format(self, data: bytes) -> bool:
        """Detecta si los datos están en un formato compatible con este proveedor."""
        raise NotImplementedError("Método no implementado")


# Implementación simulada de reconocimiento de voz
class VoiceRecognitionSimulator(BaseBiometricProvider):
    """Simulador de reconocimiento de voz para desarrollo y pruebas."""
    
    def process_enrollment(self, data: bytes) -> bytes:
        """Simula el procesamiento de una muestra de voz para registro."""
        # En un sistema real, esto extraería características de la voz
        # y generaría un modelo biométrico
        
        # Simulamos generando un hash de los datos
        template = hashlib.sha256(data).digest()
        return template
    
    def verify(self, data: bytes, template: bytes) -> float:
        """Simula la verificación de una muestra de voz."""
        # En un sistema real, esto compararía las características de la voz
        # con el modelo almacenado
        
        # Simulamos comparando el hash de los datos con el template
        data_hash = hashlib.sha256(data).digest()
        
        # Calcular similitud basada en bytes coincidentes
        similarity = sum(a == b for a, b in zip(data_hash, template)) / len(template)
        
        # Añadir algo de variabilidad para simular un sistema real
        import random
        similarity = max(0.0, min(1.0, similarity + random.uniform(-0.1, 0.1)))
        
        return similarity
    
    def check_liveness(self, data: bytes) -> bool:
        """Simula la detección de liveness en una muestra de voz."""
        # En un sistema real, esto analizaría patrones que indiquen
        # que la voz proviene de una persona viva y no de una grabación
        
        # Simulamos con una probabilidad alta de éxito
        import random
        return random.random() < 0.95
    
    def detect_format(self, data: bytes) -> bool:
        """Detecta si los datos parecen ser una muestra de voz."""
        # Implementación simplificada
        # En un sistema real, se verificaría el formato de audio
        
        # Verificar si los primeros bytes coinciden con formatos de audio comunes
        if len(data) < 12:
            return False
        
        # Verificar si parece WAV
        if data[:4] == b'RIFF' and data[8:12] == b'WAVE':
            return True
        
        # Verificar si parece MP3
        if data[:3] == b'ID3' or (data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
            return True
        
        # Otros formatos...
        
        return False
