"""
Módulo de Seguridad Avanzada para VokaFlow

Este módulo implementa un sistema de seguridad multicapa que proporciona:
- Autenticación multifactor
- Detección de amenazas y anomalías
- Cifrado avanzado para datos sensibles
- Gestión de permisos y accesos
- Auditoría y logging de seguridad
"""

import os
import time
import json
import logging
import hashlib
import secrets
import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Configuración de logging
logger = logging.getLogger("vicky.security")

class SecurityLevel(Enum):
    """Niveles de seguridad para diferentes operaciones y datos."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class SecurityContext:
    """Contexto de seguridad para una sesión o transacción."""
    user_id: str
    session_id: str
    auth_level: SecurityLevel
    permissions: List[str]
    ip_address: str
    user_agent: str
    timestamp: float
    mfa_verified: bool = False
    risk_score: float = 0.0
    anomaly_detected: bool = False

class AuthenticationManager:
    """Gestiona la autenticación de usuarios con soporte para múltiples factores."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.secret_key = os.environ.get("VICKY_AUTH_SECRET", secrets.token_hex(32))
        self.token_expiry = config.get("token_expiry", 3600)  # 1 hora por defecto
        self.max_failed_attempts = config.get("max_failed_attempts", 5)
        self.lockout_duration = config.get("lockout_duration", 1800)  # 30 minutos
        self.failed_attempts = {}  # user_id -> (count, timestamp)
        self.mfa_required_level = SecurityLevel[config.get("mfa_required_level", "HIGH")]
        
        # Inicializar backend de autenticación biométrica si está configurado
        self.biometric_enabled = config.get("biometric_enabled", False)
        if self.biometric_enabled:
            try:
                from .biometric_auth import BiometricAuthenticator
                self.biometric_auth = BiometricAuthenticator(config.get("biometric_config", {}))
            except ImportError:
                logger.warning("Módulo de autenticación biométrica no disponible")
                self.biometric_enabled = False
    
    def authenticate(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[str]:
        """Autenticación básica con nombre de usuario y contraseña."""
        # Verificar si el usuario está bloqueado por intentos fallidos
        if self._is_account_locked(username):
            logger.warning(f"Intento de acceso a cuenta bloqueada: {username} desde {ip_address}")
            return None
        
        # Aquí iría la lógica para verificar las credenciales contra la base de datos
        # Por simplicidad, asumimos que la verificación es exitosa si las credenciales no están vacías
        if not username or not password:
            self._record_failed_attempt(username)
            return None
        
        # Simulamos una verificación exitosa
        user_id = f"user_{hashlib.sha256(username.encode()).hexdigest()[:8]}"
        
        # Generar token JWT
        payload = {
            "sub": user_id,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=self.token_expiry),
            "ip": hashlib.sha256(ip_address.encode()).hexdigest(),
            "auth_level": SecurityLevel.MEDIUM.value,
            "mfa_verified": False
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Registrar el evento de autenticación exitosa
        logger.info(f"Autenticación exitosa para usuario {username} desde {ip_address}")
        
        return token
    
    def verify_mfa(self, user_id: str, token: str, mfa_code: str) -> Optional[str]:
        """Verifica el segundo factor de autenticación y actualiza el token."""
        try:
            # Decodificar el token actual
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Verificar que el token pertenece al usuario correcto
            if payload["sub"] != user_id:
                logger.warning(f"Intento de verificación MFA con token de otro usuario: {user_id}")
                return None
            
            # Aquí iría la lógica para verificar el código MFA
            # Por simplicidad, asumimos que la verificación es exitosa si el código no está vacío
            if not mfa_code:
                return None
            
            # Actualizar el token con nivel de autenticación elevado
            payload["auth_level"] = SecurityLevel.HIGH.value
            payload["mfa_verified"] = True
            
            # Renovar la expiración
            payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.token_expiry)
            
            new_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            
            logger.info(f"Verificación MFA exitosa para usuario {user_id}")
            
            return new_token
            
        except jwt.PyJWTError as e:
            logger.error(f"Error al verificar MFA: {str(e)}")
            return None
    
    def verify_biometric(self, user_id: str, token: str, biometric_data: bytes) -> Optional[str]:
        """Verifica la autenticación biométrica y actualiza el token."""
        if not self.biometric_enabled:
            logger.error("Autenticación biométrica no habilitada")
            return None
        
        try:
            # Decodificar el token actual
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Verificar que el token pertenece al usuario correcto
            if payload["sub"] != user_id:
                logger.warning(f"Intento de verificación biométrica con token de otro usuario: {user_id}")
                return None
            
            # Verificar datos biométricos
            if not self.biometric_auth.verify(user_id, biometric_data):
                logger.warning(f"Verificación biométrica fallida para usuario {user_id}")
                return None
            
            # Actualizar el token con nivel de autenticación crítico
            payload["auth_level"] = SecurityLevel.CRITICAL.value
            payload["mfa_verified"] = True
            
            # Renovar la expiración
            payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.token_expiry)
            
            new_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            
            logger.info(f"Verificación biométrica exitosa para usuario {user_id}")
            
            return new_token
            
        except jwt.PyJWTError as e:
            logger.error(f"Error al verificar biometría: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en verificación biométrica: {str(e)}")
            return None
    
    def verify_token(self, token: str, ip_address: str) -> Optional[SecurityContext]:
        """Verifica un token JWT y devuelve el contexto de seguridad."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Verificar IP para prevenir robo de tokens
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
            if payload.get("ip") != ip_hash:
                logger.warning(f"Posible robo de token: IP original {payload.get('ip')}, IP actual {ip_hash}")
                return None
            
            # Crear contexto de seguridad
            context = SecurityContext(
                user_id=payload["sub"],
                session_id=payload.get("sid", secrets.token_hex(16)),
                auth_level=SecurityLevel(payload["auth_level"]),
                permissions=payload.get("permissions", []),
                ip_address=ip_address,
                user_agent=payload.get("ua", "Unknown"),
                timestamp=time.time(),
                mfa_verified=payload.get("mfa_verified", False)
            )
            
            return context
            
        except jwt.ExpiredSignatureError:
            logger.info("Token expirado")
            return None
        except jwt.PyJWTError as e:
            logger.error(f"Error al verificar token: {str(e)}")
            return None
    
    def _is_account_locked(self, username: str) -> bool:
        """Verifica si una cuenta está bloqueada por intentos fallidos."""
        if username not in self.failed_attempts:
            return False
        
        count, timestamp = self.failed_attempts[username]
        
        # Si ha superado el número máximo de intentos y no ha pasado el tiempo de bloqueo
        if count >= self.max_failed_attempts and (time.time() - timestamp) < self.lockout_duration:
            return True
        
        # Si ha pasado el tiempo de bloqueo, reiniciar contador
        if count >= self.max_failed_attempts and (time.time() - timestamp) >= self.lockout_duration:
            self.failed_attempts[username] = (0, 0)
            
        return False
    
    def _record_failed_attempt(self, username: str) -> None:
        """Registra un intento fallido de autenticación."""
        if username in self.failed_attempts:
            count, _ = self.failed_attempts[username]
            self.failed_attempts[username] = (count + 1, time.time())
        else:
            self.failed_attempts[username] = (1, time.time())
        
        count = self.failed_attempts[username][0]
        if count >= self.max_failed_attempts:
            logger.warning(f"Cuenta bloqueada por múltiples intentos fallidos: {username}")


class EncryptionManager:
    """Gestiona el cifrado y descifrado de datos sensibles."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Generar o cargar clave maestra
        master_key_env = os.environ.get("VICKY_ENCRYPTION_MASTER_KEY")
        if master_key_env:
            self.master_key = master_key_env.encode()
        else:
            # En producción, esta clave debería ser persistente y segura
            self.master_key = Fernet.generate_key()
        
        self.fernet = Fernet(self.master_key)
        
        # Configurar rotación de claves
        self.key_rotation_days = config.get("key_rotation_days", 30)
        self.last_rotation = config.get("last_rotation", time.time())
        
        # Inicializar backend de HSM si está configurado
        self.hsm_enabled = config.get("hsm_enabled", False)
        if self.hsm_enabled:
            try:
                from .hsm_integration import HSMManager
                self.hsm = HSMManager(config.get("hsm_config", {}))
            except ImportError:
                logger.warning("Módulo HSM no disponible")
                self.hsm_enabled = False
    
    def encrypt_data(self, data: Union[str, bytes], security_level: SecurityLevel = SecurityLevel.MEDIUM) -> bytes:
        """Cifra datos con el nivel de seguridad especificado."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if security_level == SecurityLevel.LOW:
            # Cifrado simple con Fernet
            return self.fernet.encrypt(data)
        
        elif security_level == SecurityLevel.MEDIUM:
            # Cifrado con sal única
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(self.master_key)
            f = Fernet(base64.urlsafe_b64encode(key))
            encrypted = f.encrypt(data)
            return salt + encrypted
        
        elif security_level in (SecurityLevel.HIGH, SecurityLevel.CRITICAL):
            if self.hsm_enabled:
                # Usar HSM para datos de alta seguridad
                return self.hsm.encrypt(data)
            else:
                # Cifrado avanzado con AES-256-GCM
                key = os.urandom(32)  # AES-256
                iv = os.urandom(12)   # Nonce para GCM
                
                # Cifrar la clave con la clave maestra
                encrypted_key = self.fernet.encrypt(key)
                
                # Cifrar los datos con AES-GCM
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(iv),
                    backend=default_backend()
                )
                encryptor = cipher.encryptor()
                ciphertext = encryptor.update(data) + encryptor.finalize()
                
                # Combinar todo
                result = {
                    "encrypted_key": encrypted_key.decode('utf-8'),
                    "iv": iv.hex(),
                    "ciphertext": ciphertext.hex(),
                    "tag": encryptor.tag.hex()
                }
                return json.dumps(result).encode('utf-8')
    
    def decrypt_data(self, encrypted_data: bytes, security_level: SecurityLevel = SecurityLevel.MEDIUM) -> bytes:
        """Descifra datos según el nivel de seguridad utilizado."""
        if security_level == SecurityLevel.LOW:
            # Descifrado simple con Fernet
            return self.fernet.decrypt(encrypted_data)
        
        elif security_level == SecurityLevel.MEDIUM:
            # Descifrado con sal
            salt, encrypted = encrypted_data[:16], encrypted_data[16:]
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(self.master_key)
            f = Fernet(base64.urlsafe_b64encode(key))
            return f.decrypt(encrypted)
        
        elif security_level in (SecurityLevel.HIGH, SecurityLevel.CRITICAL):
            if self.hsm_enabled:
                # Usar HSM para datos de alta seguridad
                return self.hsm.decrypt(encrypted_data)
            else:
                # Descifrado avanzado con AES-256-GCM
                data = json.loads(encrypted_data.decode('utf-8'))
                
                # Descifrar la clave
                key = self.fernet.decrypt(data["encrypted_key"].encode('utf-8'))
                
                # Descifrar los datos
                iv = bytes.fromhex(data["iv"])
                ciphertext = bytes.fromhex(data["ciphertext"])
                tag = bytes.fromhex(data["tag"])
                
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(iv, tag),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                return decryptor.update(ciphertext) + decryptor.finalize()
    
    def rotate_keys(self) -> bool:
        """Rota las claves de cifrado si es necesario."""
        current_time = time.time()
        days_since_rotation = (current_time - self.last_rotation) / (24 * 3600)
        
        if days_since_rotation < self.key_rotation_days:
            return False
        
        try:
            # Generar nueva clave maestra
            new_master_key = Fernet.generate_key()
            new_fernet = Fernet(new_master_key)
            
            # Aquí iría la lógica para re-cifrar datos existentes
            # ...
            
            # Actualizar claves
            self.master_key = new_master_key
            self.fernet = new_fernet
            self.last_rotation = current_time
            
            logger.info("Rotación de claves de cifrado completada")
            return True
            
        except Exception as e:
            logger.error(f"Error durante la rotación de claves: {str(e)}")
            return False


class ThreatDetectionEngine:
    """Motor de detección de amenazas y anomalías."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.anomaly_threshold = config.get("anomaly_threshold", 0.75)
        self.rate_limit_thresholds = config.get("rate_limit_thresholds", {
            "login": 10,  # intentos por minuto
            "api": 100,   # solicitudes por minuto
            "query": 50   # consultas por minuto
        })
        
        # Contadores para limitación de tasa
        self.rate_counters = {}  # {ip_address: {action: [(timestamp, count)]}}
        
        # Cargar reglas de detección
        self.rules = config.get("detection_rules", [])
        
        # Inicializar modelo de ML para detección de anomalías si está configurado
        self.ml_detection_enabled = config.get("ml_detection_enabled", False)
        if self.ml_detection_enabled:
            try:
                from .anomaly_detection import AnomalyDetector
                self.anomaly_detector = AnomalyDetector(config.get("anomaly_detector_config", {}))
            except ImportError:
                logger.warning("Módulo de detección de anomalías no disponible")
                self.ml_detection_enabled = False
    
    def check_request(self, context: SecurityContext, request_data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """
        Analiza una solicitud para detectar posibles amenazas.
        
        Returns:
            Tuple[bool, float, str]: (es_seguro, puntuación_riesgo, razón)
        """
        # Verificar limitación de tasa
        if not self._check_rate_limit(context.ip_address, request_data.get("action", "api")):
            return False, 1.0, "Excedido límite de tasa"
        
        # Verificar reglas estáticas
        for rule in self.rules:
            if self._check_rule(rule, context, request_data):
                return False, 0.9, f"Violación de regla: {rule.get('name', 'desconocida')}"
        
        # Detección de anomalías basada en ML
        risk_score = 0.0
        if self.ml_detection_enabled:
            features = self._extract_features(context, request_data)
            risk_score = self.anomaly_detector.predict(features)
            
            if risk_score > self.anomaly_threshold:
                return False, risk_score, "Comportamiento anómalo detectado"
        
        return True, risk_score, "OK"
    
    def _check_rate_limit(self, ip_address: str, action: str) -> bool:
        """Verifica si una IP ha excedido los límites de tasa para una acción."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Inicializar contadores si es necesario
        if ip_address not in self.rate_counters:
            self.rate_counters[ip_address] = {}
        if action not in self.rate_counters[ip_address]:
            self.rate_counters[ip_address][action] = []
        
        # Limpiar entradas antiguas
        self.rate_counters[ip_address][action] = [
            (ts, count) for ts, count in self.rate_counters[ip_address][action]
            if ts > minute_ago
        ]
        
        # Calcular total de acciones en el último minuto
        total = sum(count for _, count in self.rate_counters[ip_address][action])
        
        # Verificar límite
        threshold = self.rate_limit_thresholds.get(action, 100)
        if total >= threshold:
            logger.warning(f"Límite de tasa excedido para {ip_address} en acción {action}: {total}/{threshold}")
            return False
        
        # Actualizar contador
        self.rate_counters[ip_address][action].append((current_time, 1))
        return True
    
    def _check_rule(self, rule: Dict[str, Any], context: SecurityContext, request_data: Dict[str, Any]) -> bool:
        """Verifica si una solicitud viola una regla de seguridad."""
        rule_type = rule.get("type")
        
        if rule_type == "ip_blacklist" and context.ip_address in rule.get("values", []):
            return True
        
        elif rule_type == "user_agent_blacklist" and any(ua in context.user_agent for ua in rule.get("values", [])):
            return True
        
        elif rule_type == "path_blacklist" and request_data.get("path") in rule.get("values", []):
            return True
        
        elif rule_type == "pattern_match":
            field = rule.get("field", "")
            patterns = rule.get("patterns", [])
            value = self._get_nested_value(request_data, field)
            
            if value and any(pattern in str(value) for pattern in patterns):
                return True
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Obtiene un valor anidado de un diccionario usando una ruta con puntos."""
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _extract_features(self, context: SecurityContext, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae características para el modelo de detección de anomalías."""
        # Aquí iría la lógica para extraer características relevantes
        # Este es un ejemplo simplificado
        return {
            "user_id": context.user_id,
            "ip_address": context.ip_address,
            "auth_level": context.auth_level.value,
            "timestamp": context.timestamp,
            "action": request_data.get("action", ""),
            "path": request_data.get("path", ""),
            "method": request_data.get("method", ""),
            "payload_size": len(str(request_data.get("payload", ""))),
            "has_attachments": "attachments" in request_data,
            "num_parameters": len(request_data.get("params", {}))
        }


class AccessControlManager:
    """Gestiona permisos y control de acceso basado en roles y atributos."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Cargar roles y permisos
        self.roles = config.get("roles", {})
        self.permissions = config.get("permissions", {})
        
        # Mapeo de usuarios a roles
        self.user_roles = config.get("user_roles", {})
        
        # Caché de decisiones de acceso para optimizar rendimiento
        self.access_cache = {}
        self.cache_ttl = config.get("access_cache_ttl", 300)  # 5 minutos
    
    def check_permission(self, context: SecurityContext, resource: str, action: str) -> bool:
        """
        Verifica si un usuario tiene permiso para realizar una acción sobre un recurso.
        
        Args:
            context: Contexto de seguridad del usuario
            resource: Recurso al que se intenta acceder
            action: Acción que se intenta realizar (read, write, delete, etc.)
            
        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        # Verificar caché
        cache_key = f"{context.user_id}:{resource}:{action}"
        cached_result = self._get_cached_decision(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Obtener roles del usuario
        user_roles = self.user_roles.get(context.user_id, [])
        
        # Verificar permisos explícitos del usuario
        if self._has_explicit_permission(context.permissions, resource, action):
            self._cache_decision(cache_key, True)
            return True
        
        # Verificar permisos basados en roles
        for role in user_roles:
            if role in self.roles:
                role_permissions = self.roles[role]
                if self._has_explicit_permission(role_permissions, resource, action):
                    self._cache_decision(cache_key, True)
                    return True
        
        # Verificar reglas de acceso basadas en atributos (ABAC)
        if self._check_attribute_rules(context, resource, action):
            self._cache_decision(cache_key, True)
            return True
        
        # Por defecto, denegar acceso
        self._cache_decision(cache_key, False)
        return False
    
    def _has_explicit_permission(self, permissions: List[str], resource: str, action: str) -> bool:
        """Verifica si una lista de permisos incluye explícitamente un recurso y acción."""
        # Verificar permiso específico
        if f"{resource}:{action}" in permissions:
            return True
        
        # Verificar permiso wildcard para el recurso
        if f"{resource}:*" in permissions:
            return True
        
        # Verificar permiso global
        if "*:*" in permissions:
            return True
        
        return False
    
    def _check_attribute_rules(self, context: SecurityContext, resource: str, action: str) -> bool:
        """Verifica reglas de acceso basadas en atributos del contexto."""
        # Aquí iría la lógica para reglas ABAC más complejas
        # Por ejemplo, restricciones basadas en tiempo, ubicación, nivel de autenticación, etc.
        
        # Ejemplo: requerir MFA para acciones críticas
        if action in ["delete", "admin", "configure"] and not context.mfa_verified:
            return False
        
        # Ejemplo: requerir nivel de autenticación alto para recursos sensibles
        if resource.startswith("sensitive_") and context.auth_level.value < SecurityLevel.HIGH.value:
            return False
        
        return False  # Por defecto, las reglas ABAC no otorgan acceso
    
    def _get_cached_decision(self, key: str) -> Optional[bool]:
        """Obtiene una decisión de acceso de la caché si es válida."""
        if key in self.access_cache:
            decision, timestamp = self.access_cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return decision
        return None
    
    def _cache_decision(self, key: str, decision: bool) -> None:
        """Almacena una decisión de acceso en la caché."""
        self.access_cache[key] = (decision, time.time())
    
    def grant_permission(self, user_id: str, permission: str) -> None:
        """Otorga un permiso específico a un usuario."""
        # Implementación simplificada - en producción, esto actualizaría la base de datos
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        # Añadir el permiso a la lista de permisos del usuario
        user_permissions = self.permissions.get(user_id, [])
        if permission not in user_permissions:
            user_permissions.append(permission)
        self.permissions[user_id] = user_permissions
    
    def revoke_permission(self, user_id: str, permission: str) -> None:
        """Revoca un permiso específico de un usuario."""
        # Implementación simplificada
        user_permissions = self.permissions.get(user_id, [])
        if permission in user_permissions:
            user_permissions.remove(permission)
            self.permissions[user_id] = user_permissions


class AuditLogger:
    """Registra eventos de seguridad para auditoría y análisis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_level = config.get("log_level", logging.INFO)
        self.log_format = config.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Configurar logger
        self.logger = logging.getLogger("vicky.security.audit")
        self.logger.setLevel(self.log_level)
        
        # Configurar handler para archivos
        log_file = config.get("log_file", "security_audit.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(self.log_format))
        self.logger.addHandler(file_handler)
        
        # Configurar handler para stdout si está habilitado
        if config.get("log_to_stdout", True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(self.log_format))
            self.logger.addHandler(console_handler)
        
        # Configurar integración con SIEM si está habilitada
        self.siem_enabled = config.get("siem_enabled", False)
        if self.siem_enabled:
            try:
                from .siem_integration import SIEMConnector
                self.siem = SIEMConnector(config.get("siem_config", {}))
            except ImportError:
                logger.warning("Módulo de integración SIEM no disponible")
                self.siem_enabled = False
    
    def log_security_event(self, event_type: str, context: SecurityContext, details: Dict[str, Any], severity: str = "INFO") -> None:
        """Registra un evento de seguridad."""
        log_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "ip_address": context.ip_address,
            "user_agent": context.user_agent,
            "auth_level": context.auth_level.name,
            "details": details
        }
        
        # Determinar nivel de log
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        
        # Registrar evento
        log_method(f"{event_type}: {json.dumps(log_data)}")
        
        # Enviar a SIEM si está habilitado
        if self.siem_enabled and severity in ["WARNING", "ERROR", "CRITICAL"]:
            try:
                self.siem.send_event(log_data)
            except Exception as e:
                self.logger.error(f"Error al enviar evento a SIEM: {str(e)}")
    
    def log_auth_success(self, context: SecurityContext, method: str) -> None:
        """Registra un evento de autenticación exitosa."""
        self.log_security_event(
            "AUTHENTICATION_SUCCESS",
            context,
            {"method": method},
            "INFO"
        )
    
    def log_auth_failure(self, context: SecurityContext, method: str, reason: str) -> None:
        """Registra un evento de autenticación fallida."""
        self.log_security_event(
            "AUTHENTICATION_FAILURE",
            context,
            {"method": method, "reason": reason},
            "WARNING"
        )
    
    def log_access_denied(self, context: SecurityContext, resource: str, action: str) -> None:
        """Registra un evento de acceso denegado."""
        self.log_security_event(
            "ACCESS_DENIED",
            context,
            {"resource": resource, "action": action},
            "WARNING"
        )
    
    def log_security_violation(self, context: SecurityContext, violation_type: str, details: Dict[str, Any]) -> None:
        """Registra una violación de seguridad."""
        self.log_security_event(
            "SECURITY_VIOLATION",
            context,
            {"violation_type": violation_type, **details},
            "ERROR"
        )


class SecurityManager:
    """Clase principal que coordina todos los componentes de seguridad."""
    
    def __init__(self, config_path: str = None):
        # Cargar configuración
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Configuración por defecto
            self.config = {
                "authentication": {
                    "token_expiry": 3600,
                    "max_failed_attempts": 5,
                    "lockout_duration": 1800,
                    "mfa_required_level": "HIGH",
                    "biometric_enabled": False
                },
                "encryption": {
                    "key_rotation_days": 30,
                    "hsm_enabled": False
                },
                "threat_detection": {
                    "anomaly_threshold": 0.75,
                    "rate_limit_thresholds": {
                        "login": 10,
                        "api": 100,
                        "query": 50
                    },
                    "ml_detection_enabled": False,
                    "detection_rules": []
                },
                "access_control": {
                    "roles": {},
                    "permissions": {},
                    "user_roles": {},
                    "access_cache_ttl": 300
                },
                "audit": {
                    "log_level": "INFO",
                    "log_file": "security_audit.log",
                    "log_to_stdout": True,
                    "siem_enabled": False
                }
            }
        
        # Inicializar componentes
        self.auth_manager = AuthenticationManager(self.config.get("authentication", {}))
        self.encryption_manager = EncryptionManager(self.config.get("encryption", {}))
        self.threat_detection = ThreatDetectionEngine(self.config.get("threat_detection", {}))
        self.access_control = AccessControlManager(self.config.get("access_control", {}))
        self.audit_logger = AuditLogger(self.config.get("audit", {}))
        
        logger.info("Sistema de seguridad avanzada inicializado")
    
    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[str]:
        """Autentica a un usuario y devuelve un token JWT si es exitoso."""
        return self.auth_manager.authenticate(username, password, ip_address, user_agent)
    
    def verify_mfa(self, user_id: str, token: str, mfa_code: str) -> Optional[str]:
        """Verifica el segundo factor de autenticación."""
        return self.auth_manager.verify_mfa(user_id, token, mfa_code)
    
    def verify_token(self, token: str, ip_address: str) -> Optional[SecurityContext]:
        """Verifica un token JWT y devuelve el contexto de seguridad."""
        return self.auth_manager.verify_token(token, ip_address)
    
    def check_access(self, context: SecurityContext, resource: str, action: str) -> bool:
        """Verifica si un usuario tiene permiso para realizar una acción sobre un recurso."""
        has_permission = self.access_control.check_permission(context, resource, action)
        
        if not has_permission:
            self.audit_logger.log_access_denied(context, resource, action)
        
        return has_permission
    
    def encrypt(self, data: Union[str, bytes], security_level: SecurityLevel = SecurityLevel.MEDIUM) -> bytes:
        """Cifra datos con el nivel de seguridad especificado."""
        return self.encryption_manager.encrypt_data(data, security_level)
    
    def decrypt(self, encrypted_data: bytes, security_level: SecurityLevel = SecurityLevel.MEDIUM) -> bytes:
        """Descifra datos según el nivel de seguridad utilizado."""
        return self.encryption_manager.decrypt_data(encrypted_data, security_level)
    
    def analyze_request(self, context: SecurityContext, request_data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Analiza una solicitud para detectar posibles amenazas."""
        is_safe, risk_score, reason = self.threat_detection.check_request(context, request_data)
        
        if not is_safe:
            self.audit_logger.log_security_violation(
                context,
                "THREAT_DETECTED",
                {"risk_score": risk_score, "reason": reason, "request": request_data}
            )
        
        return is_safe, risk_score, reason
    
    def log_event(self, event_type: str, context: SecurityContext, details: Dict[str, Any], severity: str = "INFO") -> None:
        """Registra un evento de seguridad."""
        self.audit_logger.log_security_event(event_type, context, details, severity)
    
    def create_security_context(self, user_id: str, ip_address: str, user_agent: str) -> SecurityContext:
        """Crea un contexto de seguridad básico para un usuario."""
        return SecurityContext(
            user_id=user_id,
            session_id=secrets.token_hex(16),
            auth_level=SecurityLevel.LOW,
            permissions=[],
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=time.time()
        )


# Inicialización del sistema de seguridad
def initialize_security(config_path: str = None) -> SecurityManager:
    """Inicializa y devuelve una instancia del gestor de seguridad."""
    return SecurityManager(config_path)
