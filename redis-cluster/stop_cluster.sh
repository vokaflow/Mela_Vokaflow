#!/bin/bash
# Script de parada de Redis Cluster

echo "🛑 Deteniendo Redis Cluster..."

# Detener procesos Redis
pkill -f redis-server
sleep 2

echo "✅ Redis Cluster detenido"