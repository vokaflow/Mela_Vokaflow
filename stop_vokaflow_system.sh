#!/bin/bash

# =================================================================
# 🛑 VokaFlow System Stop Script
# =================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

LOG_DIR="/opt/vokaflow/logs"
LOG_FILE="$LOG_DIR/system_stop.log"

# Función de logging
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

mkdir -p "$LOG_DIR"

log_info "🛑 Deteniendo VokaFlow System..."

# Detener proceso del backend si existe
if [ -f "/tmp/vokaflow-backend.pid" ]; then
    BACKEND_PID=$(cat /tmp/vokaflow-backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        log_info "Deteniendo backend (PID: $BACKEND_PID)..."
        kill -TERM $BACKEND_PID
        sleep 5
        
        # Si aún está corriendo, forzar
        if kill -0 $BACKEND_PID 2>/dev/null; then
            log_warning "Forzando detención del backend..."
            kill -KILL $BACKEND_PID
        fi
        
        log_success "Backend detenido"
    else
        log_warning "PID del backend no encontrado o ya detenido"
    fi
    rm -f /tmp/vokaflow-backend.pid
fi

# Detener cualquier proceso de Python relacionado con VokaFlow
log_info "Buscando procesos Python de VokaFlow..."
pkill -f "python.*main.py" || log_info "No se encontraron procesos adicionales"
pkill -f "uvicorn" || log_info "No se encontraron procesos uvicorn"

log_success "✅ VokaFlow System detenido correctamente"

exit 0
