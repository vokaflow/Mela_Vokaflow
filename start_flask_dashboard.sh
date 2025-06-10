#!/bin/bash

# =================================================================
# 🎭 VokaFlow Flask Dashboard Startup Script
# =================================================================

set -e  # Salir si hay errores

# Configuración de colores y logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VOKAFLOW_DIR="/opt/vokaflow"
LOG_DIR="$VOKAFLOW_DIR/logs"
LOG_FILE="$LOG_DIR/flask_dashboard.log"

# Función de logging
log_info() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

# Asegurar que el directorio de logs existe
mkdir -p "$LOG_DIR"

log_info "🎭 Iniciando VokaFlow Flask Dashboard..."

# Cambiar al directorio de trabajo
cd "$VOKAFLOW_DIR/flask_vokaflow"

# Activar entorno virtual si existe
if [ -d "../venv" ]; then
    log_info "Activando entorno virtual..."
    source ../venv/bin/activate
    log_success "Entorno virtual activado"
else
    log_error "No se encontró entorno virtual"
    exit 1
fi

# Verificar dependencias de Flask
log_info "Verificando dependencias de Flask..."
python3 -c "import flask" || {
    log_error "Flask no está instalado. Instala con: pip install flask"
    exit 1
}
log_success "Flask disponible"

# Configurar variables de entorno
export PYTHONPATH="/opt/vokaflow:$PYTHONPATH"
export FLASK_ENV="production"
export FLASK_DEBUG="false"
export BACKEND_URL="http://localhost:8000"

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    log_info "Creando archivo .env para Flask..."
    cat > .env << EOF
# Backend VokaFlow
BACKEND_URL=http://localhost:8000

# Flask Configuration
FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
FLASK_ENV=production
FLASK_DEBUG=false

# Audio Configuration
AUDIO_UPLOAD_FOLDER=static/audio
MAX_AUDIO_SIZE=26214400

# AI Configuration (opcional)
AI_PROVIDER=openai
AI_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HUGGINGFACE_API_KEY=
EOF
    log_success "Archivo .env creado"
fi

# Verificar puerto disponible
if netstat -tulpn | grep :5000 > /dev/null 2>&1; then
    log_info "Puerto 5000 ya está en uso, intentando detener proceso existente..."
    pkill -f "python.*app.py" || true
    sleep 2
fi

# Iniciar Flask Dashboard
log_info "Iniciando Flask Dashboard en puerto 5000..."

# Ejecutar la aplicación Flask
exec python3 app.py >> "$LOG_FILE" 2>&1 &
FLASK_PID=$!

# Esperar un momento para que el servidor inicie
sleep 3

# Verificar que el servidor esté funcionando
if kill -0 $FLASK_PID 2>/dev/null; then
    log_success "✅ Flask Dashboard iniciado correctamente (PID: $FLASK_PID)"
    
    # Verificar que responda HTTP
    if curl -s -f http://localhost:5000 > /dev/null 2>&1; then
        log_success "✅ Dashboard respondiendo correctamente en http://localhost:5000"
    else
        log_info "⚠️ Dashboard iniciado pero no responde inmediatamente"
    fi
    
    echo $FLASK_PID > /tmp/vokaflow-flask.pid
    
    log_success "🎉 VokaFlow Flask Dashboard iniciado exitosamente"
    log_info "🎭 Dashboard disponible en: http://localhost:5000"
    log_info "📋 Logs en: $LOG_FILE"
    
    # Mantener el script corriendo para systemd
    wait $FLASK_PID
else
    log_error "❌ Error al iniciar Flask Dashboard"
    exit 1
fi
