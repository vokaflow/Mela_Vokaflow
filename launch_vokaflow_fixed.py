#!/usr/bin/env python3
"""
🚀 VokaFlow Backend Launcher - VERSIÓN CORREGIDA
Launcher para el backend con todos los errores corregidos
"""

import os
import sys
import time
import subprocess
import signal
import logging
from pathlib import Path
from datetime import datetime

# Configuración de logging limpio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vokaflow_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vokaflow-launcher")

class VokaFlowLauncher:
    """Launcher corregido para VokaFlow Backend"""
    
    def __init__(self):
        self.base_path = Path("/opt/vokaflow")
        self.venv_path = self.base_path / "venv"
        self.process = None
        self.running = True
        
        # Verificar rutas
        if not self.base_path.exists():
            logger.error(f"❌ Base path no encontrado: {self.base_path}")
            sys.exit(1)
        
        if not self.venv_path.exists():
            logger.error(f"❌ Virtual environment no encontrado: {self.venv_path}")
            sys.exit(1)
    
    def kill_existing_processes(self):
        """🔫 Eliminar procesos existentes en puerto 8000"""
        try:
            result = subprocess.run(
                ['lsof', '-ti', ':8000'], 
                capture_output=True, 
                text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], check=False)
                        logger.info(f"🔫 Proceso {pid} eliminado del puerto 8000")
                    except:
                        pass
        except:
            pass
        
        # Esperar que se libere el puerto
        time.sleep(3)
    
    def launch_backend(self):
        """🚀 Lanzar Backend VokaFlow corregido"""
        logger.info("🚀 Iniciando VokaFlow Backend...")
        
        env = os.environ.copy()
        env.update({
            'PYTHONPATH': f"{self.base_path}/src:{env.get('PYTHONPATH', '')}",
            'VOKAFLOW_ENV': 'production',
            'VOKAFLOW_BASE_PATH': str(self.base_path)
        })
        
        cmd = [
            str(self.venv_path / "bin" / "python"),
            "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1",
            "--log-level", "info",
            "--access-log"
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.base_path / "src"),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            logger.info("✅ VokaFlow Backend iniciado en puerto 8000")
            return True
        except Exception as e:
            logger.error(f"❌ Error iniciando backend: {e}")
            return False
    
    def monitor_process(self):
        """📊 Monitorear proceso backend"""
        if not self.process:
            return False
        
        # Verificar si el proceso sigue corriendo
        if self.process.poll() is not None:
            logger.error("❌ El proceso backend ha terminado inesperadamente")
            return False
        
        return True
    
    def wait_for_ready(self):
        """⏳ Esperar a que el backend esté listo"""
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts and self.running:
            try:
                import requests
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Backend está listo y respondiendo")
                    return True
            except:
                pass
            
            if not self.monitor_process():
                logger.error("❌ Proceso backend falló durante inicialización")
                return False
            
            attempt += 1
            time.sleep(2)
            if attempt % 5 == 0:
                logger.info(f"⏳ Esperando backend... ({attempt}/{max_attempts})")
        
        logger.warning("⚠️ Backend tardó en responder")
        return False
    
    def show_status(self):
        """📊 Mostrar estado del sistema"""
        logger.info("=" * 60)
        logger.info("🌟 VOKAFLOW BACKEND STATUS 🌟")
        logger.info("=" * 60)
        logger.info("🚀 Backend: http://localhost:8000")
        logger.info("📚 Documentación: http://localhost:8000/docs")
        logger.info("🔍 ReDoc: http://localhost:8000/redoc")
        logger.info("❤️ Health Check: http://localhost:8000/health")
        logger.info("=" * 60)
        logger.info("💫 VokaFlow conquistando la galaxia...")
        logger.info("🛑 Presiona Ctrl+C para detener")
        logger.info("=" * 60)
    
    def launch(self):
        """🚀 LANZAMIENTO PRINCIPAL"""
        logger.info("=" * 60)
        logger.info("🚀✨ VOKAFLOW BACKEND - VERSIÓN CORREGIDA ✨🚀")
        logger.info("=" * 60)
        
        # Limpiar procesos existentes
        logger.info("🧹 Limpiando procesos existentes...")
        self.kill_existing_processes()
        
        # Lanzar backend
        if not self.launch_backend():
            logger.error("❌ Falló el lanzamiento del backend")
            return
        
        # Esperar que esté listo
        if not self.wait_for_ready():
            logger.error("❌ Backend no respondió correctamente")
            self.shutdown()
            return
        
        # Mostrar estado
        self.show_status()
        
        # Configurar manejo de señales
        def signal_handler(signum, frame):
            logger.info("🛑 Cerrando VokaFlow Backend...")
            self.running = False
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Loop principal
        try:
            while self.running:
                if not self.monitor_process():
                    logger.error("❌ Proceso backend ha fallado")
                    break
                time.sleep(5)  # Verificar cada 5 segundos
        except KeyboardInterrupt:
            signal_handler(None, None)
    
    def shutdown(self):
        """🛑 Cierre limpio"""
        logger.info("🛑 Iniciando cierre del backend...")
        
        if self.process and self.process.poll() is None:
            logger.info("🛑 Terminando proceso backend...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
                logger.info("✅ Proceso terminado correctamente")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Forzando cierre del proceso")
                self.process.kill()
                self.process.wait()
        
        logger.info("✅ VokaFlow Backend cerrado correctamente")

def main():
    """🚀 Función principal"""
    try:
        launcher = VokaFlowLauncher()
        launcher.launch()
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 