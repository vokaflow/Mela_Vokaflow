"""
VokaFlow - Vicky State Persistence Manager
Maneja la persistencia del estado de Vicky y configuraciones del sistema
"""

import os
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VickyStateManager:
    """Gestor de persistencia del estado de Vicky"""
    
    def __init__(self, data_dir: str = "./data/vicky"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos de estado
        self.state_file = self.data_dir / "vicky_state.json"
        self.config_file = self.data_dir / "vicky_config.json"
        self.memory_file = self.data_dir / "vicky_memory.pkl"
        self.conversations_db = self.data_dir / "conversations.db"
        self.metrics_file = self.data_dir / "metrics.json"
        
        # Inicializar base de datos de conversaciones
        self._init_conversations_db()
        
        # Estado por defecto
        self.default_state = {
            "current_personality": "balanced",
            "hemisphere_balance": {"technical": 0.6, "emotional": 0.4},
            "active_engines": [],
            "session_count": 0,
            "total_interactions": 0,
            "last_update": datetime.now().isoformat(),
            "uptime_start": datetime.now().isoformat(),
            "cognitive_load": 0.0,
            "memory_usage": {"short_term": 0.0, "long_term": 0.0},
            "learning_metrics": {
                "patterns_learned": 0,
                "adaptations_made": 0,
                "success_rate": 0.9
            }
        }
        
        # Configuración por defecto
        self.default_config = {
            "auto_save": True,
            "save_interval": 60,  # segundos
            "max_memory_items": 1000,
            "backup_enabled": True,
            "backup_interval": 3600,  # segundos
            "max_backups": 10,
            "personality_preferences": {},
            "hemisphere_presets": {
                "technical": {"technical": 0.8, "emotional": 0.2},
                "balanced": {"technical": 0.6, "emotional": 0.4},
                "creative": {"technical": 0.3, "emotional": 0.7},
                "analytical": {"technical": 0.85, "emotional": 0.15},
                "empathetic": {"technical": 0.25, "emotional": 0.75}
            }
        }
    
    def _init_conversations_db(self):
        """Inicializa la base de datos de conversaciones"""
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            # Tabla de conversaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_message TEXT,
                    vicky_response TEXT,
                    personality TEXT,
                    hemisphere_balance TEXT,
                    confidence REAL,
                    processing_time REAL,
                    timestamp TEXT,
                    metadata TEXT
                )
            ''')
            
            # Tabla de métricas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT,
                    metric_value REAL,
                    metadata TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Tabla de estados del sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state_data TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Base de datos de conversaciones inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Guarda el estado actual de Vicky"""
        try:
            # Actualizar timestamp
            state["last_update"] = datetime.now().isoformat()
            
            # Guardar en archivo JSON
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            # Guardar en base de datos para historial
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO system_states (state_data, timestamp) VALUES (?, ?)",
                (json.dumps(state), datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            
            logger.debug("Estado de Vicky guardado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando estado: {e}")
            return False
    
    def load_state(self) -> Dict[str, Any]:
        """Carga el estado de Vicky"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Validar y completar campos faltantes
                for key, value in self.default_state.items():
                    if key not in state:
                        state[key] = value
                
                logger.debug("Estado de Vicky cargado exitosamente")
                return state
            else:
                logger.info("No se encontró estado previo, usando estado por defecto")
                return self.default_state.copy()
                
        except Exception as e:
            logger.error(f"Error cargando estado: {e}")
            return self.default_state.copy()
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Guarda la configuración de Vicky"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.debug("Configuración de Vicky guardada")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Carga la configuración de Vicky"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Completar configuración con valores por defecto
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                
                return config
            else:
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self.default_config.copy()
    
    def save_conversation(self, user_message: str, vicky_response: str, 
                         personality: str, hemisphere_balance: Dict[str, float],
                         confidence: float = 0.9, processing_time: float = 0.0,
                         session_id: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Guarda una conversación en la base de datos"""
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, user_message, vicky_response, personality, 
                 hemisphere_balance, confidence, processing_time, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id or "default",
                user_message,
                vicky_response,
                personality,
                json.dumps(hemisphere_balance),
                confidence,
                processing_time,
                datetime.now().isoformat(),
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error guardando conversación: {e}")
            return False
    
    def get_conversation_history(self, session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene el historial de conversaciones"""
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT * FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (session_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM conversations 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            conversations = []
            
            for row in cursor.fetchall():
                conv = dict(zip(columns, row))
                conv['hemisphere_balance'] = json.loads(conv['hemisphere_balance'])
                conv['metadata'] = json.loads(conv['metadata'])
                conversations.append(conv)
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def save_metrics(self, metric_type: str, metric_value: float, metadata: Dict[str, Any] = None) -> bool:
        """Guarda métricas del sistema"""
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO metrics (metric_type, metric_value, metadata, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                metric_type,
                metric_value,
                json.dumps(metadata or {}),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error guardando métrica: {e}")
            return False
    
    def get_metrics(self, metric_type: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtiene métricas del sistema"""
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            since = datetime.now() - timedelta(hours=hours)
            
            if metric_type:
                cursor.execute('''
                    SELECT * FROM metrics 
                    WHERE metric_type = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                ''', (metric_type, since.isoformat()))
            else:
                cursor.execute('''
                    SELECT * FROM metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                ''', (since.isoformat(),))
            
            columns = [desc[0] for desc in cursor.description]
            metrics = []
            
            for row in cursor.fetchall():
                metric = dict(zip(columns, row))
                metric['metadata'] = json.loads(metric['metadata'])
                metrics.append(metric)
            
            conn.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return []
    
    def backup_data(self) -> bool:
        """Crea un backup de todos los datos"""
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"vicky_backup_{timestamp}.json"
            
            # Recopilar todos los datos
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "state": self.load_state(),
                "config": self.load_config(),
                "conversations": self.get_conversation_history(limit=1000),
                "metrics": self.get_metrics(hours=24*7),  # Una semana
                "version": "1.0.0"
            }
            
            # Guardar backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Limpiar backups antiguos
            self._cleanup_old_backups(backup_dir)
            
            logger.info(f"Backup creado: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def _cleanup_old_backups(self, backup_dir: Path, max_backups: int = 10):
        """Limpia backups antiguos"""
        try:
            backup_files = list(backup_dir.glob("vicky_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Eliminar backups excedentes
            for old_backup in backup_files[max_backups:]:
                old_backup.unlink()
                logger.debug(f"Backup antiguo eliminado: {old_backup}")
                
        except Exception as e:
            logger.error(f"Error limpiando backups: {e}")
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """Restaura datos desde un backup"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                backup_path = self.data_dir / "backups" / backup_file
            
            if not backup_path.exists():
                logger.error(f"Archivo de backup no encontrado: {backup_file}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restaurar estado y configuración
            if 'state' in backup_data:
                self.save_state(backup_data['state'])
            
            if 'config' in backup_data:
                self.save_config(backup_data['config'])
            
            logger.info(f"Datos restaurados desde: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        try:
            conn = sqlite3.connect(self.conversations_db)
            cursor = conn.cursor()
            
            # Estadísticas de conversaciones
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            conversations_24h = cursor.fetchone()[0]
            
            # Estadísticas de métricas
            cursor.execute("SELECT COUNT(*) FROM metrics")
            total_metrics = cursor.fetchone()[0]
            
            # Promedio de confianza
            cursor.execute("SELECT AVG(confidence) FROM conversations")
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            # Tiempo de procesamiento promedio
            cursor.execute("SELECT AVG(processing_time) FROM conversations")
            avg_processing_time = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                "total_conversations": total_conversations,
                "conversations_24h": conversations_24h,
                "total_metrics": total_metrics,
                "avg_confidence": round(avg_confidence, 3),
                "avg_processing_time": round(avg_processing_time, 3),
                "data_dir_size": self._get_directory_size(self.data_dir),
                "last_backup": self._get_last_backup_time(),
                "uptime": self._calculate_uptime()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _get_directory_size(self, directory: Path) -> int:
        """Obtiene el tamaño de un directorio en bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            return total_size
        except Exception:
            return 0
    
    def _get_last_backup_time(self) -> Optional[str]:
        """Obtiene la fecha del último backup"""
        try:
            backup_dir = self.data_dir / "backups"
            if not backup_dir.exists():
                return None
            
            backup_files = list(backup_dir.glob("vicky_backup_*.json"))
            if not backup_files:
                return None
            
            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            return datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat()
            
        except Exception:
            return None
    
    def _calculate_uptime(self) -> str:
        """Calcula el tiempo de actividad del sistema"""
        try:
            state = self.load_state()
            if "uptime_start" in state:
                start_time = datetime.fromisoformat(state["uptime_start"])
                uptime_delta = datetime.now() - start_time
                
                days = uptime_delta.days
                hours, remainder = divmod(uptime_delta.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                return f"{days}d {hours}h {minutes}m {seconds}s"
            else:
                return "Unknown"
                
        except Exception:
            return "Error"

# Instancia global del gestor de estado
state_manager = VickyStateManager()
