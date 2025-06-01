#!/usr/bin/env python3
"""
🚀 VokaFlow Enterprise Launcher - ARQUITECTURA CORREGIDA
Backend (8000) + Frontend (3000) - Vicky integrada en backend
Configuración persistente y estable
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
    """Lanzador Enterprise con arquitectura correcta"""
    
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
    
    def kill_existing_processes(self):
        """🔫 Eliminar procesos existentes en puertos"""
        import socket
        ports_to_clear = [8000, 3000]
        
        for port in ports_to_clear:
            try:
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'], 
                    capture_output=True, 
                    text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], check=False)
                            logger.info(f"🔫 Proceso {pid} eliminado del puerto {port}")
                        except:
                            pass
            except:
                pass
        
        # Esperar un momento para que se liberen los puertos
        time.sleep(2)
    
    def launch_backend(self):
        """🚀 Lanzar Backend VokaFlow con Vicky integrada + High Scale System"""
        logger.info("🚀 Iniciando Backend VokaFlow (incluye Vicky AI + High Scale)")
        
        env = self.setup_environment()
        cmd = [
            str(self.venv_path / "bin" / "python"),
            "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1",  # Solo 1 worker de uvicorn, el paralelismo viene del High Scale System
            "--log-level", "info"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path / "src"),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes['backend'] = process
            logger.info("✅ Backend VokaFlow + Vicky + High Scale iniciado en puerto 8000")
            return process
        except Exception as e:
            logger.error(f"❌ Error iniciando backend: {e}")
            return None
    
    def launch_frontend(self):
        """🖥️ Lanzar Frontend Dashboard"""
        logger.info("🖥️ Iniciando Frontend Dashboard...")
        
        env = self.setup_environment()
        
        # Asegurar que npm install esté actualizado
        try:
            subprocess.run(
                ["npm", "install"], 
                cwd=str(self.frontend_path),
                env=env,
                check=False,
                capture_output=True
            )
        except:
            pass
        
        cmd = ["npm", "run", "dev", "--", "--port", "3000", "--hostname", "0.0.0.0"]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.frontend_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes['frontend'] = process
            logger.info("✅ Frontend Dashboard iniciado en puerto 3000")
            return process
        except Exception as e:
            logger.error(f"❌ Error iniciando frontend: {e}")
            return None
    
    def monitor_processes(self):
        """📊 Monitorear procesos sin reinicios excesivos"""
        def monitor():
            restart_count = {'backend': 0, 'frontend': 0}
            max_restarts = 3
            
            while self.running:
                for name, process in list(self.processes.items()):
                    if process and process.poll() is not None:
                        if restart_count[name] < max_restarts:
                            logger.warning(f"⚠️ Proceso {name} terminado. Reiniciando... ({restart_count[name] + 1}/{max_restarts})")
                            restart_count[name] += 1
                            self.restart_process(name)
                        else:
                            logger.error(f"❌ Proceso {name} falló {max_restarts} veces. Deteniendo reinicios.")
                            del self.processes[name]
                
                time.sleep(15)  # Intervalo más largo para evitar spam
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def restart_process(self, name):
        """🔄 Reiniciar proceso específico"""
        logger.info(f"🔄 Reiniciando {name}...")
        
        # Esperar antes de reiniciar
        time.sleep(5)
        
        if name == 'backend':
            self.launch_backend()
        elif name == 'frontend':
            self.launch_frontend()
    
    def check_ports_availability(self):
        """🔍 Verificar disponibilidad de puertos"""
        import socket
        ports = [8000, 3000]
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                logger.warning(f"⚠️ Puerto {port} ya está en uso - será liberado")
            else:
                logger.info(f"✅ Puerto {port} disponible")
            sock.close()
    
    def wait_for_backend_ready(self):
        """⏳ Esperar a que el backend esté listo"""
        import requests
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Backend está listo y respondiendo")
                    return True
            except:
                pass
            
            attempt += 1
            time.sleep(2)
            logger.info(f"⏳ Esperando backend... ({attempt}/{max_attempts})")
        
        logger.warning("⚠️ Backend tardó en responder, continuando...")
        return False
    
    def setup_systemd_services(self):
        """⚙️ Configurar servicios systemd"""
        service_content = f"""[Unit]
Description=VokaFlow Enterprise Platform
After=network.target

[Service]
Type=simple
User=dw7
Group=dw7
WorkingDirectory={self.base_path}
Environment=PYTHONPATH={self.base_path}/src
ExecStart={sys.executable} {self.base_path}/launch_enterprise_vokaflow_fixed.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/tmp/vokaflow-enterprise.service")
        service_path.write_text(service_content)
        
        logger.info("⚙️ Archivo de servicio systemd creado")
        logger.info("📋 Para configurar persistencia ejecuta:")
        logger.info("   sudo cp /tmp/vokaflow-enterprise.service /etc/systemd/system/")
        logger.info("   sudo systemctl daemon-reload")
        logger.info("   sudo systemctl enable vokaflow-enterprise")
    
    def launch_enterprise(self):
        """🚀 LANZAMIENTO PRINCIPAL CORREGIDO"""
        logger.info("=" * 60)
        logger.info("🚀✨ VOKAFLOW ENTERPRISE - ARQUITECTURA CORREGIDA ✨🚀")
        logger.info("=" * 60)
        logger.info("🏗️ Backend (8000): FastAPI + Vicky AI integrada")
        logger.info("🖥️ Frontend (3000): Next.js Dashboard")
        logger.info("=" * 60)
        
        # Verificar y limpiar puertos
        self.check_ports_availability()
        self.kill_existing_processes()
        
        # Configurar systemd
        self.setup_systemd_services()
        
        # Lanzar componentes EN ORDEN
        logger.info("🚀 Iniciando secuencia de lanzamiento...")
        
        # 1. Backend primero
        backend = self.launch_backend()
        if not backend:
            logger.error("❌ Falló el lanzamiento del backend. Abortando.")
            return
        
        # 2. Esperar que el backend esté listo
        self.wait_for_backend_ready()
        
        # 3. Frontend después
        frontend = self.launch_frontend()
        if not frontend:
            logger.error("❌ Falló el lanzamiento del frontend")
        
        # 4. Esperar estabilización
        time.sleep(10)
        
        # 5. Iniciar monitoreo
        monitor_thread = self.monitor_processes()
        
        # 6. Mostrar estado
        self.show_status()
        
        # Configurar cierre limpio
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
                time.sleep(2)
        except KeyboardInterrupt:
            signal_handler(None, None)
    
    def show_status(self):
        """📊 Mostrar estado actual + High Scale System"""
        logger.info("=" * 60)
        logger.info("🌟 VOKAFLOW ENTERPRISE STATUS 🌟")
        logger.info("=" * 60)
        
        services = {
            'Backend + Vicky + High Scale': ('http://localhost:8000', 'backend'),
            'Dashboard': ('http://localhost:3000', 'frontend')
        }
        
        for service, (url, key) in services.items():
            status = "🟢 ACTIVO" if key in self.processes and self.processes[key].poll() is None else "🔴 INACTIVO"
            logger.info(f"{service:30} {status:10} → {url}")
        
        logger.info("=" * 60)
        logger.info("🧠 Vicky AI: Integrada en Backend")
        logger.info("🚀 High Scale System: Auto-inicialización bajo demanda")
        logger.info("⚡ Workers: Optimizados por CPU (no más 272 workers!)")
        logger.info("🔗 APIs disponibles:")
        logger.info("   • /api/v1/vicky/*        - Vicky AI")
        logger.info("   • /api/v1/tasks/*        - Task Management")
        logger.info("   • /api/v1/high-scale/*   - High Scale Tasks")
        logger.info("   • /health                - Health Check")
        logger.info("🚀 Enterprise VokaFlow conquistando la galaxia...")
        logger.info("💫 Presiona Ctrl+C para detener")
        logger.info("=" * 60)
    
    def shutdown(self):
        """🛑 Cierre limpio"""
        logger.info("🛑 Iniciando cierre limpio...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
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