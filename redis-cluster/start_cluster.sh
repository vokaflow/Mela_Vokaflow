#!/bin/bash
# Script de inicio de Redis Cluster para VokaFlow

echo "🚀 Iniciando Redis Cluster para VokaFlow..."

# Iniciar nodos Redis
redis-server /opt/vokaflow/redis-cluster/redis-cluster/7000/redis.conf & redis-server /opt/vokaflow/redis-cluster/redis-cluster/7001/redis.conf & redis-server /opt/vokaflow/redis-cluster/redis-cluster/7002/redis.conf & redis-server /opt/vokaflow/redis-cluster/redis-cluster/7003/redis.conf & redis-server /opt/vokaflow/redis-cluster/redis-cluster/7004/redis.conf & redis-server /opt/vokaflow/redis-cluster/redis-cluster/7005/redis.conf &

# Esperar a que los nodos se inicien
echo "⏳ Esperando inicio de nodos..."
sleep 5

# Crear cluster
echo "🔗 Creando cluster Redis..."
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1 --cluster-yes

echo "✅ Redis Cluster iniciado correctamente"
echo "💡 Verificar con: redis-cli -c -p 7000 cluster nodes"