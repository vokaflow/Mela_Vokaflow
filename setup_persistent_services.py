#!/usr/bin/env python3
"""
🔧 Setup Persistent VokaFlow Services
Configurador de servicios systemd para VokaFlow Backend + Dashboard
Hace que ambos componentes sean persistentes tras reinicio físico
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

def create_backend_service():
    """Crear servicio systemd para VokaFlow Backend"""
    
    base_path = "/opt/vokaflow"
    current_user = getpass.getuser()
    
    service_content = f"""[Unit]
Description=VokaFlow Backend - Sistema Universal de Traducción WhatsApp
Documentation=https://github.com/vokaflow/vokaflow-backend
After=network-online.target redis.service
Wants=network-online.target
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=exec
User={current_user}
Group={current_user}
WorkingDirectory={base_path}/src
Environment=PYTHONPATH={base_path}/src
Environment=VOKAFLOW_ENV=production
Environment=PYTHONUNBUFFERED=1
Environment=PATH={base_path}/venv/bin:/usr/local/bin:/usr/bin:/bin

# Comando principal
ExecStart={base_path}/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

# Reinicio automático
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vokaflow-backend

# Limits y seguridad
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

def create_dashboard_service():
    """Crear servicio systemd para VokaFlow Dashboard"""
    
    base_path = "/opt/vokaflow"
    current_user = getpass.getuser()
    
    service_content = f"""[Unit]
Description=VokaFlow Dashboard - Panel de Control Enterprise
Documentation=https://github.com/vokaflow/dashboard
After=network-online.target vokaflow-backend.service
Wants=vokaflow-backend.service
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=exec
User={current_user}
Group={current_user}
WorkingDirectory={base_path}/dashboard
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=NEXT_TELEMETRY_DISABLED=1
Environment=PATH=/usr/local/bin:/usr/bin:/bin

# Asegurar que las dependencias estén instaladas
ExecStartPre=/usr/bin/npm install --production=false

# Comando principal - build y start para producción
ExecStartPre=/usr/bin/npm run build
ExecStart=/usr/bin/npm run start

# Reinicio automático
Restart=always
RestartSec=15

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vokaflow-dashboard

# Limits y timeouts
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

def create_env_file():
    """Crear archivo de variables de entorno para producción"""
    
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
    
    env_path = "/opt/vokaflow/.env.production"
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Archivo de entorno creado: {env_path}")
    return env_path

def install_services():
    """Instalar y habilitar servicios systemd"""
    
    print("🔧 Configurando servicios systemd persistentes...")
    print("=" * 60)
    
    # Crear servicios
    backend_service = create_backend_service()
    dashboard_service = create_dashboard_service()
    env_file = create_env_file()
    
    # Comandos de instalación
    install_commands = [
        # Copiar servicios
        f"sudo cp {backend_service} /etc/systemd/system/",
        f"sudo cp {dashboard_service} /etc/systemd/system/",
        
        # Reload systemd
        "sudo systemctl daemon-reload",
        
        # Habilitar servicios para que inicien en boot
        "sudo systemctl enable vokaflow-backend.service",
        "sudo systemctl enable vokaflow-dashboard.service",
        
        # Iniciar servicios
        "sudo systemctl start vokaflow-backend.service",
        "sudo systemctl start vokaflow-dashboard.service"
    ]
    
    print("📋 Comandos para ejecutar:")
    print("=" * 60)
    
    for cmd in install_commands:
        print(f"   {cmd}")
    
    print("\n🤖 ¿Ejecutar automáticamente? (y/n): ", end="")
    response = input().strip().lower()
    
    if response in ['y', 'yes', 'sí', 'si']:
        print("\n🚀 Ejecutando comandos...")
        
        for cmd in install_commands:
            print(f"\n🔄 Ejecutando: {cmd}")
            try:
                result = subprocess.run(cmd, shell=True, check=True, 
                                      capture_output=True, text=True)
                print(f"✅ Éxito: {cmd}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en: {cmd}")
                print(f"   Error: {e.stderr}")
                
        print("\n🎉 ¡Servicios configurados!")
        check_services_status()
    else:
        print("\n📝 Ejecuta los comandos manualmente cuando estés listo.")

def check_services_status():
    """Verificar estado de los servicios"""
    
    print("\n📊 Estado de los servicios:")
    print("=" * 60)
    
    services = ["vokaflow-backend", "vokaflow-dashboard"]
    
    for service in services:
        try:
            # Verificar estado
            result = subprocess.run(
                f"sudo systemctl is-active {service}",
                shell=True, capture_output=True, text=True
            )
            status = result.stdout.strip()
            
            # Verificar si está habilitado
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

def show_management_commands():
    """Mostrar comandos de gestión de servicios"""
    
    print("\n🛠️ Comandos de gestión de servicios:")
    print("=" * 60)
    
    commands = {
        "Ver estado": [
            "sudo systemctl status vokaflow-backend",
            "sudo systemctl status vokaflow-dashboard"
        ],
        "Ver logs": [
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
        print(f"\n📋 {category}:")
        for cmd in cmds:
            print(f"   {cmd}")

def create_monitoring_script():
    """Crear script de monitoreo de servicios"""
    
    script_content = """#!/usr/bin/env python3
'''
📊 VokaFlow Services Monitor
Monitor en tiempo real de los servicios VokaFlow
'''

import subprocess
import time
import json
from datetime import datetime

def check_service_status(service_name):
    try:
        # Estado del servicio
        result = subprocess.run(
            f"systemctl is-active {service_name}",
            shell=True, capture_output=True, text=True
        )
        
        active = result.stdout.strip() == "active"
        
        # Tiempo de actividad
        uptime_result = subprocess.run(
            f"systemctl show {service_name} --property=ActiveEnterTimestamp",
            shell=True, capture_output=True, text=True
        )
        
        return {
            "name": service_name,
            "active": active,
            "status": result.stdout.strip(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "name": service_name,
            "active": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    services = ["vokaflow-backend", "vokaflow-dashboard"]
    
    print("📊 VokaFlow Services Monitor")
    print("=" * 50)
    print("🔄 Presiona Ctrl+C para salir\\n")
    
    try:
        while True:
            status_data = {}
            
            for service in services:
                status = check_service_status(service)
                status_data[service] = status
                
                emoji = "🟢" if status["active"] else "🔴"
                print(f"{emoji} {service}: {status['status']}")
            
            # URLs de acceso
            print("\\n🌐 URLs de acceso:")
            print("   • Backend:  http://localhost:8000")
            print("   • Dashboard: http://localhost:3000")
            print("   • Health:   http://localhost:8000/health")
            
            print(f"\\n🕒 Última actualización: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\\n👋 Monitor detenido")

if __name__ == "__main__":
    main()
"""
    
    script_path = "/opt/vokaflow/monitor_services.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Script de monitoreo creado: {script_path}")
    print(f"   Ejecútalo con: python {script_path}")

def main():
    """Función principal"""
    print("🔧✨ SETUP PERSISTENT VOKAFLOW SERVICES ✨🔧")
    print("=" * 60)
    print("🎯 Configurando servicios systemd persistentes")
    print("🚀 Backend + Dashboard se iniciarán automáticamente tras reinicio")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("/opt/vokaflow").exists():
        print("❌ Error: Directorio /opt/vokaflow no encontrado")
        sys.exit(1)
    
    if not Path("/opt/vokaflow/src/main.py").exists():
        print("❌ Error: main.py del backend no encontrado")
        sys.exit(1)
        
    if not Path("/opt/vokaflow/dashboard/package.json").exists():
        print("❌ Error: Dashboard no encontrado en /opt/vokaflow/dashboard")
        sys.exit(1)
    
    # Instalar servicios
    install_services()
    
    # Crear script de monitoreo
    create_monitoring_script()
    
    # Mostrar comandos de gestión
    show_management_commands()
    
    print("\n🎉 ¡Configuración completa!")
    print("🔄 Los servicios se iniciarán automáticamente tras reinicio del sistema")
    print("📊 Usa 'python /opt/vokaflow/monitor_services.py' para monitorear")

if __name__ == "__main__":
    main() 