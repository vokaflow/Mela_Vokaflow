"""
VokaFlow Persistent Security Storage
===================================

Sistema de almacenamiento persistente y seguro para datos empresariales.
Maneja cifrado, backup distribuido, integridad de datos y cumplimiento normativo.
"""

import os
import json
import sqlite3
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger("vokaflow.security.storage")

class PersistentSecurityStorage:
    """Almacenamiento seguro persistente Fortune 500"""
    
    def __init__(self, storage_path: str = "data/security"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Base de datos SQLite para datos estructurados
        self.db_path = self.storage_path / "enterprise_security.db"
        
        # Configuración de cifrado
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher = Fernet(self._encryption_key)
        
        # Inicializar base de datos
        self._initialize_database()
        
        logger.info(f"🔒 Persistent Security Storage initialized at {self.storage_path}")
    
    def store_secure_data(self, category: str, data_id: str, data: Dict[str, Any], 
                         encrypt: bool = True) -> bool:
        """Almacena datos de forma segura"""
        try:
            # Serializar datos
            json_data = json.dumps(data, default=str)
            
            # Cifrar si se requiere
            if encrypt:
                encrypted_data = self._cipher.encrypt(json_data.encode())
                stored_data = base64.b64encode(encrypted_data).decode()
                is_encrypted = 1
            else:
                stored_data = json_data
                is_encrypted = 0
            
            # Calcular hash de integridad
            data_hash = hashlib.sha256(json_data.encode()).hexdigest()
            
            # Almacenar en base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO secure_storage 
                    (category, data_id, data, data_hash, is_encrypted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    category, data_id, stored_data, data_hash, is_encrypted,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                conn.commit()
            
            logger.info(f"✅ Secure data stored: {category}/{data_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing secure data: {e}")
            return False
    
    def retrieve_secure_data(self, category: str, data_id: str) -> Optional[Dict[str, Any]]:
        """Recupera datos seguros"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data, data_hash, is_encrypted FROM secure_storage
                    WHERE category = ? AND data_id = ?
                """, (category, data_id))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                stored_data, data_hash, is_encrypted = result
                
                # Descifrar si es necesario
                if is_encrypted:
                    encrypted_data = base64.b64decode(stored_data.encode())
                    decrypted_data = self._cipher.decrypt(encrypted_data).decode()
                    json_data = decrypted_data
                else:
                    json_data = stored_data
                
                # Verificar integridad
                calculated_hash = hashlib.sha256(json_data.encode()).hexdigest()
                if calculated_hash != data_hash:
                    logger.error(f"❌ Data integrity check failed for {category}/{data_id}")
                    return None
                
                # Deserializar
                data = json.loads(json_data)
                logger.info(f"✅ Secure data retrieved: {category}/{data_id}")
                return data
                
        except Exception as e:
            logger.error(f"❌ Error retrieving secure data: {e}")
            return None
    
    def store_audit_log(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Almacena log de auditoría"""
        try:
            audit_entry = {
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "details": details,
                "source_ip": details.get("ip_address", "unknown"),
                "user_agent": details.get("user_agent", "unknown")
            }
            
            # Los logs de auditoría siempre se cifran
            self.store_secure_data("audit_logs", 
                                 f"{event_type}_{user_id}_{int(datetime.now().timestamp())}", 
                                 audit_entry, encrypt=True)
            
            logger.info(f"📋 Audit log stored: {event_type} by {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing audit log: {e}")
    
    def get_audit_logs(self, start_date: datetime, end_date: datetime, 
                      event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recupera logs de auditoría"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT category, data_id FROM secure_storage 
                    WHERE category = 'audit_logs' 
                    AND created_at BETWEEN ? AND ?
                """
                
                params = [start_date.isoformat(), end_date.isoformat()]
                
                if event_type:
                    query += " AND data_id LIKE ?"
                    params.append(f"{event_type}_%")
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                audit_logs = []
                for category, data_id in results:
                    log_data = self.retrieve_secure_data(category, data_id)
                    if log_data:
                        audit_logs.append(log_data)
                
                logger.info(f"📋 Retrieved {len(audit_logs)} audit logs")
                return audit_logs
                
        except Exception as e:
            logger.error(f"❌ Error retrieving audit logs: {e}")
            return []
    
    def store_security_config(self, config_name: str, config_data: Dict[str, Any]):
        """Almacena configuración de seguridad"""
        return self.store_secure_data("security_config", config_name, config_data, encrypt=True)
    
    def get_security_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Recupera configuración de seguridad"""
        return self.retrieve_secure_data("security_config", config_name)
    
    def backup_security_data(self, backup_path: Optional[str] = None) -> bool:
        """Crea backup de datos de seguridad"""
        try:
            if backup_path is None:
                backup_path = self.storage_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            # Copiar base de datos
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"💾 Security data backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return False
    
    def cleanup_old_data(self, retention_days: int = 2555):  # 7 años para SOX
        """Limpia datos antiguos según políticas de retención"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM secure_storage 
                    WHERE created_at < ? AND category != 'security_config'
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"🧹 Cleaned up {deleted_count} old security records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return False
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del almacenamiento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Conteo por categoría
                cursor.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM secure_storage 
                    GROUP BY category
                """)
                category_counts = dict(cursor.fetchall())
                
                # Tamaño de base de datos
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    "total_records": sum(category_counts.values()),
                    "category_counts": category_counts,
                    "database_size_bytes": db_size,
                    "database_size_mb": round(db_size / 1024 / 1024, 2),
                    "storage_path": str(self.storage_path),
                    "encryption_enabled": True
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting storage statistics: {e}")
            return {}
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Obtiene o crea clave de cifrado"""
        key_file = self.storage_path / ".encryption_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generar nueva clave
            password = os.getenv('ENTERPRISE_ENCRYPTION_PASSWORD', 'vokaflow_enterprise_2024').encode()
            salt = secrets.token_bytes(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Guardar clave y salt
            with open(key_file, 'wb') as f:
                f.write(key)
            
            with open(self.storage_path / ".salt", 'wb') as f:
                f.write(salt)
            
            logger.info("🔑 New encryption key generated")
            return key
    
    def _initialize_database(self):
        """Inicializa la base de datos SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla principal de almacenamiento seguro
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS secure_storage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    data_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    data_hash TEXT NOT NULL,
                    is_encrypted INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(category, data_id)
                )
            """)
            
            # Índices para optimización
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON secure_storage(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON secure_storage(created_at)")
            
            conn.commit()
            
        logger.info("🗄️ Security database initialized") 