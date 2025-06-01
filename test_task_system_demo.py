#!/usr/bin/env python3
"""
VokaFlow - Demostración del Sistema de Tareas Optimizado
Prueba completa de todas las capacidades del TaskManager
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000/api/tasks"
HEADERS = {"Content-Type": "application/json"}

def print_section(title: str):
    """Imprime una sección con formato"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_result(action: str, result: Dict[str, Any]):
    """Imprime resultado de una acción"""
    print(f"✅ {action}")
    print(f"   {json.dumps(result, indent=2, default=str)}")

def print_error(action: str, error: str):
    """Imprime error de una acción"""
    print(f"❌ {action} - Error: {error}")

def get_stats():
    """Obtiene estadísticas del sistema"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            return response.json()
        else:
            print_error("Obtener estadísticas", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        print_error("Obtener estadísticas", str(e))
        return None

def submit_task(task_data: Dict[str, Any]):
    """Envía una tarea"""
    try:
        response = requests.post(f"{BASE_URL}/submit", json=task_data, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print_error("Enviar tarea", f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error("Enviar tarea", str(e))
        return None

def get_task_details(task_id: str):
    """Obtiene detalles de una tarea"""
    try:
        response = requests.get(f"{BASE_URL}/{task_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print_error("Obtener detalles de tarea", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        print_error("Obtener detalles de tarea", str(e))
        return None

def list_tasks(category: str = None):
    """Lista tareas"""
    try:
        url = f"{BASE_URL}/list"
        if category:
            url += f"?category={category}"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print_error("Listar tareas", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        print_error("Listar tareas", str(e))
        return None

def get_functions():
    """Obtiene funciones disponibles"""
    try:
        response = requests.get(f"{BASE_URL}/functions/list")
        if response.status_code == 200:
            return response.json()
        else:
            print_error("Obtener funciones", f"HTTP {response.status_code}")
            return None
    except Exception as e:
        print_error("Obtener funciones", str(e))
        return None

def submit_batch_tasks(tasks_data: list):
    """Envía tareas en lote"""
    try:
        response = requests.post(f"{BASE_URL}/batch", json=tasks_data, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print_error("Enviar lote de tareas", f"HTTP {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error("Enviar lote de tareas", str(e))
        return None

def main():
    """Función principal de demostración"""
    print("🎯 VokaFlow - Demostración del Sistema de Tareas Optimizado")
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar estado inicial
    print_section("Estado Inicial del Sistema")
    initial_stats = get_stats()
    if initial_stats:
        print_result("Estadísticas iniciales", initial_stats)
    
    # 2. Mostrar funciones disponibles
    print_section("Funciones Disponibles")
    functions = get_functions()
    if functions:
        print_result("Funciones registradas", functions)
    
    # 3. Enviar tareas individuales con diferentes prioridades
    print_section("Enviando Tareas Individuales")
    
    # Tarea CRÍTICA
    critical_task = {
        "name": "sistema_critico",
        "function_name": "vicky_process",
        "args": ["Procesamiento crítico del sistema"],
        "priority": "CRITICAL",
        "category": "vicky",
        "max_retries": 5
    }
    
    critical_result = submit_task(critical_task)
    if critical_result:
        print_result("Tarea CRÍTICA enviada", critical_result)
        critical_task_id = critical_result["task_id"]
    
    # Tarea ALTA prioridad
    high_task = {
        "name": "analisis_audio",
        "function_name": "analyze_audio",
        "args": ["/tmp/audio_sample.wav"],
        "priority": "HIGH",
        "category": "analysis",
        "timeout": 30.0
    }
    
    high_result = submit_task(high_task)
    if high_result:
        print_result("Tarea ALTA prioridad enviada", high_result)
        high_task_id = high_result["task_id"]
    
    # Tarea NORMAL
    normal_task = {
        "name": "generar_reporte",
        "function_name": "generate_report",
        "args": ["mensual"],
        "priority": "NORMAL",
        "category": "report"
    }
    
    normal_result = submit_task(normal_task)
    if normal_result:
        print_result("Tarea NORMAL enviada", normal_result)
        normal_task_id = normal_result["task_id"]
    
    # Tarea BAJA prioridad
    low_task = {
        "name": "backup_automatico",
        "function_name": "backup_data",
        "args": ["/opt/vokaflow/backup"],
        "priority": "LOW",
        "category": "backup",
        "delay": 2.0  # Retrasar 2 segundos
    }
    
    low_result = submit_task(low_task)
    if low_result:
        print_result("Tarea BAJA prioridad enviada (con delay)", low_result)
        low_task_id = low_result["task_id"]
    
    # 4. Enviar lote de tareas
    print_section("Enviando Lote de Tareas")
    
    batch_tasks = [
        {
            "name": "notificacion_1",
            "function_name": "send_notification",
            "args": ["usuario1", "Mensaje de prueba 1"],
            "priority": "NORMAL",
            "category": "notification"
        },
        {
            "name": "notificacion_2",
            "function_name": "send_notification",
            "args": ["usuario2", "Mensaje de prueba 2"],
            "priority": "NORMAL",
            "category": "notification"
        },
        {
            "name": "limpieza_temp",
            "function_name": "cleanup_temp",
            "priority": "LOW",
            "category": "cleanup"
        },
        {
            "name": "optimizar_modelos",
            "function_name": "optimize_models",
            "priority": "HIGH",
            "category": "optimization"
        }
    ]
    
    batch_result = submit_batch_tasks(batch_tasks)
    if batch_result:
        print_result("Lote de tareas enviado", batch_result)
    
    # 5. Esperar procesamiento
    print_section("Esperando Procesamiento")
    print("⏳ Esperando 5 segundos para que se procesen las tareas...")
    time.sleep(5)
    
    # 6. Verificar estadísticas después del procesamiento
    print_section("Estadísticas Después del Procesamiento")
    final_stats = get_stats()
    if final_stats:
        print_result("Estadísticas finales", final_stats)
    
    # 7. Verificar detalles de tareas específicas
    print_section("Detalles de Tareas Específicas")
    
    if 'critical_task_id' in locals():
        critical_details = get_task_details(critical_task_id)
        if critical_details:
            print_result(f"Detalles tarea crítica ({critical_task_id[:8]})", critical_details)
    
    if 'high_task_id' in locals():
        high_details = get_task_details(high_task_id)
        if high_details:
            print_result(f"Detalles tarea alta prioridad ({high_task_id[:8]})", high_details)
    
    # 8. Listar tareas por categoría
    print_section("Listado de Tareas por Categoría")
    
    categories = ["vicky", "analysis", "backup", "notification", "cleanup"]
    
    for category in categories:
        category_tasks = list_tasks(category)
        if category_tasks and category_tasks["tasks"]:
            print_result(f"Tareas en categoría '{category}'", {
                "count": len(category_tasks["tasks"]),
                "tasks": [
                    {
                        "name": task["name"],
                        "status": task["status"],
                        "execution_time": task["execution_time"]
                    }
                    for task in category_tasks["tasks"]
                ]
            })
    
    # 9. Resumen final
    print_section("Resumen Final")
    
    if initial_stats and final_stats:
        summary = {
            "tareas_procesadas": final_stats["total_tasks"] - initial_stats["total_tasks"],
            "tareas_completadas": final_stats["completed_tasks"] - initial_stats["completed_tasks"],
            "tareas_fallidas": final_stats["failed_tasks"] - initial_stats["failed_tasks"],
            "workers_activos": final_stats["workers_count"],
            "sistema_funcionando": final_stats["running"]
        }
        
        print_result("Resumen de la demostración", summary)
        
        if summary["tareas_procesadas"] > 0:
            print(f"\n🎉 ¡Demostración exitosa!")
            print(f"   • Se procesaron {summary['tareas_procesadas']} tareas")
            print(f"   • {summary['tareas_completadas']} completadas exitosamente")
            print(f"   • {summary['tareas_fallidas']} fallaron")
            print(f"   • Sistema funcionando con {summary['workers_activos']} workers")
        else:
            print(f"\n⚠️  No se procesaron tareas nuevas durante la demostración")
    
    print(f"\n✨ Demostración completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demostración interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        sys.exit(1) 