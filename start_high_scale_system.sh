#!/bin/bash
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
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --backlog 4096 \
    --limit-max-requests 100000 \
    --limit-concurrency 10000 \
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