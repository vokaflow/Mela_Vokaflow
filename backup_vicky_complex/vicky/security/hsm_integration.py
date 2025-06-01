"""
Módulo de integración con HSM (Hardware Security Module) para VokaFlow.

Este módulo proporciona una capa de abstracción para interactuar con HSMs,
permitiendo operaciones criptográficas de alta seguridad.
"""

import os
import logging
from typing import Dict, Any, Optional, Union

# Configuración de logging
logger = logging.getLogger("vicky.security.hsm")

class HSMManager:
    """
    Gestor de integración con Hardware Security Module (HSM).
    
    Proporciona una interfaz unificada para realizar operaciones criptográficas
    de alta seguridad utilizando módulos HSM.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hsm_type = config.get("hsm_type", "simulator")
        self.connection_string = config.get("connection_string", "")
        self.key_label = config.get("key_label", "vicky_master_key")
        
        # Inicializar el backend HSM apropiado
        self.hsm_backend = self._initialize_backend()
        
        if not self.hsm_backend:
            logger.warning("Usando simulador HSM en lugar de hardware real")
            self.hsm_backend = HSMSimulator()
    
    def _initialize_backend(self) -> Optional[Any]:
        """Inicializa el backend HSM según la configuración."""
        if self.hsm_type == "simulator":
            return HSMSimulator()
        
        elif self.hsm_type == "pkcs11":
            try:
                from .hsm_backends.pkcs11_backend import PKCS11Backend
                return PKCS11Backend(self.config)
            except ImportError:
                logger.error("No se pudo cargar el backend PKCS#11")
                return None
        
        elif self.hsm_type == "aws_cloudhsm":
            try:
                from .hsm_backends.aws_cloudhsm import AWSCloudHSMBackend
                return AWSCloudHSMBackend(self.config)
            except ImportError:
                logger.error("No se pudo cargar el backend AWS CloudHSM")
                return None
        
        elif self.hsm_type == "azure_keyvault":
            try:
                from .hsm_backends.azure_keyvault import AzureKeyVaultBackend
                return AzureKeyVaultBackend(self.config)
            except ImportError:
                logger.error("No se pudo cargar el backend Azure Key Vault")
                return None
        
        logger.error(f"Tipo de HSM no soportado: {self.hsm_type}")
        return None
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Cifra datos utilizando el HSM.
        
        Args:
            data: Datos a cifrar
            
        Returns:
            bytes: Datos cifrados
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            return self.hsm_backend.encrypt(data, self.key_label)
        except Exception as e:
            logger.error(f"Error al cifrar con HSM: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Descifra datos utilizando el HSM.
        
        Args:
            encrypted_data: Datos cifrados
            
        Returns:
            bytes: Datos descifrados
        """
        try:
            return self.hsm_backend.decrypt(encrypted_data, self.key_label)
        except Exception as e:
            logger.error(f"Error al descifrar con HSM: {str(e)}")
            raise
    
    def sign(self, data: Union[str, bytes]) -> bytes:
        """
        Firma datos utilizando el HSM.
        
        Args:
            data: Datos a firmar
            
        Returns:
            bytes: Firma digital
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            return self.hsm_backend.sign(data, self.key_label)
        except Exception as e:
            logger.error(f"Error al firmar con HSM: {str(e)}")
            raise
    
    def verify(self, data: Union[str, bytes], signature: bytes) -> bool:
        """
        Verifica una firma digital utilizando el HSM.
        
        Args:
            data: Datos originales
            signature: Firma a verificar
            
        Returns:
            bool: True si la firma es válida, False en caso contrario
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            return self.hsm_backend.verify(data, signature, self.key_label)
        except Exception as e:
            logger.error(f"Error al verificar firma con HSM: {str(e)}")
            return False
    
    def generate_key(self, key_type: str, key_size: int, key_label: Optional[str] = None) -> str:
        """
        Genera una nueva clave en el HSM.
        
        Args:
            key_type: Tipo de clave (RSA, EC, AES, etc.)
            key_size: Tamaño de la clave en bits
            key_label: Etiqueta para identificar la clave (opcional)
            
        Returns:
            str: Identificador o etiqueta de la clave generada
        """
        if not key_label:
            key_label = f"{self.key_label}_{key_type}_{key_size}"
        
        try:
            return self.hsm_backend.generate_key(key_type, key_size, key_label)
        except Exception as e:
            logger.error(f"Error al generar clave en HSM: {str(e)}")
            raise


class HSMSimulator:
    """
    Simulador de HSM para desarrollo y pruebas.
    
    Implementa las operaciones básicas de un HSM utilizando criptografía estándar.
    NO debe usarse en producción.
    """
    
    def __init__(self):
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        import base64
        
        self.backend = default_backend()
        self.keys = {}  # Almacenamiento simulado de claves
        
        # Generar clave RSA por defecto
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        self.keys["vicky_master_key"] = private_key
        
        # Generar clave AES por defecto
        aes_key = os.urandom(32)  # AES-256
        self.keys["vicky_master_key_aes"] = aes_key
        
        logger.warning("Usando simulador HSM - NO APTO PARA PRODUCCIÓN")
    
    def encrypt(self, data: bytes, key_label: str) -> bytes:
        """Cifra datos con la clave especificada."""
        if key_label not in self.keys:
            raise ValueError(f"Clave no encontrada: {key_label}")
        
        key = self.keys[key_label]
        
        if isinstance(key, rsa.RSAPrivateKey):
            # Cifrado RSA
            public_key = key.public_key()
            ciphertext = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return ciphertext
        else:
            # Cifrado AES
            iv = os.urandom(16)
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Añadir padding PKCS7
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return iv + ciphertext
    
    def decrypt(self, encrypted_data: bytes, key_label: str) -> bytes:
        """Descifra datos con la clave especificada."""
        if key_label not in self.keys:
            raise ValueError(f"Clave no encontrada: {key_label}")
        
        key = self.keys[key_label]
        
        if isinstance(key, rsa.RSAPrivateKey):
            # Descifrado RSA
            plaintext = key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return plaintext
        else:
            # Descifrado AES
            iv, ciphertext = encrypted_data[:16], encrypted_data[16:]
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Quitar padding PKCS7
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            return plaintext
    
    def sign(self, data: bytes, key_label: str) -> bytes:
        """Firma datos con la clave especificada."""
        if key_label not in self.keys:
            raise ValueError(f"Clave no encontrada: {key_label}")
        
        key = self.keys[key_label]
        
        if isinstance(key, rsa.RSAPrivateKey):
            # Firma RSA
            signature = key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature
        else:
            # Para claves simétricas, usar HMAC
            from cryptography.hazmat.primitives import hmac
            h = hmac.HMAC(key, hashes.SHA256(), backend=self.backend)
            h.update(data)
            return h.finalize()
    
    def verify(self, data: bytes, signature: bytes, key_label: str) -> bool:
        """Verifica una firma con la clave especificada."""
        if key_label not in self.keys:
            raise ValueError(f"Clave no encontrada: {key_label}")
        
        key = self.keys[key_label]
        
        try:
            if isinstance(key, rsa.RSAPrivateKey):
                # Verificación RSA
                public_key = key.public_key()
                public_key.verify(
                    signature,
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            else:
                # Para claves simétricas, verificar HMAC
                from cryptography.hazmat.primitives import hmac
                h = hmac.HMAC(key, hashes.SHA256(), backend=self.backend)
                h.update(data)
                h.verify(signature)
                return True
        except Exception:
            return False
    
    def generate_key(self, key_type: str, key_size: int, key_label: str) -> str:
        """Genera una nueva clave."""
        if key_type.upper() == "RSA":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=self.backend
            )
            self.keys[key_label] = private_key
        
        elif key_type.upper() == "AES":
            aes_key = os.urandom(key_size // 8)
            self.keys[key_label] = aes_key
        
        else:
            raise ValueError(f"Tipo de clave no soportado: {key_type}")
        
        return key_label
