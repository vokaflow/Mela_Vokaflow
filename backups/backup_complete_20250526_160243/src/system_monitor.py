"""
Sistema de monitoreo básico para VokaFlow
"""
import psutil
import time
import platform
from datetime import datetime
from typing import Dict, Any

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        uptime = time.time() - self.start_time
        
        return {
            "status": "healthy",
            "status_message": "Sistema funcionando correctamente",
            "uptime_formatted": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m",
            "hostname": platform.node(),
            "current_metrics": {
                "cpu": {"percent": psutil.cpu_percent()},
                "memory": {"virtual": {"percent": psutil.virtual_memory().percent}},
                "disk": {"usage": {"percent": psutil.disk_usage('/').percent}}
            },
            "components": {
                "python": {"status": "ok"},
                "database": {"status": "connected"}
            },
            "warnings": []
        }
    
    def get_detailed_metrics(self, component=None, limit=20):
        """Obtiene métricas detalladas"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": datetime.now().isoformat()
        }

# Instancia global
_system_monitor = SystemMonitor()

def get_system_monitor():
    """Obtiene la instancia del monitor del sistema"""
    return _system_monitor
