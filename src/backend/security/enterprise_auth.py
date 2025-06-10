"""
VokaFlow Enterprise Authentication Manager
=========================================

Sistema de autenticación empresarial para Fortune 500.
Maneja autenticación multifactor, gestión de sesiones,
control de acceso y políticas de seguridad.
"""

import os
import jwt
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("vokaflow.security.auth")

class AuthLevel(Enum):
    """Niveles de autenticación empresarial"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    EXECUTIVE = "executive"
    ADMIN = "admin"
    SYSTEM = "system"

@dataclass
class UserSession:
    """Sesión de usuario empresarial"""
    user_id: str
    session_id: str
    auth_level: AuthLevel
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    mfa_verified: bool = False
    permissions: List[str] = None

class EnterpriseAuthManager:
    """Gestor de autenticación empresarial Fortune 500"""
    
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}
        self.failed_attempts: Dict[str, int] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.secret_key = os.getenv('ENTERPRISE_SECRET_KEY', 
                                  'vokaflow_enterprise_2024_secure_key_' + secrets.token_hex(32))
        self.session_timeout = timedelta(minutes=30)
        
        logger.info("🔐 Enterprise Authentication Manager initialized")
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str, user_agent: str) -> Optional[UserSession]:
        """Autentica un usuario con validación empresarial"""
        try:
            # Verificar IP bloqueada
            if self._is_ip_blocked(ip_address):
                logger.warning(f"🚫 Authentication blocked for IP: {ip_address}")
                return None
            
            # Verificar intentos fallidos
            if self._check_failed_attempts(username):
                logger.warning(f"🚫 User {username} exceeded failed attempts")
                return None
            
            # Validar credenciales (simulado para demo)
            if self._validate_credentials(username, password):
                session = self._create_session(username, ip_address, user_agent)
                logger.info(f"✅ User {username} authenticated successfully")
                return session
            else:
                self._record_failed_attempt(username, ip_address)
                logger.warning(f"❌ Failed authentication for user: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return None
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """Valida una sesión existente"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            # Verificar timeout
            if datetime.now() - session.last_activity > self.session_timeout:
                self._expire_session(session_id)
                return None
            
            # Actualizar última actividad
            session.last_activity = datetime.now()
            return session
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    def require_mfa(self, session_id: str, mfa_code: str) -> bool:
        """Requiere autenticación multifactor"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Validar código MFA (simulado)
            if self._validate_mfa_code(session.user_id, mfa_code):
                session.mfa_verified = True
                session.auth_level = AuthLevel.ENHANCED
                logger.info(f"✅ MFA verified for user: {session.user_id}")
                return True
            else:
                logger.warning(f"❌ Invalid MFA code for user: {session.user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error during MFA validation: {e}")
            return False
    
    def get_user_permissions(self, session_id: str) -> List[str]:
        """Obtiene permisos del usuario"""
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        # Permisos basados en nivel de autenticación
        base_permissions = ["read", "basic_access"]
        
        if session.auth_level == AuthLevel.ENHANCED:
            base_permissions.extend(["write", "translate", "vicky_access"])
        elif session.auth_level == AuthLevel.EXECUTIVE:
            base_permissions.extend(["write", "translate", "vicky_access", "analytics", "reports"])
        elif session.auth_level == AuthLevel.ADMIN:
            base_permissions.extend(["write", "translate", "vicky_access", "analytics", 
                                   "reports", "user_management", "system_config"])
        elif session.auth_level == AuthLevel.SYSTEM:
            base_permissions.append("*")  # Todos los permisos
        
        return base_permissions
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Valida credenciales de usuario (simulado)"""
        # En producción, esto consultaría la base de datos con hash seguro
        valid_users = {
            "admin": "enterprise_admin_2024",
            "demo": "demo123",
            "vokaflow": "vokaflow_enterprise",
            "executive": "exec_secure_2024"
        }
        return valid_users.get(username) == password
    
    def _validate_mfa_code(self, user_id: str, mfa_code: str) -> bool:
        """Valida código MFA (simulado)"""
        # En producción, esto validaría TOTP o SMS
        return mfa_code in ["123456", "000000", "111111"]  # Códigos demo
    
    def _create_session(self, username: str, ip_address: str, user_agent: str) -> UserSession:
        """Crea una nueva sesión de usuario"""
        session_id = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=username,
            session_id=session_id,
            auth_level=AuthLevel.BASIC,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Verifica si una IP está bloqueada"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.now() - block_time < timedelta(minutes=15):
                return True
            else:
                del self.blocked_ips[ip_address]
        return False
    
    def _check_failed_attempts(self, username: str) -> bool:
        """Verifica intentos fallidos"""
        return self.failed_attempts.get(username, 0) >= 3
    
    def _record_failed_attempt(self, username: str, ip_address: str):
        """Registra intento fallido"""
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
        
        # Bloquear IP después de 5 intentos fallidos
        if self.failed_attempts[username] >= 5:
            self.blocked_ips[ip_address] = datetime.now()
    
    def _expire_session(self, session_id: str):
        """Expira una sesión"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

# Instancia global del gestor de autenticación
_enterprise_auth_manager = None

def get_enterprise_auth_manager() -> EnterpriseAuthManager:
    """Obtiene la instancia global del gestor de autenticación empresarial"""
    global _enterprise_auth_manager
    if _enterprise_auth_manager is None:
        _enterprise_auth_manager = EnterpriseAuthManager()
    return _enterprise_auth_manager

def reset_enterprise_auth_manager():
    """Reinicia el gestor de autenticación (para pruebas)"""
    global _enterprise_auth_manager
    _enterprise_auth_manager = None 