#!/usr/bin/env python3
"""
Script de verificación rápida del backend VokaFlow
"""
import requests
import time

def test_backend():
    """Probar los endpoints principales del backend"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        ("/", "Página principal"),
        ("/health", "Health check"),
        ("/docs", "Documentación Swagger"),
        ("/redoc", "Documentación ReDoc"),
        ("/openapi.json", "OpenAPI JSON"),
        ("/api/dashboard/stats", "Dashboard stats"),
        ("/api/translations/stats", "Translation stats"),
        ("/api/system/health", "System health"),
    ]
    
    print("🧪 Probando backend VokaFlow...")
    print("=" * 50)
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {description}: {response.status_code}")
            
            if endpoint == "/docs" and response.status_code == 200:
                print(f"   📖 Documentación disponible en: {base_url}/docs")
            if endpoint == "/redoc" and response.status_code == 200:
                print(f"   📖 ReDoc disponible en: {base_url}/redoc")
                
        except requests.RequestException as e:
            print(f"❌ {description}: Error de conexión - {e}")
    
    print("=" * 50)
    print("✨ Prueba completada")

if __name__ == "__main__":
    test_backend() 