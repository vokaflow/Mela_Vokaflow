#!/usr/bin/env python3
# VokaFlow Load Test Script

import asyncio
import aiohttp
import time
import json
from datetime import datetime

async def send_task_batch(session, batch_size=100):
    tasks = []
    for i in range(batch_size):
        task = {
            "name": f"load_test_task_{i}",
            "function_name": "vicky_inference",
            "args": [f"Test prompt {i}", "qwen_7b"],
            "priority": "NORMAL",
            "worker_type": "GENERAL_PURPOSE",
            "category": "load_test"
        }
        tasks.append(task)
    
    batch_request = {
        "tasks": tasks,
        "batch_priority": "NORMAL",
        "execution_mode": "parallel"
    }
    
    start_time = time.time()
    async with session.post(
        "http://localhost:8000/api/high-scale-tasks/batch",
        json=batch_request
    ) as response:
        result = await response.json()
        end_time = time.time()
        
        return {
            "duration": end_time - start_time,
            "submitted": result.get("total_submitted", 0),
            "errors": result.get("total_errors", 0)
        }

async def load_test_main():
    print("🚀 Iniciando prueba de carga VokaFlow...")
    
    total_tasks = 0
    total_time = 0
    errors = 0
    
    async with aiohttp.ClientSession() as session:
        # Enviar 10 lotes de 100 tareas cada uno
        for batch_num in range(10):
            print(f"📦 Enviando lote {batch_num + 1}/10...")
            
            result = await send_task_batch(session, 100)
            
            total_tasks += result["submitted"]
            total_time += result["duration"]
            errors += result["errors"]
            
            print(f"   ✅ {result['submitted']} tareas enviadas en {result['duration']:.2f}s")
            
            # Esperar un poco entre lotes
            await asyncio.sleep(0.1)
    
    # Calcular métricas
    avg_throughput = total_tasks / total_time if total_time > 0 else 0
    
    print(f"\n📊 Resultados de la prueba:")
    print(f"   • Total de tareas: {total_tasks}")
    print(f"   • Tiempo total: {total_time:.2f}s")
    print(f"   • Throughput promedio: {avg_throughput:.0f} tareas/segundo")
    print(f"   • Errores: {errors}")
    
    # Obtener métricas del sistema
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/high-scale-tasks/metrics") as response:
            metrics = await response.json()
            print(f"\n🔍 Métricas del sistema:")
            print(f"   • Throughput actual: {metrics.get('throughput_per_second', 0):.0f} req/s")
            print(f"   • Tareas pendientes: {metrics.get('total_pending_tasks', 0)}")
            print(f"   • Workers activos: {metrics.get('active_workers', 0)}")

if __name__ == "__main__":
    asyncio.run(load_test_main())