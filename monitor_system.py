#!/usr/bin/env python3
# VokaFlow Real-time Monitoring

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime

async def monitor_system():
    print("📊 Monitor VokaFlow - Sistema de Alta Escala")
    print("=" * 60)
    
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                # Obtener métricas
                async with session.get("http://localhost:8000/api/high-scale-tasks/metrics") as response:
                    if response.status == 200:
                        metrics = await response.json()
                        
                        # Limpiar pantalla
                        print("\033[H\033[J", end="")
                        
                        # Mostrar métricas
                        print(f"📊 Monitor VokaFlow - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print("=" * 60)
                        print(f"🚀 Throughput: {metrics.get('throughput_per_second', 0):.0f} req/s")
                        print(f"📋 Tareas pendientes: {metrics.get('total_pending_tasks', 0)}")
                        print(f"👷 Workers activos: {metrics.get('active_workers', 0)}")
                        print(f"🔗 Nodos Redis: {metrics.get('redis_nodes', 0)}")
                        print(f"🧩 Particiones: {metrics.get('partitions', 0)}")
                        
                        # Recursos del sistema
                        resources = metrics.get('system_resources', {})
                        print(f"\n💻 Recursos del Sistema:")
                        print(f"   CPU: {resources.get('cpu_percent', 0):.1f}%")
                        print(f"   Memoria: {resources.get('memory_percent', 0):.1f}%")
                        print(f"   Disco: {resources.get('disk_usage', 0):.1f}%")
                        
                        # Distribución de colas
                        queue_dist = metrics.get('queue_distribution', {})
                        if queue_dist:
                            print(f"\n📊 Distribución de Colas:")
                            for priority, count in queue_dist.items():
                                print(f"   {priority}: {count}")
                        
                        # Workers pools
                        worker_pools = metrics.get('worker_pools', {})
                        if worker_pools:
                            print(f"\n👷 Pools de Workers:")
                            for pool_type, info in worker_pools.items():
                                print(f"   {pool_type}: {info.get('max_workers', 0)} workers ({info.get('pool_type', 'Unknown')})")
                        
                    else:
                        print(f"❌ Error obteniendo métricas: HTTP {response.status}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
        
        await asyncio.sleep(2)  # Actualizar cada 2 segundos

if __name__ == "__main__":
    try:
        asyncio.run(monitor_system())
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")
        sys.exit(0)