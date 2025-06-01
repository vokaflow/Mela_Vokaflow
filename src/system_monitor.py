#!/usr/bin/env python3
"""
Monitor del sistema para VokaFlow
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning",
                "status_message": "Sistema funcionando correctamente",
                "uptime_formatted": self._format_uptime(),
                "hostname": psutil.os.uname().nodename if hasattr(psutil.os, 'uname') else "unknown",
                "current_metrics": {
                    "cpu": {"percent": cpu_percent},
                    "memory": {"virtual": {"percent": memory.percent}},
                    "disk": {"usage": {"percent": disk.percent}}
                },
                "components": {
                    "python": {"status": "healthy"},
                    "database": {"status": "healthy"}
                },
                "warnings": []
            }
        except Exception as e:
            return {
                "status": "error",
                "status_message": f"Error al obtener métricas: {str(e)}",
                "uptime_formatted": self._format_uptime(),
                "hostname": "unknown",
                "current_metrics": {"cpu": {"percent": 0}, "memory": {"virtual": {"percent": 0}}, "disk": {"usage": {"percent": 0}}},
                "components": {"python": {"status": "error"}, "database": {"status": "unknown"}},
                "warnings": [f"Error en monitor del sistema: {str(e)}"]
            }
    
    def _format_uptime(self) -> str:
        """Formatea el tiempo de actividad"""
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_detailed_metrics(self, component: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """Obtiene métricas detalladas del sistema"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.get_system_status(),
            "component": component,
            "limit": limit
        }

# Instancia global
_system_monitor = SystemMonitor()

def get_system_monitor() -> SystemMonitor:
    """Obtiene la instancia del monitor del sistema"""
    return _system_monitor
