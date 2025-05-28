#!/bin/bash
# Script para actualizar el backend de VokaFlow

set -e

VOKAFLOW_HOME="/opt/vokaflow"
SERVICE_NAME="vokaflow-backend"

echo "🔄 === ACTUALIZANDO VOKAFLOW BACKEND ==="
echo "$(date)"

# Verificar que el servicio existe
if ! systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    echo "❌ Servicio $SERVICE_NAME no encontrado. Ejecutar setup-production.sh primero."
    exit 1
fi

# Hacer backup del código actual
echo "📦 Creando backup..."
sudo -u vokaflow cp -r "$VOKAFLOW_HOME/src" "$VOKAFLOW_HOME/backups/src-$(date +%Y%m%d-%H%M%S)"

# Detener servicio
echo "⏹️ Deteniendo servicio..."
systemctl stop "$SERVICE_NAME"

# Actualizar código
echo "📥 Actualizando código..."
if [ -d "./src" ]; then
    cp -r ./src/* "$VOKAFLOW_HOME"/src/
    cp -r ./python-backend/* "$VOKAFLOW_HOME"/src/ 2>/dev/null || true
    chown -R vokaflow:vokaflow "$VOKAFLOW_HOME"/src
else
    echo "❌ Directorio src no encontrado"
    exit 1
fi

# Actualizar dependencias si es necesario
if [ -f "requirements.txt" ] || [ -f "./python-backend/requirements.txt" ]; then
    echo "📦 Actualizando dependencias..."
    cp requirements.txt "$VOKAFLOW_HOME"/ 2>/dev/null || true
    cp ./python-backend/requirements.txt "$VOKAFLOW_HOME"/requirements.txt 2>/dev/null || true
    sudo -u vokaflow "$VOKAFLOW_HOME"/venv/bin/pip install -r "$VOKAFLOW_HOME"/requirements.txt
fi

# Reiniciar servicio
echo "▶️ Iniciando servicio..."
systemctl start "$SERVICE_NAME"

# Verificar estado
sleep 5
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✅ Actualización completada exitosamente"
    echo "📊 Estado del servicio:"
    systemctl status "$SERVICE_NAME" --no-pager -l
else
    echo "❌ Error al iniciar el servicio"
    echo "📋 Logs recientes:"
    journalctl -u "$SERVICE_NAME" --no-pager -n 20
    exit 1
fi
