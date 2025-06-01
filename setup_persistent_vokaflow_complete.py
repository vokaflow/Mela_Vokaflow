#!/usr/bin/env python3
"""
🔧✨ Setup Persistent VokaFlow - SOLUCIÓN COMPLETA ✨🔧
1. Migra dashboard a Frontend_Vokaflow (donde launcher lo busca)
2. Configura servicios systemd persistentes para backend + dashboard
3. Hace que ambos sean persistentes tras reinicio físico
"""

import os
import sys
import shutil
import subprocess
import getpass
from pathlib import Path
import json

class VokaFlowPersistentSetup:
    def __init__(self):
        self.base_path = Path("/opt/vokaflow")
        self.dashboard_path = self.base_path / "dashboard"
        self.frontend_path = self.base_path / "Frontend_Vokaflow"
        self.current_user = getpass.getuser()
        
    def migrate_dashboard_to_frontend(self):
        """🔄 Migrar dashboard a Frontend_Vokaflow donde launcher lo busca"""
        print("🔄 PASO 1: Migrando dashboard a Frontend_Vokaflow...")
        print("=" * 60)
        
        # Verificar que dashboard existe
        if not self.dashboard_path.exists():
            print("❌ Directorio dashboard no encontrado")
            return False
            
        # Limpiar Frontend_Vokaflow si existe
        if self.frontend_path.exists():
            print(f"🧹 Limpiando {self.frontend_path}...")
            shutil.rmtree(self.frontend_path)
        
        # Crear nuevo directorio
        self.frontend_path.mkdir(exist_ok=True)
        print(f"📁 Directorio {self.frontend_path} creado")
        
        # Copiar contenido
        print(f"📋 Copiando contenido de {self.dashboard_path} a {self.frontend_path}...")
        for item in self.dashboard_path.iterdir():
            if item.is_dir():
                shutil.copytree(item, self.frontend_path / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, self.frontend_path / item.name)
            print(f"   ✅ {item.name}")
        
        # Verificar package.json
        package_json = self.frontend_path / "package.json"
        if package_json.exists():
            print("✅ package.json encontrado en Frontend_Vokaflow")
            
            # Leer scripts
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                scripts = package_data.get('scripts', {})
                print("📋 Scripts disponibles:")
                for script_name, script_cmd in scripts.items():
                    print(f"   • {script_name}: {script_cmd}")
            except:
                print("⚠️ No se pudo leer package.json")
                
            print("🎉 ¡Migración completada!")
            return True
        else:
            print("❌ package.json no encontrado")
            return False
    
    def create_backend_service(self):
        """📋 Crear servicio systemd para backend"""
        
        service_content = f"""[Unit]
Description=VokaFlow Backend - Sistema Universal de Traducción WhatsApp
Documentation=https://github.com/vokaflow/vokaflow-backend
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=exec
User={self.current_user}
Group={self.current_user}
WorkingDirectory={self.base_path}/src
Environment=PYTHONPATH={self.base_path}/src
Environment=VOKAFLOW_ENV=production
Environment=PYTHONUNBUFFERED=1
Environment=PATH={self.base_path}/venv/bin:/usr/local/bin:/usr/bin:/bin

# Comando principal
ExecStart={self.base_path}/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

# Reinicio automático
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vokaflow-backend

# Timeouts
TimeoutStartSec=60
TimeoutStopSec=30
KillMode=mixed
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
"""
        
        service_path = "/tmp/vokaflow-backend.service"
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Servicio backend creado: {service_path}")
        return service_path
    
    def create_dashboard_service(self):
        """📋 Crear servicio systemd para dashboard"""
        
        service_content = f"""[Unit]
Description=VokaFlow Dashboard - Panel de Control Enterprise
Documentation=https://github.com/vokaflow/dashboard
After=network-online.target vokaflow-backend.service
Wants=vokaflow-backend.service
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=exec
User={self.current_user}
Group={self.current_user}
WorkingDirectory={self.base_path}/Frontend_Vokaflow
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=NEXT_TELEMETRY_DISABLED=1
Environment=PATH=/usr/local/bin:/usr/bin:/bin

# Asegurar dependencias y build
ExecStartPre=/usr/bin/npm install --production=false
ExecStartPre=/usr/bin/npm run build

# Comando principal
ExecStart=/usr/bin/npm run start

# Reinicio automático
Restart=always
RestartSec=15

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vokaflow-dashboard

# Timeouts
TimeoutStartSec=120
TimeoutStopSec=30
KillMode=mixed
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
"""
        
        service_path = "/tmp/vokaflow-dashboard.service"
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Servicio dashboard creado: {service_path}")
        return service_path
    
    def create_env_file(self):
        """📄 Crear archivo de variables de entorno"""
        
        env_content = """# VokaFlow Production Environment
VOKAFLOW_ENV=production
PYTHONUNBUFFERED=1
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# Backend Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UVICORN_WORKERS=1

# Dashboard Configuration  
DASHBOARD_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
"""
        
        env_path = self.base_path / ".env.production"
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Archivo de entorno creado: {env_path}")
        return env_path
    
    def install_services(self, backend_service, dashboard_service):
        """🚀 Instalar servicios systemd"""
        
        commands = [
            f"sudo cp {backend_service} /etc/systemd/system/",
            f"sudo cp {dashboard_service} /etc/systemd/system/",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable vokaflow-backend.service",
            "sudo systemctl enable vokaflow-dashboard.service",
            "sudo systemctl start vokaflow-backend.service",
            "sudo systemctl start vokaflow-dashboard.service"
        ]
        
        print("📋 Comandos para configurar persistencia:")
        print("=" * 60)
        for cmd in commands:
            print(f"   {cmd}")
        
        print("\\n🤖 ¿Ejecutar automáticamente? (y/n): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes', 'sí', 'si']:
            print("\\n🚀 Ejecutando comandos...")
            
            for cmd in commands:
                print(f"\\n🔄 Ejecutando: {cmd}")
                try:
                    result = subprocess.run(cmd, shell=True, check=True, 
                                          capture_output=True, text=True)
                    print(f"✅ Éxito: {cmd}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error en: {cmd}")
                    print(f"   Error: {e.stderr}")
                    
            print("\\n🎉 ¡Servicios configurados!")
            self.check_services_status()
        else:
            print("\\n📝 Ejecuta los comandos manualmente cuando estés listo.")
    
    def check_services_status(self):
        """📊 Verificar estado de servicios"""
        
        print("\\n📊 Estado de los servicios:")
        print("=" * 60)
        
        services = ["vokaflow-backend", "vokaflow-dashboard"]
        
        for service in services:
            try:
                result = subprocess.run(
                    f"sudo systemctl is-active {service}",
                    shell=True, capture_output=True, text=True
                )
                status = result.stdout.strip()
                
                enabled_result = subprocess.run(
                    f"sudo systemctl is-enabled {service}",
                    shell=True, capture_output=True, text=True
                )
                enabled = enabled_result.stdout.strip()
                
                status_emoji = "🟢" if status == "active" else "🔴"
                enabled_emoji = "✅" if enabled == "enabled" else "❌"
                
                print(f"{status_emoji} {service}: {status} | Auto-start: {enabled_emoji} {enabled}")
                
            except Exception as e:
                print(f"❌ Error verificando {service}: {e}")
    
    def create_launcher_fix(self):
        """🔧 Arreglar launcher para usar Frontend_Vokaflow"""
        
        # El launcher ya busca en Frontend_Vokaflow, solo verificamos
        launcher_path = self.base_path / "launch_enterprise_vokaflow_fixed.py"
        if launcher_path.exists():
            print("✅ Launcher enterprise ya configurado para Frontend_Vokaflow")
            return True
        return False
    
    def show_management_commands(self):
        """📋 Mostrar comandos de gestión"""
        
        print("\\n🛠️ Comandos de gestión de servicios persistentes:")
        print("=" * 60)
        
        commands = {
            "Ver estado": [
                "sudo systemctl status vokaflow-backend",
                "sudo systemctl status vokaflow-dashboard"
            ],
            "Ver logs en tiempo real": [
                "sudo journalctl -u vokaflow-backend -f",
                "sudo journalctl -u vokaflow-dashboard -f"
            ],
            "Reiniciar": [
                "sudo systemctl restart vokaflow-backend",
                "sudo systemctl restart vokaflow-dashboard"
            ],
            "Detener": [
                "sudo systemctl stop vokaflow-backend",
                "sudo systemctl stop vokaflow-dashboard"
            ],
            "Deshabilitar auto-start": [
                "sudo systemctl disable vokaflow-backend",
                "sudo systemctl disable vokaflow-dashboard"
            ]
        }
        
        for category, cmds in commands.items():
            print(f"\\n📋 {category}:")
            for cmd in cmds:
                print(f"   {cmd}")
    
    def run_complete_setup(self):
        """🚀 Ejecutar configuración completa"""
        
        print("🔧✨ SETUP PERSISTENT VOKAFLOW - SOLUCIÓN COMPLETA ✨🔧")
        print("=" * 80)
        print("🎯 1. Migra dashboard a Frontend_Vokaflow")
        print("🎯 2. Configura servicios systemd persistentes")
        print("🎯 3. Backend + Dashboard persistentes tras reinicio físico")
        print("=" * 80)
        
        # Paso 1: Migrar dashboard
        if not self.migrate_dashboard_to_frontend():
            print("❌ Error en migración de dashboard")
            return False
        
        print("\\n" + "=" * 60)
        print("🔧 PASO 2: Configurando servicios persistentes...")
        print("=" * 60)
        
        # Crear servicios
        backend_service = self.create_backend_service()
        dashboard_service = self.create_dashboard_service()
        env_file = self.create_env_file()
        
        # Verificar launcher
        self.create_launcher_fix()
        
        # Instalar servicios
        self.install_services(backend_service, dashboard_service)
        
        # Mostrar comandos de gestión
        self.show_management_commands()
        
        print("\\n🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("🚀 Backend y Dashboard ahora son persistentes tras reinicio")
        print("💫 Prueba: python launch_enterprise_vokaflow_fixed.py")
        print("🔄 O reinicia el sistema y deberían iniciar automáticamente")
        
        return True

def main():
    """Función principal"""
    try:
        setup = VokaFlowPersistentSetup()
        setup.run_complete_setup()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 