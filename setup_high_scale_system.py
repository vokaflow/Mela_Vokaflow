#!/usr/bin/env python3
"""
VokaFlow - Configuración del Sistema de Alta Escala
Script para configurar Redis Cluster y optimizaciones para millones de req/s
"""

import os
import sys
import subprocess
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HighScaleSystemSetup:
    """
    Configurador del sistema de alta escala
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.redis_cluster_nodes = [
            {"port": 7000, "dir": "redis-cluster/7000"},
            {"port": 7001, "dir": "redis-cluster/7001"},
            {"port": 7002, "dir": "redis-cluster/7002"},
            {"port": 7003, "dir": "redis-cluster/7003"},
            {"port": 7004, "dir": "redis-cluster/7004"},
            {"port": 7005, "dir": "redis-cluster/7005"}
        ]
        self.redis_cluster_dir = self.project_root / "redis-cluster"
        
    def setup_complete_system(self):
        """Configurar el sistema completo de alta escala"""
        logger.info("🚀 Configurando sistema VokaFlow de alta escala...")
        
        try:
            # 1. Verificar dependencias
            self._check_dependencies()
            
            # 2. Configurar Redis Cluster
            self._setup_redis_cluster()
            
            # 3. Configurar optimizaciones del sistema
            self._setup_system_optimizations()
            
            # 4. Crear archivos de configuración
            self._create_config_files()
            
            # 5. Crear scripts de deployment
            self._create_deployment_scripts()
            
            # 6. Configurar monitoreo
            self._setup_monitoring()
            
            logger.info("✅ Sistema de alta escala configurado correctamente")
            self._print_usage_instructions()
            
        except Exception as e:
            logger.error(f"❌ Error configurando sistema: {e}")
            raise

    def _check_dependencies(self):
        """Verificar dependencias del sistema"""
        logger.info("🔍 Verificando dependencias...")
        
        dependencies = {
            "redis-server": "Redis Server",
            "redis-cli": "Redis CLI",
            "python3": "Python 3",
            "pip": "Python Package Manager"
        }
        
        missing = []
        for cmd, desc in dependencies.items():
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    logger.info(f"✅ {desc} disponible")
                else:
                    missing.append(desc)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(desc)
        
        if missing:
            logger.error(f"❌ Dependencias faltantes: {', '.join(missing)}")
            logger.info("💡 Instalar con: sudo apt-get install redis-server python3-pip")
            sys.exit(1)

    def _setup_redis_cluster(self):
        """Configurar Redis Cluster para alta escala"""
        logger.info("⚙️ Configurando Redis Cluster...")
        
        # Crear directorio del cluster
        self.redis_cluster_dir.mkdir(exist_ok=True)
        
        # Crear configuraciones para cada nodo
        for node in self.redis_cluster_nodes:
            node_dir = self.redis_cluster_dir / node["dir"]
            node_dir.mkdir(parents=True, exist_ok=True)
            
            # Configuración Redis optimizada para alta escala
            redis_config = f"""
# Redis configuración para alta escala - Puerto {node['port']}
port {node['port']}
cluster-enabled yes
cluster-config-file nodes-{node['port']}.conf
cluster-node-timeout 15000
appendonly yes
appendfsync everysec

# Optimizaciones para alta escala
maxmemory 1gb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 300
tcp-backlog 2048

# Configuraciones de rendimiento
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error no
rdbcompression yes
rdbchecksum yes

# Configuraciones de red
bind 127.0.0.1
protected-mode no
databases 16

# Configuraciones de cliente
maxclients 10000
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60

# Configuraciones avanzadas
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
"""
            
            config_path = node_dir / "redis.conf"
            with open(config_path, "w") as f:
                f.write(redis_config.strip())
            
            logger.info(f"✅ Configuración creada para nodo {node['port']}")
        
        # Crear script de inicio del cluster
        cluster_start_script = f"""#!/bin/bash
# Script de inicio de Redis Cluster para VokaFlow

echo "🚀 Iniciando Redis Cluster para VokaFlow..."

# Iniciar nodos Redis
{' & '.join([f"redis-server {self.redis_cluster_dir}/{node['dir']}/redis.conf" for node in self.redis_cluster_nodes])} &

# Esperar a que los nodos se inicien
echo "⏳ Esperando inicio de nodos..."
sleep 5

# Crear cluster
echo "🔗 Creando cluster Redis..."
redis-cli --cluster create \\
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \\
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \\
  --cluster-replicas 1 --cluster-yes

echo "✅ Redis Cluster iniciado correctamente"
echo "💡 Verificar con: redis-cli -c -p 7000 cluster nodes"
"""
        
        start_script_path = self.redis_cluster_dir / "start_cluster.sh"
        with open(start_script_path, "w") as f:
            f.write(cluster_start_script.strip())
        
        os.chmod(start_script_path, 0o755)
        
        # Crear script de parada del cluster
        cluster_stop_script = """#!/bin/bash
# Script de parada de Redis Cluster

echo "🛑 Deteniendo Redis Cluster..."

# Detener procesos Redis
pkill -f redis-server
sleep 2

echo "✅ Redis Cluster detenido"
"""
        
        stop_script_path = self.redis_cluster_dir / "stop_cluster.sh"
        with open(stop_script_path, "w") as f:
            f.write(cluster_stop_script.strip())
        
        os.chmod(stop_script_path, 0o755)

    def _setup_system_optimizations(self):
        """Configurar optimizaciones del sistema operativo"""
        logger.info("⚡ Configurando optimizaciones del sistema...")
        
        # Configuraciones de kernel recomendadas
        sysctl_config = """
# Optimizaciones VokaFlow para alta escala

# Red
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_congestion_control = bbr

# Memoria
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# Sistema de archivos
fs.file-max = 1000000
fs.nr_open = 1000000

# Procesos
kernel.pid_max = 4194304
"""
        
        sysctl_path = self.project_root / "configs" / "99-vokaflow-optimizations.conf"
        sysctl_path.parent.mkdir(exist_ok=True)
        
        with open(sysctl_path, "w") as f:
            f.write(sysctl_config.strip())
        
        # Configuraciones de límites
        limits_config = """
# Límites para VokaFlow alta escala
* soft nofile 1000000
* hard nofile 1000000
* soft nproc 1000000
* hard nproc 1000000
root soft nofile 1000000
root hard nofile 1000000
"""
        
        limits_path = self.project_root / "configs" / "vokaflow-limits.conf"
        with open(limits_path, "w") as f:
            f.write(limits_config.strip())
        
        logger.info("✅ Configuraciones de optimización creadas")
        logger.info("💡 Aplicar con: sudo cp configs/99-vokaflow-optimizations.conf /etc/sysctl.d/")
        logger.info("💡 Aplicar límites: sudo cp configs/vokaflow-limits.conf /etc/security/limits.d/")

    def _create_config_files(self):
        """Crear archivos de configuración para el sistema"""
        logger.info("📝 Creando archivos de configuración...")
        
        # Configuración principal del sistema de alta escala
        high_scale_config = {
            "redis_cluster": {
                "nodes": [f"redis://127.0.0.1:{node['port']}" for node in self.redis_cluster_nodes],
                "max_connections_per_node": 100,
                "retry_on_timeout": True,
                "health_check_interval": 30
            },
            "worker_pools": {
                "cpu_intensive": {
                    "max_workers": "auto",  # Will be set to CPU count
                    "pool_type": "ProcessPool"
                },
                "io_intensive": {
                    "max_workers": "auto * 2",
                    "pool_type": "ThreadPool"
                },
                "memory_intensive": {
                    "max_workers": "auto / 2",
                    "pool_type": "ThreadPool"
                },
                "network_intensive": {
                    "max_workers": "auto * 4",
                    "pool_type": "ThreadPool"
                },
                "general_purpose": {
                    "max_workers": "auto",
                    "pool_type": "ThreadPool"
                }
            },
            "rate_limiting": {
                "vicky": 50000,
                "audio": 20000,
                "database": 100000,
                "notifications": 1000000,
                "analytics": 30000,
                "ml": 10000,
                "system": 5000,
                "general": 10000
            },
            "auto_scaling": {
                "enabled": True,
                "scale_up_threshold": 1000,
                "scale_down_threshold": 100,
                "cpu_threshold_up": 80,
                "cpu_threshold_down": 30,
                "evaluation_interval": 30
            },
            "monitoring": {
                "enabled": True,
                "metrics_interval": 1,
                "log_interval": 10
            },
            "partitioning": {
                "partition_count": 16,
                "hash_algorithm": "md5"
            }
        }
        
        config_path = self.project_root / "configs" / "high_scale_config.json"
        with open(config_path, "w") as f:
            json.dump(high_scale_config, f, indent=2)
        
        # Configuración de prioridades detallada
        priorities_config = {
            "EMERGENCY": {
                "value": 0,
                "sla_ms": 100,
                "timeout_s": 5,
                "max_retries": 1,
                "use_cases": ["system_failures", "security_alerts", "disaster_recovery"]
            },
            "CRITICAL": {
                "value": 1,
                "sla_ms": 500,
                "timeout_s": 30,
                "max_retries": 3,
                "use_cases": ["vicky_ai", "financial_transactions", "realtime_communication"]
            },
            "HIGH": {
                "value": 2,
                "sla_ms": 2000,
                "timeout_s": 60,
                "max_retries": 3,
                "use_cases": ["audio_analysis", "push_notifications", "interactive_queries"]
            },
            "NORMAL": {
                "value": 3,
                "sla_ms": 10000,
                "timeout_s": 300,
                "max_retries": 3,
                "use_cases": ["file_processing", "reports", "crud_operations"]
            },
            "LOW": {
                "value": 4,
                "sla_ms": 60000,
                "timeout_s": 600,
                "max_retries": 2,
                "use_cases": ["analytics", "aggregations", "synchronization"]
            },
            "BATCH": {
                "value": 5,
                "sla_ms": 300000,
                "timeout_s": 3600,
                "max_retries": 1,
                "use_cases": ["ml_training", "bulk_processing", "etl"]
            },
            "BACKGROUND": {
                "value": 6,
                "sla_ms": 1800000,
                "timeout_s": 7200,
                "max_retries": 1,
                "use_cases": ["cleanup", "optimization", "indexing"]
            },
            "MAINTENANCE": {
                "value": 7,
                "sla_ms": 7200000,
                "timeout_s": 14400,
                "max_retries": 1,
                "use_cases": ["backups", "health_checks", "log_rotation"]
            }
        }
        
        priorities_path = self.project_root / "configs" / "priorities_config.json"
        with open(priorities_path, "w") as f:
            json.dump(priorities_config, f, indent=2)
        
        logger.info("✅ Archivos de configuración creados")

    def _create_deployment_scripts(self):
        """Crear scripts de deployment optimizados"""
        logger.info("🚢 Creando scripts de deployment...")
        
        # Script de inicio del sistema completo
        startup_script = """#!/bin/bash
# VokaFlow High Scale System Startup

echo "🚀 Iniciando sistema VokaFlow de alta escala..."

# Verificar dependencias
echo "🔍 Verificando dependencias..."
command -v redis-server >/dev/null 2>&1 || { echo "❌ Redis no instalado"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 no instalado"; exit 1; }

# Configurar límites del sistema
echo "⚙️ Configurando límites del sistema..."
ulimit -n 1000000
ulimit -u 1000000

# Iniciar Redis Cluster
echo "🔗 Iniciando Redis Cluster..."
cd redis-cluster
./start_cluster.sh
cd ..

# Esperar a que Redis esté listo
echo "⏳ Esperando Redis Cluster..."
sleep 10

# Verificar Redis Cluster
echo "🔍 Verificando Redis Cluster..."
redis-cli -c -p 7000 ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis Cluster operativo"
else
    echo "❌ Error en Redis Cluster"
    exit 1
fi

# Iniciar VokaFlow Backend
echo "🚀 Iniciando VokaFlow Backend..."
export PYTHONPATH=$PWD:$PYTHONPATH
export VOKAFLOW_HIGH_SCALE=true
export VOKAFLOW_REDIS_CLUSTER=true

# Usar múltiples workers Uvicorn para alta escala
uvicorn main:app \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --backlog 4096 \\
    --limit-max-requests 100000 \\
    --limit-concurrency 10000 \\
    --timeout-keep-alive 30 &

BACKEND_PID=$!
echo "✅ VokaFlow Backend iniciado (PID: $BACKEND_PID)"

# Esperar a que el backend esté listo
echo "⏳ Esperando backend..."
sleep 10

# Verificar backend
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ VokaFlow Backend operativo"
    echo "🎉 Sistema de alta escala iniciado correctamente"
    echo "📊 Métricas: http://localhost:8000/api/high-scale-tasks/metrics"
    echo "📚 Documentación: http://localhost:8000/docs"
else
    echo "❌ Error en VokaFlow Backend"
    kill $BACKEND_PID
    exit 1
fi

# Mantener el script corriendo
wait $BACKEND_PID
"""
        
        startup_path = self.project_root / "start_high_scale_system.sh"
        with open(startup_path, "w") as f:
            f.write(startup_script.strip())
        
        os.chmod(startup_path, 0o755)
        
        # Script de parada del sistema
        shutdown_script = """#!/bin/bash
# VokaFlow High Scale System Shutdown

echo "🛑 Deteniendo sistema VokaFlow de alta escala..."

# Detener backend
echo "🔄 Deteniendo VokaFlow Backend..."
pkill -f uvicorn
sleep 5

# Detener Redis Cluster
echo "🔄 Deteniendo Redis Cluster..."
cd redis-cluster
./stop_cluster.sh
cd ..

echo "✅ Sistema de alta escala detenido"
"""
        
        shutdown_path = self.project_root / "stop_high_scale_system.sh"
        with open(shutdown_path, "w") as f:
            f.write(shutdown_script.strip())
        
        os.chmod(shutdown_path, 0o755)
        
        # Script de pruebas de carga
        load_test_script = """#!/usr/bin/env python3
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
    
    print(f"\\n📊 Resultados de la prueba:")
    print(f"   • Total de tareas: {total_tasks}")
    print(f"   • Tiempo total: {total_time:.2f}s")
    print(f"   • Throughput promedio: {avg_throughput:.0f} tareas/segundo")
    print(f"   • Errores: {errors}")
    
    # Obtener métricas del sistema
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/high-scale-tasks/metrics") as response:
            metrics = await response.json()
            print(f"\\n🔍 Métricas del sistema:")
            print(f"   • Throughput actual: {metrics.get('throughput_per_second', 0):.0f} req/s")
            print(f"   • Tareas pendientes: {metrics.get('total_pending_tasks', 0)}")
            print(f"   • Workers activos: {metrics.get('active_workers', 0)}")

if __name__ == "__main__":
    asyncio.run(load_test_main())
"""
        
        load_test_path = self.project_root / "load_test.py"
        with open(load_test_path, "w") as f:
            f.write(load_test_script.strip())
        
        os.chmod(load_test_path, 0o755)

    def _setup_monitoring(self):
        """Configurar monitoreo del sistema"""
        logger.info("📊 Configurando monitoreo...")
        
        # Script de monitoreo en tiempo real
        monitoring_script = """#!/usr/bin/env python3
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
                        print("\\033[H\\033[J", end="")
                        
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
                        print(f"\\n💻 Recursos del Sistema:")
                        print(f"   CPU: {resources.get('cpu_percent', 0):.1f}%")
                        print(f"   Memoria: {resources.get('memory_percent', 0):.1f}%")
                        print(f"   Disco: {resources.get('disk_usage', 0):.1f}%")
                        
                        # Distribución de colas
                        queue_dist = metrics.get('queue_distribution', {})
                        if queue_dist:
                            print(f"\\n📊 Distribución de Colas:")
                            for priority, count in queue_dist.items():
                                print(f"   {priority}: {count}")
                        
                        # Workers pools
                        worker_pools = metrics.get('worker_pools', {})
                        if worker_pools:
                            print(f"\\n👷 Pools de Workers:")
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
        print("\\n🛑 Monitoreo detenido")
        sys.exit(0)
"""
        
        monitoring_path = self.project_root / "monitor_system.py"
        with open(monitoring_path, "w") as f:
            f.write(monitoring_script.strip())
        
        os.chmod(monitoring_path, 0o755)

    def _print_usage_instructions(self):
        """Imprimir instrucciones de uso"""
        print("\n" + "="*60)
        print("🎉 VokaFlow Sistema de Alta Escala - Configuración Completa")
        print("="*60)
        print("\n📋 Comandos disponibles:")
        print("   • Iniciar sistema:     ./start_high_scale_system.sh")
        print("   • Detener sistema:     ./stop_high_scale_system.sh")
        print("   • Monitorear sistema:  ./monitor_system.py")
        print("   • Prueba de carga:     ./load_test.py")
        print("\n🔧 Configuraciones manuales recomendadas:")
        print("   • sudo cp configs/99-vokaflow-optimizations.conf /etc/sysctl.d/")
        print("   • sudo cp configs/vokaflow-limits.conf /etc/security/limits.d/")
        print("   • sudo sysctl -p")
        print("\n📊 Endpoints del sistema:")
        print("   • API Principal:       http://localhost:8000/docs")
        print("   • Tareas Alta Escala:  http://localhost:8000/api/high-scale-tasks/")
        print("   • Métricas:            http://localhost:8000/api/high-scale-tasks/metrics")
        print("   • Configuración:       http://localhost:8000/api/high-scale-tasks/priorities")
        print("\n🎯 Capacidades del sistema:")
        print("   • ⚡ Millones de solicitudes por segundo")
        print("   • 🔗 Redis Cluster distribuido (6 nodos)")
        print("   • 👷 Workers especializados por tipo de tarea")
        print("   • 📈 Auto-scaling automático")
        print("   • 🛡️ Rate limiting avanzado")
        print("   • 🔄 Circuit breakers")
        print("   • 📊 Monitoreo en tiempo real")
        print("   • 🎚️ 8 niveles de prioridad")
        print("   • 🧩 16 particiones para distribución")
        print("\n💡 Para optimización máxima, reinicia el sistema después de aplicar las configuraciones.")

def main():
    """Función principal"""
    setup = HighScaleSystemSetup()
    setup.setup_complete_system()

if __name__ == "__main__":
    main() 