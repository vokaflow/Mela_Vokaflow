#!/bin/bash
# Script de monitoreo para VokaFlow

VOKAFLOW_HOME="/opt/vokaflow"
SERVICE_NAME="vokaflow-backend"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_status() {
    local service=$1
    local status=$(systemctl is-active $service 2>/dev/null || echo "inactive")
    
    if [ "$status" = "active" ]; then
        echo -e "${GREEN}✅ $service: $status${NC}"
    else
        echo -e "${RED}❌ $service: $status${NC}"
    fi
}

print_header "ESTADO DE SERVICIOS"
print_status "$SERVICE_NAME"
print_status "nginx"
print_status "redis-server"

print_header "RECURSOS DEL SISTEMA"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "RAM: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "Disco: $(df -h / | awk 'NR==2{print $5}')"

print_header "CONEXIONES DE RED"
echo "Puerto 8000: $(netstat -an | grep :8000 | grep LISTEN | wc -l) listeners"
echo "Puerto 80: $(netstat -an | grep :80 | grep LISTEN | wc -l) listeners"

print_header "LOGS RECIENTES"
echo "Últimas 5 líneas del servicio:"
journalctl -u "$SERVICE_NAME" --no-pager -n 5

print_header "PROCESOS VOKAFLOW"
ps aux | grep -E "(python.*main\.py|vokaflow)" | grep -v grep

print_header "ESPACIO EN DISCO"
echo "Directorio principal:"
du -sh "$VOKAFLOW_HOME" 2>/dev/null || echo "No accesible"
echo "Logs:"
du -sh /var/log/vokaflow 2>/dev/null || echo "No accesible"

print_header "CONECTIVIDAD"
echo "Base de datos: $(timeout 5 python3 -c "
import os
import sys
sys.path.append('$VOKAFLOW_HOME/src')
try:
    from backend.utils.database import test_connection
    if test_connection():
        print('✅ Conectado')
    else:
        print('❌ Error de conexión')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>/dev/null || echo "❌ No se pudo verificar")"

echo "Redis: $(redis-cli ping 2>/dev/null || echo "❌ No responde")"
