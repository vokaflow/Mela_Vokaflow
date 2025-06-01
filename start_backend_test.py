#!/usr/bin/env python3
"""
Script para iniciar el backend en modo test y verificar los endpoints
"""

import sys
import time
import subprocess
import requests
import signal
import os
from threading import Thread
import json

class BackendTester:
    def __init__(self):
        self.backend_process = None
        self.base_url = "http://localhost:8000"
    
    def start_backend(self):
        """Iniciar el backend en segundo plano"""
        try:
            print("🚀 Iniciando backend...")
            
            # Cambiar al directorio correcto
            os.chdir("/opt/vokaflow")
            
            # Iniciar el backend en segundo plano
            self.backend_process = subprocess.Popen(
                [sys.executable, "src/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd="/opt/vokaflow"
            )
            
            # Esperar a que el servidor se inicie
            for i in range(30):  # Máximo 30 segundos
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Backend iniciado exitosamente en {i+1} segundos")
                        return True
                except:
                    time.sleep(1)
                    print(f"   Esperando... {i+1}/30")
            
            print("❌ Error: Backend no se inició en 30 segundos")
            return False
            
        except Exception as e:
            print(f"❌ Error al iniciar backend: {e}")
            return False
    
    def test_endpoints(self):
        """Probar los 3 endpoints específicos"""
        endpoints = [
            ("/api/dashboard/stats", "Dashboard Stats"),
            ("/api/system/health", "System Health"),
            ("/api/translations/stats", "Translations Stats")
        ]
        
        print("\n📋 Probando endpoints específicos del dashboard...")
        print("="*60)
        
        success_count = 0
        
        for endpoint, name in endpoints:
            try:
                print(f"\n🔍 Probando {name}: {endpoint}")
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Status: 200 - Respuesta exitosa")
                    
                    # Verificar formato de respuesta
                    if "success" in data and "data" in data:
                        print(f"   ✅ Formato correcto (success + data)")
                        
                        # Mostrar algunos campos clave
                        actual_data = data["data"]
                        sample_fields = list(actual_data.keys())[:5]
                        for field in sample_fields:
                            print(f"   📄 {field}: {actual_data[field]}")
                        
                        success_count += 1
                    else:
                        print(f"   ⚠️ Formato inesperado")
                        print(f"   📄 Estructura: {list(data.keys())}")
                else:
                    print(f"   ❌ Status: {response.status_code}")
                    print(f"   📄 Error: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print(f"\n📊 Resultado: {success_count}/3 endpoints funcionando correctamente")
        return success_count == 3
    
    def stop_backend(self):
        """Detener el backend"""
        if self.backend_process:
            print("\n🛑 Deteniendo backend...")
            try:
                # Intentar terminación graceful
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Forzar terminación si es necesario
                self.backend_process.kill()
                self.backend_process.wait()
            print("✅ Backend detenido")
    
    def run_test(self):
        """Ejecutar prueba completa"""
        try:
            print("🧪 Iniciando prueba completa del backend")
            print("="*60)
            
            # 1. Iniciar backend
            if not self.start_backend():
                return False
            
            # 2. Probar endpoints
            success = self.test_endpoints()
            
            # 3. Mostrar resumen
            print("\n🏁 RESUMEN FINAL")
            print("="*60)
            if success:
                print("✅ TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE")
                print("🎉 El frontend ya puede conectarse y obtener datos reales")
            else:
                print("❌ HAY PROBLEMAS CON ALGUNOS ENDPOINTS")
                print("🔧 Revisa los logs del backend para más detalles")
            
            return success
            
        finally:
            # Siempre detener el backend al final
            self.stop_backend()

def main():
    tester = BackendTester()
    
    # Manejar Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n\n🛑 Interrupción detectada, deteniendo...")
        tester.stop_backend()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Ejecutar prueba
    success = tester.run_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 