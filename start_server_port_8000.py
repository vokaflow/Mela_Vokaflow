#!/usr/bin/env python3
"""
Script para iniciar el servidor en el puerto 8000
"""
import os
import sys
import uvicorn

# Configurar la ruta del proyecto
sys.path.append("/opt/vokaflow")
os.environ["PYTHONPATH"] = "/opt/vokaflow"
os.environ["PORT"] = "8000"

print("Configuración del entorno completada")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"PORT: {os.environ.get('PORT')}")

try:
    print("Iniciando servidor en puerto 8000...")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
    print("Servidor iniciado correctamente")
except Exception as e:
    print(f"Error al iniciar el servidor: {e}")
    import traceback
    traceback.print_exc() 