#!/bin/bash
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