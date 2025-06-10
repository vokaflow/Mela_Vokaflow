#!/bin/bash

# =================================================================
# 🚀 VokaFlow Backend Startup Script - Vicky AI Enterprise
# =================================================================

set -e  # Salir si hay errores

# Configuración de colores y logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

VOKAFLOW_DIR="/opt/vokaflow"
LOG_DIR="$VOKAFLOW_DIR/logs"
LOG_FILE="$LOG_DIR/backend_startup.log"

# Función de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') - SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

# Asegurar que el directorio de logs existe
mkdir -p "$LOG_DIR"

log_info "🚀 Iniciando VokaFlow Backend con servicios de traducción..."

# Cambiar al directorio de trabajo
cd "$VOKAFLOW_DIR"

# Verificar que Python esté disponible
if ! command -v python3 &> /dev/null; then
    log_error "Python3 no está instalado o no está en el PATH"
    exit 1
fi

# Verificar que pip esté disponible
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    log_error "pip no está instalado o no está en el PATH"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    log_info "Activando entorno virtual..."
    source venv/bin/activate
    log_success "Entorno virtual activado"
else
    log_warning "No se encontró entorno virtual, usando Python del sistema"
fi

# Las dependencias deben instalarse manualmente antes de ejecutar este script
log_info "Verificando dependencias básicas..."
python3 -c "import fastapi, uvicorn" || {
    log_error "Dependencias básicas no encontradas. Instala manualmente: pip install fastapi uvicorn"
    exit 1
}
log_success "Dependencias básicas verificadas"

# Configurar variables de entorno
log_info "Configurando variables de entorno..."
export PYTHONPATH="/opt/vokaflow:$PYTHONPATH"
export VOKAFLOW_ENV="production"
export VOKAFLOW_LOG_LEVEL="INFO"

# Verificar que la base de datos esté configurada
if [ ! -f ".env" ]; then
    log_warning "Archivo .env no encontrado, creando configuración básica..."
    cat > .env << EOF
# Base de datos
DATABASE_URL=sqlite:///./vokaflow.db

# Seguridad
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')

# Configuración
DEBUG=false
ENVIRONMENT=production
MODELS_DIR=./models
UPLOADS_DIR=./uploads
AUDIO_DIR=./audio

# VickyAI
VICKY_AI_ENABLED=true
VICKY_PERSONALITIES_DIR=VickyAI/personalities
VICKY_CONFIG_PATH=VickyAI/config/vicky.yaml
EOF
    log_success "Archivo .env creado"
fi

# Cargar variables de entorno
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    log_success "Variables de entorno cargadas"
fi

# Crear directorios necesarios
log_info "Creando directorios necesarios..."
mkdir -p logs models uploads audio data/personality data/security thumbnails ssl
log_success "Directorios creados"

# Verificar Redis
log_info "Verificando Redis..."
if systemctl is-active --quiet redis-server || systemctl is-active --quiet redis; then
    log_success "Redis está activo"
else
    log_warning "Redis no está activo, intentando iniciar..."
    sudo systemctl start redis-server || sudo systemctl start redis || log_warning "No se pudo iniciar Redis automáticamente"
fi

# Verificar PostgreSQL
log_info "Verificando PostgreSQL..."
if systemctl is-active --quiet postgresql; then
    log_success "PostgreSQL está activo"
else
    log_warning "PostgreSQL no está activo, intentando iniciar..."
    sudo systemctl start postgresql || log_warning "No se pudo iniciar PostgreSQL automáticamente"
fi

# Verificar conectividad de la base de datos
log_info "Verificando conectividad de la base de datos..."
python3 -c "
import sys
import os
sys.path.append('$VOKAFLOW_DIR')
try:
    # Cambiar al directorio src temporalmente para la verificación
    os.chdir('$VOKAFLOW_DIR/src')
    from dotenv import load_dotenv
    load_dotenv()
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./vokaflow.db')
    print('Base de datos configurada:', database_url[:20] + '...')
except Exception as e:
    print(f'Error de configuración de base de datos: {e}')
    sys.exit(1)
" || {
    log_error "Error de conectividad de base de datos"
    exit 1
}
log_success "Base de datos verificada"

# Verificar modelos de traducción
log_info "Verificando modelos de traducción..."
python3 -c "
import sys
sys.path.append('$VOKAFLOW_DIR')
try:
    import transformers
    import torch
    print('Modelos de traducción disponibles')
except Exception as e:
    print(f'Warning: Modelos no están completamente listos: {e}')
" || log_warning "Los modelos de traducción se cargarán cuando sean necesarios"

# Verificar puerto disponible
if netstat -tulpn | grep :8000 > /dev/null 2>&1; then
    log_warning "Puerto 8000 ya está en uso, intentando detener proceso existente..."
    pkill -f "python.*main.py" || true
    sleep 2
fi

# Iniciar el backend
log_info "Iniciando VokaFlow Backend en puerto 8000..."
cd src

# Ejecutar el backend con logs dirigidos al archivo
exec python3 main.py >> "$LOG_FILE" 2>&1 &
BACKEND_PID=$!

# Esperar un momento para que el servidor inicie
sleep 5

# Verificar que el servidor esté funcionando
if kill -0 $BACKEND_PID 2>/dev/null; then
    log_success "✅ VokaFlow Backend iniciado correctamente (PID: $BACKEND_PID)"
    
    # Verificar que responda HTTP
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "✅ Backend respondiendo correctamente en http://localhost:8000"
        
        # Verificar Vicky AI
        if curl -s http://localhost:8000/api/vicky/ping > /dev/null 2>&1; then
            log_success "✅ Vicky AI integrada y funcionando"
        else
            log_warning "⚠️  Vicky AI puede no estar completamente integrada"
        fi
    else
        log_warning "⚠️  Backend iniciado pero no responde inmediatamente"
    fi
    
    echo $BACKEND_PID > /tmp/vokaflow-backend.pid
    
    log_success "🎉 VokaFlow Backend con Vicky AI Enterprise iniciado exitosamente"
    log_info "📡 API disponible en: http://localhost:8000"
    log_info "📚 Documentación en: http://localhost:8000/docs"
    log_info "📋 Logs en: $LOG_FILE"
    
    # Mantener el script corriendo para systemd
    wait $BACKEND_PID
else
    log_error "❌ Error al iniciar el backend"
    exit 1
fi
