#!/bin/bash
echo "🚀 Probando endpoints del dashboard backend..."
echo "============================================"

# Verificar si el servidor está corriendo
echo ""
echo "🔍 Verificando si el backend está disponible..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend disponible en puerto 8000"
else
    echo "❌ Backend NO disponible en puerto 8000"
    echo "   Ejecuta: cd /opt/vokaflow && python src/main.py"
    exit 1
fi

# Función para probar un endpoint
test_endpoint() {
    local endpoint=$1
    local name=$2
    
    echo ""
    echo "🔍 Probando $name: $endpoint"
    echo "----------------------------------------"
    
    response=$(curl -s -w "\nSTATUS_CODE:%{http_code}" "http://localhost:8000$endpoint")
    status_code=$(echo "$response" | tail -n1 | cut -d: -f2)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "200" ]; then
        echo "✅ Status: $status_code"
        echo "📄 Respuesta:"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo "❌ Status: $status_code"
        echo "📄 Error:"
        echo "$body"
    fi
}

# Probar los 3 endpoints específicos
test_endpoint "/api/dashboard/stats" "Dashboard Stats"
test_endpoint "/api/system/health" "System Health"  
test_endpoint "/api/translations/stats" "Translations Stats"

echo ""
echo "🏁 Pruebas completadas"
echo "============================================"
echo "📋 Los endpoints deberían devolver:"
echo "   • /api/dashboard/stats: active_users, total_messages, status, uptime"
echo "   • /api/system/health: cpu_usage, gpu_usage, memory_usage, storage_usage"
echo "   • /api/translations/stats: active, completed, german, spanish, french, japanese" 