#!/bin/bash
# Script para reiniciar el backend en el puerto 8000

echo "Buscando el proceso actual del backend..."
PID=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
    echo "Deteniendo el proceso del backend (PID: $PID)..."
    kill $PID
    sleep 2
    
    # Verificar si el proceso sigue en ejecución
    if ps -p $PID > /dev/null; then
        echo "Forzando la detención del proceso..."
        kill -9 $PID
    fi
    
    echo "Proceso anterior detenido."
else
    echo "No se encontró ningún proceso del backend en ejecución."
fi

echo "Iniciando el backend en el puerto 8000..."
cd /opt/vokaflow
source deploy/start-backend.sh &

echo "Esperando a que el servidor inicie..."
sleep 3

# Verificar si el servidor está escuchando en el puerto 8000
if netstat -tuln | grep ":8000" > /dev/null; then
    echo "✅ El backend se ha iniciado correctamente en el puerto 8000."
else
    echo "❌ Hubo un problema al iniciar el backend en el puerto 8000."
    echo "Revisar los logs para más información."
fi 