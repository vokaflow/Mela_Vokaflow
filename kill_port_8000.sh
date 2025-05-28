#!/bin/bash
echo "Buscando procesos que usan el puerto 8000..."
pid=$(sudo lsof -t -i:8000 2>/dev/null)

if [ -z "$pid" ]; then
    echo "No se encontró ningún proceso usando el puerto 8000."
else
    echo "Matando procesos en el puerto 8000 (PID: $pid)..."
    sudo kill -9 $pid
    echo "Puerto 8000 liberado."
fi

# Esperar un momento para asegurarse de que el puerto está libre
sleep 2
echo "Verificando que el puerto 8000 está libre..."
if sudo lsof -i:8000 >/dev/null 2>&1; then
    echo "ERROR: El puerto 8000 todavía está en uso."
else
    echo "Puerto 8000 está libre y listo para usar."
fi 