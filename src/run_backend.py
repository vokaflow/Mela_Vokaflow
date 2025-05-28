#!/usr/bin/env python3
"""
Script para iniciar el backend de VokaFlow
"""
import os
import sys
import subprocess
import argparse

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Dependencias básicas verificadas")
        return True
    except ImportError as e:
        print(f"❌ Error: Falta dependencia: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

def start_backend(host="0.0.0.0", port=8000, reload=False):
    """Inicia el servidor backend"""
    print(f"🚀 Iniciando servidor VokaFlow en {host}:{port}")
    
    reload_arg = "--reload" if reload else ""
    
    try:
        subprocess.run(
            f"uvicorn main:app --host {host} --port {port} {reload_arg}",
            shell=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iniciar el backend de VokaFlow")
    parser.add_argument("--host", default="0.0.0.0", help="Host para el servidor (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Puerto para el servidor (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Activar recarga automática")
    
    args = parser.parse_args()
    
    if check_dependencies():
        start_backend(args.host, args.port, args.reload)
