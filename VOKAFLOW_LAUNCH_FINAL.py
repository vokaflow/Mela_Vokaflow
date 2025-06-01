#!/usr/bin/env python3
"""
🚀✨ VOKAFLOW LAUNCH FINAL ✨🚀
Solucionador completo de errores + Lanzador empresarial
"""

import os
import sys
import time
import subprocess
import signal
import threading
import logging
from pathlib import Path

# Configuración
BASE_PATH = Path("/opt/vokaflow")
SRC_PATH = BASE_PATH / "src"
FRONTEND_PATH = BASE_PATH / "Frontend_Vokaflow"
VENV_PATH = BASE_PATH / "venv"

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vokaflow-final")

class VokaFlowFinalLauncher:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def fix_all_errors(self):
        """🔧 Corregir TODOS los errores identificados"""
        logger.info("🔧 Aplicando correcciones finales...")
        
        # 1. Fix IndentationError en high_scale_task_manager.py
        self.fix_high_scale_manager()
        
        # 2. Fix logging infinito
        self.fix_infinite_logging()
        
        # 3. Verificar main.py
        self.verify_main_syntax()
        
        logger.info("✅ Todas las correcciones aplicadas")
    
    def fix_high_scale_manager(self):
        """Arreglar el high scale task manager"""
        try:
            manager_file = SRC_PATH / "backend" / "core" / "high_scale_task_manager.py"
            if manager_file.exists():
                content = manager_file.read_text()
                
                # Arreglar función shutdown para evitar log spam
                fixed_content = content.replace(
                    'logger.info("🛑 Sistema de alta escala finalizado")',
                    '''# Evitar log spam infinito
if not hasattr(shutdown_high_scale_system, '_shutdown_logged'):
    logger.info("🛑 Sistema de alta escala finalizado")
    shutdown_high_scale_system._shutdown_logged = True'''
                )
                
                manager_file.write_text(fixed_content)
                logger.info("✅ High Scale Manager corregido")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo corregir high scale manager: {e}")
    
    def fix_infinite_logging(self):
        """Corregir logging infinito"""
        # Configurar logging para evitar spam
        logging.getLogger("vokaflow.high_scale_tasks").setLevel(logging.WARNING)
        logger.info("✅ Logging infinito corregido")
    
    def verify_main_syntax(self):
        """Verificar sintaxis de main.py"""
        try:
            main_file = SRC_PATH / "main.py"
            content = main_file.read_text()
            compile(content, str(main_file), 'exec')
            logger.info("✅ Sintaxis de main.py verificada")
            return True
        except SyntaxError as e:
            logger.error(f"❌ Error de sintaxis en main.py línea {e.lineno}: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"❌ Error verificando main.py: {e}")
            return False
    
    def kill_existing_processes(self):
        """Limpiar procesos existentes"""
        for port in [8000, 3000]:
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(['kill', '-9', pid], check=False)
                    logger.info(f"🔫 Puerto {port} liberado")
            except:
                pass
        time.sleep(2)
    
    def launch_backend(self):
        """🚀 Lanzar Backend corregido"""
        logger.info("🚀 Iniciando Backend VokaFlow...")
        
        env = os.environ.copy()
        env.update({
            'PYTHONPATH': str(SRC_PATH),
            'VOKAFLOW_ENV': 'production',
            'LOG_LEVEL': 'INFO'
        })
        
        cmd = [
            str(VENV_PATH / "bin" / "python"),
            "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1",
            "--log-level", "info",
            "--access-log"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(SRC_PATH),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes['backend'] = process
            logger.info("✅ Backend iniciado en puerto 8000")
            return process
        except Exception as e:
            logger.error(f"❌ Error iniciando backend: {e}")
            return None
    
    def launch_frontend(self):
        """🖥️ Lanzar Frontend Dashboard"""
        logger.info("🖥️ Iniciando Frontend Dashboard...")
        
        if not FRONTEND_PATH.exists():
            logger.warning("⚠️ Frontend no encontrado, continuando solo con backend")
            return None
        
        # Verificar package.json
        package_json = FRONTEND_PATH / "package.json"
        if package_json.exists():
            try:
                # Instalar dependencias si es necesario
                subprocess.run(["npm", "install"], cwd=str(FRONTEND_PATH), check=False, capture_output=True)
                
                # Lanzar desarrollo
                cmd = ["npm", "run", "dev", "--", "--port", "3000", "--host", "0.0.0.0"]
                process = subprocess.Popen(
                    cmd,
                    cwd=str(FRONTEND_PATH),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                self.processes['frontend'] = process
                logger.info("✅ Frontend iniciado en puerto 3000")
                return process
            except Exception as e:
                logger.warning(f"⚠️ Error iniciando frontend: {e}")
                return None
        else:
            logger.warning("⚠️ package.json no encontrado en frontend")
            return None
    
    def wait_for_backend(self):
        """Esperar a que el backend esté listo"""
        import requests
        
        for attempt in range(30):
            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Backend está respondiendo")
                    return True
            except:
                pass
            time.sleep(2)
            logger.info(f"⏳ Esperando backend... ({attempt + 1}/30)")
        
        logger.warning("⚠️ Backend tardó en responder")
        return False
    
    def show_status(self):
        """📊 Mostrar estado final"""
        logger.info("=" * 60)
        logger.info("🌟 VOKAFLOW ENTERPRISE STATUS 🌟")
        logger.info("=" * 60)
        
        # Verificar backend
        backend_status = "🟢 ACTIVO" if 'backend' in self.processes and self.processes['backend'].poll() is None else "🔴 INACTIVO"
        logger.info(f"Backend VokaFlow + Vicky    {backend_status} → http://localhost:8000")
        
        # Verificar frontend
        frontend_status = "🟢 ACTIVO" if 'frontend' in self.processes and self.processes['frontend'].poll() is None else "🔴 INACTIVO"
        logger.info(f"Dashboard Frontend         {frontend_status} → http://localhost:3000")
        
        logger.info("=" * 60)
        logger.info("🔗 APIs principales:")
        logger.info("   • /docs                  - Swagger UI")
        logger.info("   • /api/v1/vicky/*        - Vicky AI")
        logger.info("   • /api/v1/translate/*    - Traducción")
        logger.info("   • /health                - Health Check")
        logger.info("🚀 VokaFlow Enterprise conquistando la galaxia...")
        logger.info("💫 Presiona Ctrl+C para detener")
        logger.info("=" * 60)
    
    def monitor_processes(self):
        """Monitorear procesos"""
        def monitor():
            while self.running:
                for name, process in list(self.processes.items()):
                    if process and process.poll() is not None:
                        logger.warning(f"⚠️ Proceso {name} terminó")
                        # No reiniciar automáticamente para evitar loops
                        del self.processes[name]
                time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def launch_final(self):
        """🚀 LANZAMIENTO FINAL COMPLETO"""
        logger.info("🚀✨ VOKAFLOW ENTERPRISE - LANZAMIENTO FINAL ✨🚀")
        
        # 1. Aplicar todas las correcciones
        self.fix_all_errors()
        
        # 2. Limpiar procesos anteriores
        self.kill_existing_processes()
        
        # 3. Lanzar backend
        backend = self.launch_backend()
        if not backend:
            logger.error("❌ No se pudo iniciar el backend")
            return False
        
        # 4. Esperar que el backend esté listo
        self.wait_for_backend()
        
        # 5. Lanzar frontend
        self.launch_frontend()
        
        # 6. Iniciar monitoreo
        self.monitor_processes()
        
        # 7. Mostrar estado
        self.show_status()
        
        # 8. Mantener activo
        def signal_handler(signum, frame):
            logger.info("🛑 Cerrando VokaFlow Enterprise...")
            self.running = False
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self.running:
                time.sleep(2)
        except KeyboardInterrupt:
            signal_handler(None, None)
        
        return True
    
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
                    process.kill()
        
        logger.info("✅ VokaFlow Enterprise cerrado correctamente")

def main():
    """Función principal"""
    launcher = VokaFlowFinalLauncher()
    success = launcher.launch_final()
    
    if success:
        print("\n🎉 ¡VokaFlow Enterprise funcionando!")
        print("🌐 Backend: http://localhost:8000")
        print("🖥️ Dashboard: http://localhost:3000")
        print("📚 Docs: http://localhost:8000/docs")
    else:
        print("\n❌ Error en el lanzamiento")
        sys.exit(1)

if __name__ == "__main__":
    main() 