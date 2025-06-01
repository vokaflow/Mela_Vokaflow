#!/usr/bin/env python3
"""
🚀 VokaFlow Enterprise Launcher - Lanzamiento Galáctico Completo
Lanza toda la plataforma: Backend + Vicky + Dashboard
Configuración persistente para sobrevivir reinicos del sistema
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vokaflow_enterprise.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vokaflow-enterprise")

class VokaFlowEnterpriseLauncher:
    """Lanzador principal de la Enterprise VokaFlow"""
    
    def __init__(self):
        self.base_path = Path("/opt/vokaflow")
        self.frontend_path = self.base_path / "Frontend_Vokaflow"
        self.venv_path = self.base_path / "venv"
        self.processes = {}
        self.running = True
        
        # Verificar rutas
        self._verify_paths()
        
    def _verify_paths(self):
        """Verificar que todos los paths existen"""
        paths = [self.base_path, self.frontend_path, self.venv_path]
        for path in paths:
            if not path.exists():
                logger.error(f"❌ Path no encontrado: {path}")
                sys.exit(1)
        logger.info("✅ Todas las rutas verificadas")
    
    def setup_environment(self):
        """Configurar variables de entorno"""
        env = os.environ.copy()
        env.update({
            'PYTHONPATH': f"{self.base_path}/src:{env.get('PYTHONPATH', '')}",
            'NODE_ENV': 'production',
            'VOKAFLOW_ENV': 'enterprise',
            'VOKAFLOW_BASE_PATH': str(self.base_path)
        })
        return env
    
    def launch_backend(self):
        """🚀 Lanzar Backend VokaFlow"""
        logger.info("🚀 Iniciando Backend VokaFlow...")
        
        env = self.setup_environment()
        cmd = [
            str(self.venv_path / "bin" / "python"),
            "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--workers", "4"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path / "src"),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            self.processes['backend'] = process
            logger.info("✅ Backend VokaFlow iniciado en puerto 8000")
            return process
        except Exception as e:
            logger.error(f"❌ Error iniciando backend: {e}")
            return None
    
    def launch_frontend(self):
        """🖥️ Lanzar Frontend Dashboard"""
        logger.info("🖥️ Iniciando Frontend Dashboard...")
        
        env = self.setup_environment()
        cmd = ["npm", "run", "dev", "--", "--port", "3000"]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.frontend_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            self.processes['frontend'] = process
            logger.info("✅ Frontend Dashboard iniciado en puerto 3000")
            return process
        except Exception as e:
            logger.error(f"❌ Error iniciando frontend: {e}")
            return None
    
    def launch_vicky_service(self):
        """🧠 Lanzar Servicio Vicky AI"""
        logger.info("🧠 Iniciando Vicky AI Service...")
        
        env = self.setup_environment()
        cmd = [
            str(self.venv_path / "bin" / "python"),
            "-c",
            """
import sys
sys.path.append('/opt/vokaflow/src')
from vicky.core.personality_loader import VickyPersonalityLoader
from backend.routers.vicky import router
import asyncio
import uvicorn

# Inicializar Vicky
loader = VickyPersonalityLoader()
print(f'🧠 Vicky cargada con {len(loader.get_all_personalities())} personalidades')

# Ejecutar en puerto separado para Vicky
if __name__ == '__main__':
    print('🧠✨ Vicky AI Service iniciado en puerto 8001')
    uvicorn.run('backend.routers.vicky:router', host='0.0.0.0', port=8001, reload=False)
"""
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            self.processes['vicky'] = process
            logger.info("✅ Vicky AI Service iniciado en puerto 8001")
            return process
        except Exception as e:
            logger.error(f"❌ Error iniciando Vicky: {e}")
            return None
    
    def monitor_processes(self):
        """📊 Monitorear procesos en tiempo real"""
        def monitor():
            while self.running:
                for name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️ Proceso {name} terminado. Reiniciando...")
                        self.restart_process(name)
                time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def restart_process(self, name):
        """🔄 Reiniciar proceso específico"""
        logger.info(f"🔄 Reiniciando {name}...")
        
        if name == 'backend':
            self.launch_backend()
        elif name == 'frontend':
            self.launch_frontend()
        elif name == 'vicky':
            self.launch_vicky_service()
    
    def setup_systemd_services(self):
        """⚙️ Configurar servicios systemd para persistencia"""
        service_content = f"""[Unit]
Description=VokaFlow Enterprise Platform
After=network.target

[Service]
Type=simple
User=dw7
Group=dw7
WorkingDirectory={self.base_path}
Environment=PYTHONPATH={self.base_path}/src
ExecStart={sys.executable} {self.base_path}/launch_enterprise_vokaflow.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/tmp/vokaflow-enterprise.service")
        service_path.write_text(service_content)
        
        logger.info("⚙️ Archivo de servicio systemd creado en /tmp/vokaflow-enterprise.service")
        logger.info("📋 Para instalar ejecuta:")
        logger.info("   sudo cp /tmp/vokaflow-enterprise.service /etc/systemd/system/")
        logger.info("   sudo systemctl daemon-reload")
        logger.info("   sudo systemctl enable vokaflow-enterprise")
        logger.info("   sudo systemctl start vokaflow-enterprise")
    
    def check_ports(self):
        """🔍 Verificar puertos disponibles"""
        import socket
        ports = [8000, 8001, 3000]
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                logger.warning(f"⚠️ Puerto {port} ya está en uso")
            else:
                logger.info(f"✅ Puerto {port} disponible")
            sock.close()
    
    def launch_enterprise(self):
        """🚀 LANZAMIENTO PRINCIPAL DE LA ENTERPRISE"""
        logger.info("=" * 60)
        logger.info("🚀✨ INICIANDO VOKAFLOW ENTERPRISE PLATFORM ✨🚀")
        logger.info("=" * 60)
        
        # Verificar puertos
        self.check_ports()
        
        # Configurar servicios systemd
        self.setup_systemd_services()
        
        # Lanzar componentes
        backend = self.launch_backend()
        time.sleep(5)  # Esperar que el backend se estabilice
        
        vicky = self.launch_vicky_service() 
        time.sleep(3)  # Esperar que Vicky se inicialice
        
        frontend = self.launch_frontend()
        time.sleep(3)  # Esperar que el frontend se inicialice
        
        # Iniciar monitoreo
        monitor_thread = self.monitor_processes()
        
        # Mostrar estado
        self.show_status()
        
        # Configurar señales para cierre limpio
        def signal_handler(signum, frame):
            logger.info("🛑 Cerrando VokaFlow Enterprise...")
            self.running = False
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Mantener activo
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(None, None)
    
    def show_status(self):
        """📊 Mostrar estado de la plataforma"""
        logger.info("=" * 60)
        logger.info("🌟 VOKAFLOW ENTERPRISE STATUS 🌟")
        logger.info("=" * 60)
        
        services = {
            'Backend API': 'http://localhost:8000',
            'Vicky AI': 'http://localhost:8001', 
            'Dashboard': 'http://localhost:3000'
        }
        
        for service, url in services.items():
            status = "🟢 ACTIVO" if service.lower().replace(' ', '_') in self.processes else "🔴 INACTIVO"
            logger.info(f"{service:15} {status:10} → {url}")
        
        logger.info("=" * 60)
        logger.info("🚀 Enterprise VokaFlow conquistando la galaxia...")
        logger.info("💫 Presiona Ctrl+C para detener")
        logger.info("=" * 60)
    
    def shutdown(self):
        """🛑 Cierre limpio de todos los procesos"""
        logger.info("🛑 Iniciando cierre limpio...")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"🛑 Cerrando {name}...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Forzando cierre de {name}")
                    process.kill()
        
        logger.info("✅ VokaFlow Enterprise cerrado correctamente")

def main():
    """🚀 Función principal"""
    try:
        launcher = VokaFlowEnterpriseLauncher()
        launcher.launch_enterprise()
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 