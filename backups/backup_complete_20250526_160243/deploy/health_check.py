#!/usr/bin/env python3
"""
Script de verificación de salud para VokaFlow
"""
import asyncio
import aiohttp
import sys
import os
import json
from datetime import datetime

async def check_endpoint(session, url, name):
    """Verificar un endpoint específico"""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                data = await response.text()
                return {"name": name, "status": "✅ OK", "response_time": response.headers.get('X-Response-Time', 'N/A')}
            else:
                return {"name": name, "status": f"❌ HTTP {response.status}", "response_time": "N/A"}
    except asyncio.TimeoutError:
        return {"name": name, "status": "❌ Timeout", "response_time": "N/A"}
    except Exception as e:
        return {"name": name, "status": f"❌ Error: {str(e)[:50]}", "response_time": "N/A"}

async def main():
    """Función principal de verificación"""
    base_url = os.getenv('VOKAFLOW_URL', 'http://localhost')
    
    endpoints = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/api/", "API Root"),
        (f"{base_url}/api/vicky/status", "Vicky Status"),
        (f"{base_url}/api/db-test", "Database Test"),
    ]
    
    print(f"🔍 Verificando salud de VokaFlow - {datetime.now()}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        tasks = [check_endpoint(session, url, name) for url, name in endpoints]
        results = await asyncio.gather(*tasks)
    
    # Mostrar resultados
    all_ok = True
    for result in results:
        print(f"{result['status']} {result['name']} ({result['response_time']})")
        if "❌" in result['status']:
            all_ok = False
    
    print("=" * 60)
    if all_ok:
        print("✅ Todos los servicios están funcionando correctamente")
        sys.exit(0)
    else:
        print("❌ Algunos servicios tienen problemas")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
