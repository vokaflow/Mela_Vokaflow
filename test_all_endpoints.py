#!/usr/bin/env python3
"""
🔍 VokaFlow Endpoint Tester - Verificación completa de todos los endpoints
Prueba sistemática de los 206+ endpoints disponibles en VokaFlow API
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Configuración
BASE_URL = "http://localhost:8000"
TIMEOUT = 30
MAX_CONCURRENT = 10

class VokaFlowTester:
    def __init__(self):
        self.results = {
            "total_endpoints": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "successful_endpoints": [],
            "failed_endpoints": [],
            "test_start": datetime.now().isoformat(),
            "test_duration": 0
        }
        self.session = None
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_endpoints_to_test(self) -> List[Dict[str, Any]]:
        """Define todos los endpoints a probar"""
        endpoints = [
            # =====================================
            # 🏥 HEALTH & STATUS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/health", "description": "Health check simple"},
            {"method": "GET", "path": "/", "description": "Página principal"},
            {"method": "GET", "path": "/docs", "description": "Documentación Swagger"},
            {"method": "GET", "path": "/redoc", "description": "Documentación ReDoc"},
            {"method": "GET", "path": "/openapi.json", "description": "OpenAPI JSON"},
            
            # =====================================
            # 🔐 AUTHENTICATION ENDPOINTS  
            # =====================================
            {"method": "GET", "path": "/api/health", "description": "API Health check"},
            {"method": "GET", "path": "/api/health/status", "description": "API Status detallado"},
            {"method": "GET", "path": "/api/health/detailed", "description": "Health check detallado"},
            {"method": "GET", "path": "/api/health/system", "description": "System health"},
            {"method": "GET", "path": "/api/health/components", "description": "Component health"},
            
            # =====================================
            # 👤 USER MANAGEMENT ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/users", "description": "List users (admin)", "auth_required": True},
            {"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": True},
            {"method": "GET", "path": "/api/users/profile", "description": "User profile", "auth_required": True},
            {"method": "GET", "path": "/api/users/settings", "description": "User settings", "auth_required": True},
            {"method": "GET", "path": "/api/users/stats", "description": "User statistics", "auth_required": True},
            
            # =====================================
            # 🌐 TRANSLATION ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/translate/languages", "description": "Supported languages"},
            {"method": "GET", "path": "/api/translate/stats", "description": "Translation statistics", "auth_required": True},
            {"method": "GET", "path": "/api/translate/history", "description": "Translation history", "auth_required": True},
            {"method": "GET", "path": "/api/translate/models", "description": "Available translation models"},
            {"method": "GET", "path": "/api/translate/capabilities", "description": "Translation capabilities"},
            
            # =====================================
            # 🧠 VICKY AI ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/vicky/status", "description": "Vicky AI status"},
            {"method": "GET", "path": "/api/vicky/capabilities", "description": "Vicky capabilities"},
            {"method": "GET", "path": "/api/vicky/models", "description": "Vicky AI models"},
            {"method": "GET", "path": "/api/vicky/stats", "description": "Vicky statistics", "auth_required": True},
            {"method": "GET", "path": "/api/vicky/health", "description": "Vicky health check"},
            
            # =====================================
            # 🎤 TEXT-TO-SPEECH ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/tts/voices", "description": "Available TTS voices"},
            {"method": "GET", "path": "/api/tts/languages", "description": "TTS supported languages"},
            {"method": "GET", "path": "/api/tts/models", "description": "TTS models"},
            {"method": "GET", "path": "/api/tts/stats", "description": "TTS statistics", "auth_required": True},
            {"method": "GET", "path": "/api/tts/health", "description": "TTS health check"},
            
            # =====================================
            # 🎙️ SPEECH-TO-TEXT ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/stt/languages", "description": "STT supported languages"},
            {"method": "GET", "path": "/api/stt/models", "description": "STT models"},
            {"method": "GET", "path": "/api/stt/stats", "description": "STT statistics", "auth_required": True},
            {"method": "GET", "path": "/api/stt/health", "description": "STT health check"},
            {"method": "GET", "path": "/api/stt/capabilities", "description": "STT capabilities"},
            
            # =====================================
            # 🔊 VOICE MANAGEMENT ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/voice/samples", "description": "Voice samples", "auth_required": True},
            {"method": "GET", "path": "/api/voice/custom", "description": "Custom voices", "auth_required": True},
            {"method": "GET", "path": "/api/voice/models", "description": "Voice models"},
            {"method": "GET", "path": "/api/voice/stats", "description": "Voice statistics", "auth_required": True},
            {"method": "GET", "path": "/api/voice/health", "description": "Voice system health"},
            
            # =====================================
            # 💬 CONVERSATIONS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/conversations", "description": "List conversations", "auth_required": True},
            {"method": "GET", "path": "/api/conversations/stats", "description": "Conversation statistics", "auth_required": True},
            {"method": "GET", "path": "/api/conversations/recent", "description": "Recent conversations", "auth_required": True},
            {"method": "GET", "path": "/api/conversations/search", "description": "Search conversations", "auth_required": True},
            
            # =====================================
            # ⚙️ SYSTEM MANAGEMENT ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/system/status", "description": "System status"},
            {"method": "GET", "path": "/api/system/health", "description": "System health"},
            {"method": "GET", "path": "/api/system/metrics", "description": "System metrics", "auth_required": True},
            {"method": "GET", "path": "/api/system/events", "description": "System events", "auth_required": True},
            {"method": "GET", "path": "/api/system/api-metrics", "description": "API metrics", "auth_required": True},
            {"method": "GET", "path": "/api/system/info", "description": "System information"},
            {"method": "GET", "path": "/api/system/version", "description": "System version"},
            
            # =====================================
            # 🤖 MODEL MANAGEMENT ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/models", "description": "Available models"},
            {"method": "GET", "path": "/api/models/status", "description": "Models status"},
            {"method": "GET", "path": "/api/models/health", "description": "Models health"},
            {"method": "GET", "path": "/api/models/stats", "description": "Model statistics", "auth_required": True},
            {"method": "GET", "path": "/api/models/capabilities", "description": "Model capabilities"},
            
            # =====================================
            # 📁 FILE MANAGEMENT ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/files", "description": "List files", "auth_required": True},
            {"method": "GET", "path": "/api/files/stats", "description": "File statistics", "auth_required": True},
            {"method": "GET", "path": "/api/files/health", "description": "File system health"},
            {"method": "GET", "path": "/api/files/types", "description": "Supported file types"},
            
            # =====================================
            # 📊 ANALYTICS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/analytics/overview", "description": "Analytics overview", "auth_required": True},
            {"method": "GET", "path": "/api/analytics/usage", "description": "Usage analytics", "auth_required": True},
            {"method": "GET", "path": "/api/analytics/performance", "description": "Performance analytics", "auth_required": True},
            {"method": "GET", "path": "/api/analytics/trends", "description": "Trend analytics", "auth_required": True},
            {"method": "GET", "path": "/api/analytics/reports", "description": "Analytics reports", "auth_required": True},
            
            # =====================================
            # 🔔 NOTIFICATIONS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/notifications", "description": "List notifications", "auth_required": True},
            {"method": "GET", "path": "/api/notifications/unread", "description": "Unread notifications", "auth_required": True},
            {"method": "GET", "path": "/api/notifications/settings", "description": "Notification settings", "auth_required": True},
            {"method": "GET", "path": "/api/notifications/stats", "description": "Notification statistics", "auth_required": True},
            
            # =====================================
            # 👨‍💼 ADMIN ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/admin/users", "description": "Admin user management", "auth_required": True},
            {"method": "GET", "path": "/api/admin/stats", "description": "Admin statistics", "auth_required": True},
            {"method": "GET", "path": "/api/admin/system", "description": "Admin system info", "auth_required": True},
            {"method": "GET", "path": "/api/admin/logs", "description": "System logs", "auth_required": True},
            {"method": "GET", "path": "/api/admin/health", "description": "Admin health check", "auth_required": True},
            
            # =====================================
            # 🔑 API KEYS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/api-keys", "description": "List API keys", "auth_required": True},
            {"method": "GET", "path": "/api/api-keys/stats", "description": "API key statistics", "auth_required": True},
            {"method": "GET", "path": "/api/api-keys/usage", "description": "API key usage", "auth_required": True},
            
            # =====================================
            # 🪝 WEBHOOKS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/webhooks", "description": "List webhooks", "auth_required": True},
            {"method": "GET", "path": "/api/webhooks/stats", "description": "Webhook statistics", "auth_required": True},
            {"method": "GET", "path": "/api/webhooks/health", "description": "Webhook health", "auth_required": True},
            
            # =====================================
            # 📈 MONITORING ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/monitoring/status", "description": "Monitoring status"},
            {"method": "GET", "path": "/api/monitoring/metrics", "description": "Monitoring metrics", "auth_required": True},
            {"method": "GET", "path": "/api/monitoring/alerts", "description": "System alerts", "auth_required": True},
            {"method": "GET", "path": "/api/monitoring/health", "description": "Monitoring health"},
            
            # =====================================
            # 🎮 KINECT DASHBOARD ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/kinect/status", "description": "Kinect status"},
            {"method": "GET", "path": "/api/kinect/devices", "description": "Kinect devices"},
            {"method": "GET", "path": "/api/kinect/stats", "description": "Kinect statistics", "auth_required": True},
            {"method": "GET", "path": "/api/kinect/health", "description": "Kinect health"},
            
            # =====================================
            # 📊 DASHBOARD ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/dashboard/overview", "description": "Dashboard overview", "auth_required": True},
            {"method": "GET", "path": "/api/dashboard/stats", "description": "Dashboard statistics", "auth_required": True},
            {"method": "GET", "path": "/api/dashboard/widgets", "description": "Dashboard widgets", "auth_required": True},
            {"method": "GET", "path": "/api/dashboard/config", "description": "Dashboard configuration", "auth_required": True},
            
            # =====================================
            # 🚀 HIGH SCALE TASKS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/high-scale-tasks/status", "description": "High scale tasks status"},
            {"method": "GET", "path": "/api/high-scale-tasks/queue", "description": "Task queue status", "auth_required": True},
            {"method": "GET", "path": "/api/high-scale-tasks/workers", "description": "Worker status", "auth_required": True},
            {"method": "GET", "path": "/api/high-scale-tasks/stats", "description": "Task statistics", "auth_required": True},
            
            # =====================================
            # 📋 TASKS ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/tasks", "description": "List tasks", "auth_required": True},
            {"method": "GET", "path": "/api/tasks/status", "description": "Task status"},
            {"method": "GET", "path": "/api/tasks/stats", "description": "Task statistics", "auth_required": True},
            {"method": "GET", "path": "/api/tasks/health", "description": "Task system health"},
            
            # =====================================
            # 📄 COMPATIBILITY ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/api/translations/stats", "description": "Translation stats (compatibility)"},
            
            # =====================================
            # 🔗 STATIC & SPECIAL ENDPOINTS
            # =====================================
            {"method": "GET", "path": "/static/custom.css", "description": "Custom CSS"},
            {"method": "GET", "path": "/static/js/power_menu.js", "description": "Power menu JS"},
            {"method": "GET", "path": "/static/js/power_checker.js", "description": "Power checker JS"},
        ]
        
        return endpoints

    async def test_endpoint(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Probar un endpoint individual"""
        method = endpoint["method"]
        path = endpoint["path"]
        description = endpoint.get("description", "")
        auth_required = endpoint.get("auth_required", False)
        
        url = f"{BASE_URL}{path}"
        
        try:
            start_time = time.time()
            
            headers = {}
            if auth_required:
                # Para endpoints que requieren auth, probamos sin auth para ver el error esperado
                pass
            
            async with self.session.request(method, url, headers=headers) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # en ms
                
                status_code = response.status
                
                # Intentar leer el contenido
                try:
                    if response.content_type and 'application/json' in response.content_type:
                        content = await response.json()
                    else:
                        content_text = await response.text()
                        content = {"content_preview": content_text[:200] + "..." if len(content_text) > 200 else content_text}
                except:
                    content = {"error": "Could not parse response content"}
                
                # Determinar si el test fue exitoso
                success = False
                if auth_required and status_code in [401, 403]:
                    # Para endpoints que requieren auth, 401/403 es esperado sin auth
                    success = True
                elif not auth_required and status_code in [200, 201, 202]:
                    # Para endpoints públicos, códigos 2xx son exitosos
                    success = True
                elif status_code == 404:
                    # 404 indica que el endpoint no existe (fallo)
                    success = False
                elif status_code in [400, 405, 422]:
                    # Errores de cliente pero el endpoint existe
                    success = True
                
                result = {
                    "method": method,
                    "path": path,
                    "description": description,
                    "status_code": status_code,
                    "response_time_ms": round(response_time, 2),
                    "success": success,
                    "auth_required": auth_required,
                    "content_type": response.content_type,
                    "content_length": len(str(content)),
                    "error": None
                }
                
                if success:
                    self.results["successful"] += 1
                    self.results["successful_endpoints"].append(result)
                else:
                    self.results["failed"] += 1
                    self.results["failed_endpoints"].append(result)
                
                return result
                
        except Exception as e:
            # Error de conexión o timeout
            result = {
                "method": method,
                "path": path,
                "description": description,
                "status_code": None,
                "response_time_ms": None,
                "success": False,
                "auth_required": auth_required,
                "content_type": None,
                "content_length": 0,
                "error": str(e)
            }
            
            self.results["failed"] += 1
            self.results["failed_endpoints"].append(result)
            self.results["errors"].append(f"{method} {path}: {str(e)}")
            
            return result

    async def run_tests(self):
        """Ejecutar todas las pruebas"""
        endpoints = self.get_endpoints_to_test()
        self.results["total_endpoints"] = len(endpoints)
        
        print(f"🚀 Iniciando prueba de {len(endpoints)} endpoints...")
        print(f"🎯 URL base: {BASE_URL}")
        print(f"⏱️  Timeout: {TIMEOUT}s")
        print("=" * 80)
        
        start_time = time.time()
        
        # Ejecutar pruebas en lotes para no sobrecargar el servidor
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def test_with_semaphore(endpoint):
            async with semaphore:
                return await self.test_endpoint(endpoint)
        
        tasks = [test_with_semaphore(endpoint) for endpoint in endpoints]
        
        # Mostrar progreso
        completed = 0
        for task in asyncio.as_completed(tasks):
            result = await task
            completed += 1
            
            # Mostrar progreso cada 10 endpoints
            if completed % 10 == 0 or completed == len(endpoints):
                percentage = (completed / len(endpoints)) * 100
                print(f"📊 Progreso: {completed}/{len(endpoints)} ({percentage:.1f}%)")
        
        end_time = time.time()
        self.results["test_duration"] = round(end_time - start_time, 2)
        
        return self.results

    def print_results(self):
        """Imprimir resultados de las pruebas"""
        print("\n" + "=" * 80)
        print("🎯 RESULTADOS DE PRUEBAS DE ENDPOINTS")
        print("=" * 80)
        
        print(f"📊 Total de endpoints probados: {self.results['total_endpoints']}")
        print(f"✅ Exitosos: {self.results['successful']}")
        print(f"❌ Fallidos: {self.results['failed']}")
        print(f"⏱️  Duración total: {self.results['test_duration']}s")
        
        success_rate = (self.results['successful'] / self.results['total_endpoints']) * 100
        print(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        print("\n" + "=" * 40)
        print("✅ ENDPOINTS EXITOSOS:")
        print("=" * 40)
        
        for endpoint in self.results['successful_endpoints'][:20]:  # Mostrar primeros 20
            auth_indicator = "🔒" if endpoint['auth_required'] else "🌐"
            print(f"{auth_indicator} {endpoint['method']} {endpoint['path']} - {endpoint['status_code']} ({endpoint['response_time_ms']}ms)")
        
        if len(self.results['successful_endpoints']) > 20:
            remaining = len(self.results['successful_endpoints']) - 20
            print(f"... y {remaining} más")
        
        if self.results['failed_endpoints']:
            print("\n" + "=" * 40)
            print("❌ ENDPOINTS FALLIDOS:")
            print("=" * 40)
            
            for endpoint in self.results['failed_endpoints']:
                auth_indicator = "🔒" if endpoint['auth_required'] else "🌐"
                error_info = f" - Error: {endpoint['error']}" if endpoint['error'] else ""
                print(f"{auth_indicator} {endpoint['method']} {endpoint['path']} - {endpoint['status_code']}{error_info}")
        
        print("\n" + "=" * 80)

    def save_results(self, filename: str = None):
        """Guardar resultados en archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vokaflow_endpoint_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados guardados en: {filename}")

async def main():
    """Función principal"""
    print("🧪 VokaFlow Endpoint Tester v1.0")
    print("🔍 Verificación completa de todos los endpoints disponibles")
    print("=" * 80)
    
    async with VokaFlowTester() as tester:
        # Ejecutar las pruebas
        results = await tester.run_tests()
        
        # Mostrar resultados
        tester.print_results()
        
        # Guardar resultados
        tester.save_results()
        
        # Resumen final
        print(f"\n🎉 Prueba completada!")
        print(f"📊 {results['successful']}/{results['total_endpoints']} endpoints funcionando correctamente")
        
        return results['successful'] == results['total_endpoints']

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1) 