#!/usr/bin/env python3
"""
Script para iniciar el backend VokaFlow correctamente
"""
import os
import sys
import subprocess

def main():
    print("🚀 Iniciando VokaFlow Backend...")
    
    # Cambiar al directorio src
    os.chdir('/opt/vokaflow/src')
    
    # Activar el entorno virtual y ejecutar
    cmd = [
        sys.executable, 
        '-m', 'uvicorn', 
        'main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--reload'
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ Backend detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 