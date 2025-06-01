#!/usr/bin/env python3
"""
Script para probar los 3 endpoints específicos del dashboard
"""

import requests
import json
import sys
import time

# URLs de los endpoints a probar
BASE_URL = "http://localhost:8000"
ENDPOINTS = [
    "/api/dashboard/stats",
    "/api/system/health", 
    "/api/translations/stats"
]

def test_endpoint(url):
    """Probar un endpoint específico"""
    try:
        print(f"\n🔍 Probando: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa")
            print(f"   📄 Datos: {json.dumps(data, indent=2)[:500]}...")
            
            # Verificar estructura esperada según el endpoint
            if "dashboard/stats" in url:
                check_dashboard_format(data)
            elif "system/health" in url:
                check_system_format(data)
            elif "translations/stats" in url:
                check_translations_format(data)
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Error de conexión - Backend no disponible")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def check_dashboard_format(data):
    """Verificar formato del endpoint dashboard/stats"""
    expected_fields = ["active_users", "total_messages", "status", "uptime"]
    
    if "success" in data and "data" in data:
        actual_data = data["data"]
        for field in expected_fields:
            if field in actual_data:
                print(f"   ✅ Campo '{field}': {actual_data[field]}")
            else:
                print(f"   ⚠️ Campo '{field}' faltante")
    else:
        print(f"   ⚠️ Formato inesperado - debería tener 'success' y 'data'")

def check_system_format(data):
    """Verificar formato del endpoint system/health"""
    expected_fields = ["cpu_usage", "gpu_usage", "memory_usage", "storage_usage"]
    
    if "success" in data and "data" in data:
        actual_data = data["data"]
        for field in expected_fields:
            if field in actual_data:
                print(f"   ✅ Campo '{field}': {actual_data[field]}")
            else:
                print(f"   ⚠️ Campo '{field}' faltante")
    else:
        print(f"   ⚠️ Formato inesperado - debería tener 'success' y 'data'")

def check_translations_format(data):
    """Verificar formato del endpoint translations/stats"""
    expected_fields = ["active", "completed", "german", "spanish", "french", "japanese"]
    
    if "success" in data and "data" in data:
        actual_data = data["data"]
        for field in expected_fields:
            if field in actual_data:
                print(f"   ✅ Campo '{field}': {actual_data[field]}")
            else:
                print(f"   ⚠️ Campo '{field}' faltante")
    else:
        print(f"   ⚠️ Formato inesperado - debería tener 'success' y 'data'")

def main():
    print("🚀 Iniciando pruebas de endpoints del dashboard")
    print(f"🎯 Backend URL: {BASE_URL}")
    
    # Verificar si el servidor está corriendo
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Servidor disponible - Status: {health_response.status_code}")
    except:
        print("❌ Servidor no disponible - Asegúrate de que esté corriendo en puerto 8000")
        return
    
    # Probar cada endpoint
    for endpoint in ENDPOINTS:
        test_endpoint(f"{BASE_URL}{endpoint}")
    
    print("\n📋 Resumen:")
    print("   Los endpoints deberían devolver:")
    print("   - /api/dashboard/stats: active_users, total_messages, status, uptime")
    print("   - /api/system/health: cpu_usage, gpu_usage, memory_usage, storage_usage")
    print("   - /api/translations/stats: active, completed, german, spanish, french, japanese")

if __name__ == "__main__":
    main() 