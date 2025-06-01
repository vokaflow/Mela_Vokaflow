#!/bin/bash

# VokaFlow Management Script
# Gestión fácil del servicio VokaFlow

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
SERVICE_NAME="vokaflow-backend.service"
API_URL="http://localhost:8000"

# Funciones
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar si el servicio existe
check_service_exists() {
    if ! systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        log_error "Servicio $SERVICE_NAME no está instalado"
        log_info "Ejecuta primero: sudo /tmp/setup-vokaflow-services.sh"
        exit 1
    fi
}

# Mostrar estado
show_status() {
    echo -e "${GREEN}=== ESTADO DE VOKAFLOW ===${NC}"
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "✅ Servicio: ACTIVO"
    else
        log_error "❌ Servicio: INACTIVO"
    fi
    
    if systemctl is-enabled --quiet $SERVICE_NAME; then
        log_success "✅ Autostart: HABILITADO"
    else
        log_warning "⚠️ Autostart: DESHABILITADO"
    fi
    
    # Verificar API
    if curl -s --connect-timeout 5 $API_URL/health > /dev/null 2>&1; then
        log_success "✅ API: RESPONDIENDO"
    else
        log_error "❌ API: NO RESPONDE"
    fi
    
    # Verificar Redis
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_success "✅ Redis: CONECTADO"
    else
        log_error "❌ Redis: DESCONECTADO"
    fi
    
    echo ""
    systemctl status $SERVICE_NAME --no-pager -l
}

# Iniciar servicio
start_service() {
    log_info "Iniciando VokaFlow..."
    sudo systemctl start $SERVICE_NAME
    sleep 5
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "✅ VokaFlow iniciado correctamente"
        log_info "API disponible en: $API_URL"
    else
        log_error "❌ Error al iniciar VokaFlow"
        log_info "Ver logs: journalctl -u $SERVICE_NAME -f"
    fi
}

# Detener servicio
stop_service() {
    log_info "Deteniendo VokaFlow..."
    sudo systemctl stop $SERVICE_NAME
    log_success "✅ VokaFlow detenido"
}

# Reiniciar servicio
restart_service() {
    log_info "Reiniciando VokaFlow..."
    sudo systemctl restart $SERVICE_NAME
    sleep 5
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "✅ VokaFlow reiniciado correctamente"
    else
        log_error "❌ Error al reiniciar VokaFlow"
    fi
}

# Ver logs
show_logs() {
    echo -e "${GREEN}=== LOGS DE VOKAFLOW ===${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para salir${NC}"
    echo ""
    journalctl -u $SERVICE_NAME -f --no-pager
}

# Habilitar autostart
enable_autostart() {
    log_info "Habilitando autostart..."
    sudo systemctl enable $SERVICE_NAME
    log_success "✅ Autostart habilitado"
}

# Deshabilitar autostart
disable_autostart() {
    log_info "Deshabilitando autostart..."
    sudo systemctl disable $SERVICE_NAME
    log_success "✅ Autostart deshabilitado"
}

# Verificar salud
health_check() {
    echo -e "${GREEN}=== VERIFICACIÓN DE SALUD ===${NC}"
    
    # API Health
    if response=$(curl -s --connect-timeout 10 $API_URL/health 2>/dev/null); then
        echo -e "${GREEN}✅ API Health:${NC}"
        echo "$response" | jq . 2>/dev/null || echo "$response"
        echo ""
    else
        log_error "❌ API no responde"
    fi
    
    # High Scale Tasks
    if response=$(curl -s --connect-timeout 10 $API_URL/api/high-scale-tasks/status 2>/dev/null); then
        echo -e "${GREEN}✅ High Scale Tasks:${NC}"
        echo "$response" | jq . 2>/dev/null || echo "$response"
        echo ""
    else
        log_warning "⚠️ High Scale Tasks no disponible"
    fi
    
    # System Resources
    echo -e "${GREEN}💻 Recursos del Sistema:${NC}"
    echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% usado"
    echo "Memoria: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
    echo "Disco: $(df / | tail -1 | awk '{print $5}')"
}

# Mostrar ayuda
show_help() {
    echo -e "${GREEN}🚀 VokaFlow Management Script${NC}"
    echo ""
    echo -e "${BLUE}Uso:${NC} $0 [comando]"
    echo ""
    echo -e "${BLUE}Comandos disponibles:${NC}"
    echo "  status        - Mostrar estado del sistema"
    echo "  start         - Iniciar VokaFlow"
    echo "  stop          - Detener VokaFlow"
    echo "  restart       - Reiniciar VokaFlow"
    echo "  logs          - Ver logs en tiempo real"
    echo "  enable        - Habilitar autostart"
    echo "  disable       - Deshabilitar autostart"
    echo "  health        - Verificación completa de salud"
    echo "  install       - Instalar servicio (requiere sudo)"
    echo "  help          - Mostrar esta ayuda"
    echo ""
    echo -e "${BLUE}Ejemplos:${NC}"
    echo "  $0 status     # Ver estado actual"
    echo "  $0 restart    # Reiniciar el servicio"
    echo "  $0 logs       # Ver logs en tiempo real"
}

# Instalar servicio
install_service() {
    log_info "Instalando servicio VokaFlow..."
    
    if [ ! -f "/tmp/setup-vokaflow-services.sh" ]; then
        log_error "Script de instalación no encontrado en /tmp/setup-vokaflow-services.sh"
        exit 1
    fi
    
    sudo chmod +x /tmp/setup-vokaflow-services.sh
    sudo /tmp/setup-vokaflow-services.sh
}

# Función principal
main() {
    case "${1:-help}" in
        "status"|"s")
            check_service_exists
            show_status
            ;;
        "start")
            check_service_exists
            start_service
            ;;
        "stop")
            check_service_exists
            stop_service
            ;;
        "restart"|"r")
            check_service_exists
            restart_service
            ;;
        "logs"|"l")
            check_service_exists
            show_logs
            ;;
        "enable")
            check_service_exists
            enable_autostart
            ;;
        "disable")
            check_service_exists
            disable_autostart
            ;;
        "health"|"h")
            health_check
            ;;
        "install"|"i")
            install_service
            ;;
        "help"|"--help"|"-h"|*)
            show_help
            ;;
    esac
}

# Ejecutar
main "$@" 