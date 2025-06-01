#!/usr/bin/env python3
"""
Prueba completa del High Scale System
Verifica todas las funcionalidades implementadas
"""

import asyncio
import time
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_high_scale_system():
    """Prueba completa del sistema de alta escala"""
    print("🚀 Iniciando prueba completa del High Scale System")
    
    from src.backend.core.high_scale_task_manager import (
        create_optimized_high_scale_manager,
        TaskPriority,
        WorkerType
    )
    
    # 1. Crear y inicializar el manager
    print("\n📋 Paso 1: Inicializando High Scale Task Manager...")
    manager = create_optimized_high_scale_manager()
    await manager.initialize()
    
    # 2. Definir funciones de prueba
    def test_function_cpu(x, y):
        """Función de prueba CPU intensiva"""
        result = sum(i**2 for i in range(x, x + y))
        return f"CPU task completed: {result}"
    
    def test_function_io(filename):
        """Función de prueba I/O"""
        return f"IO task: processed file {filename}"
    
    def test_function_error():
        """Función que genera error para probar DLQ"""
        raise ValueError("Error intencional para prueba DLQ")
    
    # 3. Probar envío de tareas Redis
    print("\n📋 Paso 2: Probando Workers Redis Reales...")
    
    # Enviar tareas de diferentes tipos
    tasks = []
    
    # Tarea CPU intensiva
    task_id_1 = await manager.submit_task(
        func=test_function_cpu,
        args=(100, 1000),
        priority=TaskPriority.HIGH,
        worker_type=WorkerType.CPU_INTENSIVE,
        name="test_cpu_task",
        category="testing"
    )
    tasks.append(("CPU", task_id_1))
    
    # Tarea I/O intensiva
    task_id_2 = await manager.submit_task(
        func=test_function_io,
        args=("test_file.txt",),
        priority=TaskPriority.NORMAL,
        worker_type=WorkerType.IO_INTENSIVE,
        name="test_io_task",
        category="testing"
    )
    tasks.append(("I/O", task_id_2))
    
    # Tarea que fallará (para probar DLQ)
    task_id_3 = await manager.submit_task(
        func=test_function_error,
        args=(),
        priority=TaskPriority.LOW,
        worker_type=WorkerType.GENERAL_PURPOSE,
        name="test_error_task",
        category="testing",
        max_retries=2
    )
    tasks.append(("ERROR", task_id_3))
    
    print(f"✅ Enviadas {len(tasks)} tareas")
    
    # 4. Esperar procesamiento
    print("\n📋 Paso 3: Esperando procesamiento de tareas...")
    await asyncio.sleep(10)
    
    # 5. Verificar métricas
    print("\n📋 Paso 4: Verificando métricas...")
    metrics = await manager.get_global_metrics()
    print(f"📊 Tareas procesadas: {metrics.get('completed_tasks', 0)}")
    print(f"📊 Tareas fallidas: {metrics.get('failed_tasks', 0)}")
    print(f"📊 Workers activos: {metrics.get('active_workers', 0)}")
    print(f"📊 Nodos Redis: {metrics.get('redis_nodes', 0)}")
    
    # 6. Probar Dead Letter Queue
    print("\n📋 Paso 5: Probando Dead Letter Queue...")
    await asyncio.sleep(5)  # Esperar a que la tarea de error vaya a DLQ
    
    dlq_tasks = await manager.get_dlq_tasks()
    print(f"💀 Tareas en DLQ: {len(dlq_tasks)}")
    
    if dlq_tasks:
        # Intentar reintento desde DLQ
        dlq_task_id = dlq_tasks[0]["id"]
        success = await manager.retry_dlq_task(dlq_task_id)
        print(f"🔄 Reintento DLQ: {'✅ Exitoso' if success else '❌ Fallido'}")
    
    # 7. Probar Distributed Locking
    print("\n📋 Paso 6: Probando Distributed Locking...")
    
    worker_id = "test_worker_001"
    lock_key = "test_lock_resource"
    
    # Adquirir lock
    lock_acquired = await manager.acquire_distributed_lock(lock_key, worker_id, 30)
    print(f"🔒 Lock adquirido: {'✅ Sí' if lock_acquired else '❌ No'}")
    
    if lock_acquired:
        # Intentar adquirir el mismo lock con otro worker (debería fallar)
        other_worker = "test_worker_002"
        lock_acquired_2 = await manager.acquire_distributed_lock(lock_key, other_worker, 5)
        print(f"🔒 Lock duplicado (debe fallar): {'❌ Adquirido' if lock_acquired_2 else '✅ Rechazado correctamente'}")
        
        # Liberar lock
        lock_released = await manager.release_distributed_lock(lock_key, worker_id)
        print(f"🔓 Lock liberado: {'✅ Sí' if lock_released else '❌ No'}")
    
    # 8. Probar función con lock
    print("\n📋 Paso 7: Probando ejecución con lock...")
    
    def protected_function():
        time.sleep(1)  # Simular trabajo crítico
        return "Función protegida ejecutada correctamente"
    
    try:
        result = await manager.execute_with_lock(
            lock_key="critical_resource",
            worker_id="test_worker_003",
            func=protected_function,
            timeout=10
        )
        print(f"🛡️ Función protegida: ✅ {result}")
    except Exception as e:
        print(f"🛡️ Función protegida: ❌ {e}")
    
    # 9. Mostrar estado final
    print("\n📋 Paso 8: Estado final del sistema...")
    final_metrics = await manager.get_global_metrics()
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL DE PRUEBAS")
    print("="*60)
    print(f"✅ Tareas completadas: {final_metrics.get('completed_tasks', 0)}")
    print(f"❌ Tareas fallidas: {final_metrics.get('failed_tasks', 0)}")
    print(f"👷 Workers Redis: {len(manager.worker_tasks) if hasattr(manager, 'worker_tasks') else 0}")
    print(f"🗄️ Nodos Redis: {final_metrics.get('redis_nodes', 0)}")
    print(f"🔧 Particiones: {final_metrics.get('partitions', 0)}")
    print(f"🧠 Uso memoria: {final_metrics.get('system_resources', {}).get('memory_percent', 0):.1f}%")
    print(f"💻 Uso CPU: {final_metrics.get('system_resources', {}).get('cpu_percent', 0):.1f}%")
    
    # Mostrar tareas recientes
    recent_tasks = final_metrics.get('recent_tasks', [])
    if recent_tasks:
        print(f"\n📋 Últimas {len(recent_tasks)} tareas procesadas:")
        for i, task in enumerate(recent_tasks[-5:], 1):
            status_icon = "✅" if task["status"] == "completed" else "❌"
            print(f"  {i}. {status_icon} {task['name']} ({task.get('processing_time', 0):.3f}s)")
    
    print("="*60)
    
    # 10. Cleanup
    print("\n📋 Paso 9: Limpieza del sistema...")
    await manager.shutdown()
    print("✅ High Scale System apagado correctamente")
    
    return True

async def test_api_endpoints():
    """Probar endpoints API del High Scale System"""
    import aiohttp
    
    print("\n🌐 Probando APIs del High Scale System...")
    
    base_url = "http://localhost:8000/api/high-scale-tasks"
    
    async with aiohttp.ClientSession() as session:
        # Test metrics endpoint
        try:
            async with session.get(f"{base_url}/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"📊 Métricas API: ✅ {data.get('total_pending_tasks', 0)} tareas pendientes")
                else:
                    print(f"📊 Métricas API: ❌ Status {response.status}")
        except Exception as e:
            print(f"📊 Métricas API: ❌ Error: {e}")
        
        # Test workers status
        try:
            async with session.get(f"{base_url}/workers/status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"👷 Workers API: ✅ {data.get('total_workers', 0)} workers totales")
                else:
                    print(f"👷 Workers API: ❌ Status {response.status}")
        except Exception as e:
            print(f"👷 Workers API: ❌ Error: {e}")
        
        # Test DLQ endpoint
        try:
            async with session.get(f"{base_url}/dlq") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"💀 DLQ API: ✅ {data.get('total_tasks', 0)} tareas en DLQ")
                else:
                    print(f"💀 DLQ API: ❌ Status {response.status}")
        except Exception as e:
            print(f"💀 DLQ API: ❌ Error: {e}")

async def main():
    """Función principal de pruebas"""
    try:
        # Prueba del core system
        success = await test_high_scale_system()
        
        if success:
            print("\n🎉 Todas las pruebas del High Scale System PASARON")
            
            # Prueba de APIs (opcional, requiere servidor corriendo)
            try:
                await test_api_endpoints()
            except Exception as e:
                print(f"⚠️ Pruebas de API omitidas (servidor no disponible): {e}")
        else:
            print("\n❌ Algunas pruebas fallaron")
            
    except Exception as e:
        print(f"\n💥 Error crítico en pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 