#!/usr/bin/env python3
import asyncio
import redis.asyncio as aioredis
import psutil
import json
import time
from datetime import datetime
from pathlib import Path

class ProductionMonitor:
    def __init__(self):
        self.redis_ports = [7000, 7001, 7002, 7003, 7004, 7005]
        self.metrics_dir = Path("metrics/real-time")
        self.alerts_dir = Path("monitoring/alerts")
        
    async def monitor_system(self):
        while True:
            try:
                metrics = await self.collect_metrics()
                await self.save_metrics(metrics)
                await self.check_alerts(metrics)
                await asyncio.sleep(10)  # Cada 10 segundos
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                await asyncio.sleep(30)
    
    async def collect_metrics(self):
        timestamp = datetime.now().isoformat()
        
        # Métricas del sistema
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "disk": dict(psutil.disk_usage('/')._asdict()),
            "network": dict(psutil.net_io_counters()._asdict()),
            "load_avg": psutil.getloadavg()
        }
        
        # Métricas de Redis Cluster
        redis_metrics = {}
        for port in self.redis_ports:
            try:
                redis_client = aioredis.from_url(f"redis://localhost:{port}")
                info = await redis_client.info()
                redis_metrics[f"redis_{port}"] = {
                    "used_memory": info.get("used_memory", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
                await redis_client.close()
            except Exception as e:
                redis_metrics[f"redis_{port}"] = {"error": str(e)}
        
        return {
            "timestamp": timestamp,
            "system": system_metrics,
            "redis_cluster": redis_metrics
        }
    
    async def save_metrics(self, metrics):
        # Guardar métricas en archivo JSON
        filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H')}.json"
        file_path = self.metrics_dir / filename
        
        # Cargar métricas existentes o crear nuevo archivo
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"metrics": []}
        
        data["metrics"].append(metrics)
        
        # Mantener solo las últimas 360 entradas (1 hora con intervalos de 10s)
        if len(data["metrics"]) > 360:
            data["metrics"] = data["metrics"][-360:]
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def check_alerts(self, metrics):
        # Verificar thresholds y generar alertas
        alerts = []
        
        if metrics["system"]["cpu_percent"] > 80:
            alerts.append({"type": "cpu_high", "value": metrics["system"]["cpu_percent"]})
        
        if metrics["system"]["memory"]["percent"] > 85:
            alerts.append({"type": "memory_high", "value": metrics["system"]["memory"]["percent"]})
        
        # Verificar Redis
        for node, data in metrics["redis_cluster"].items():
            if "error" in data:
                alerts.append({"type": "redis_node_down", "node": node, "error": data["error"]})
        
        if alerts:
            alert_file = self.alerts_dir / f"alert_{int(time.time())}.json"
            with open(alert_file, 'w') as f:
                json.dump({"timestamp": metrics["timestamp"], "alerts": alerts}, f, indent=2)

if __name__ == "__main__":
    monitor = ProductionMonitor()
    asyncio.run(monitor.monitor_system())
