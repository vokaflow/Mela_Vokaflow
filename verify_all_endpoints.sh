#!/bin/bash
echo "🔍 VERIFICACIÓN COMPLETA DE ENDPOINTS VOKAFLOW API"
echo "=================================================="
echo

# Función para contar endpoints por router
count_endpoints() {
    local file=$1
    local name=$2
    if [ -f "$file" ]; then
        local count=$(grep -c "@router\." "$file" 2>/dev/null || echo "0")
        echo "📁 $name: $count endpoints"
        return $count
    else
        echo "❌ $name: Archivo no encontrado"
        return 0
    fi
}

echo "📊 RESUMEN POR ROUTER:"
echo "====================="

total=0

# Verificar cada router
count_endpoints "src/backend/routers/health.py" "Health"
total=$((total + $?))

count_endpoints "src/backend/routers/vicky.py" "Vicky"
total=$((total + $?))

count_endpoints "src/backend/routers/auth.py" "Auth"
total=$((total + $?))

count_endpoints "src/backend/routers/users.py" "Users"
total=$((total + $?))

count_endpoints "src/backend/routers/translate.py" "Translate"
total=$((total + $?))

count_endpoints "src/backend/routers/tts.py" "TTS"
total=$((total + $?))

count_endpoints "src/backend/routers/stt.py" "STT"
total=$((total + $?))

count_endpoints "src/backend/routers/voice.py" "Voice"
total=$((total + $?))

count_endpoints "src/backend/routers/conversations.py" "Conversations"
total=$((total + $?))

count_endpoints "src/backend/routers/system.py" "System"
total=$((total + $?))

count_endpoints "src/backend/routers/models.py" "Models"
total=$((total + $?))

count_endpoints "src/backend/routers/files.py" "Files"
total=$((total + $?))

count_endpoints "src/backend/routers/analytics.py" "Analytics"
total=$((total + $?))

count_endpoints "src/backend/routers/notifications.py" "Notifications"
total=$((total + $?))

count_endpoints "src/backend/routers/admin.py" "Admin"
total=$((total + $?))

count_endpoints "src/backend/routers/api_keys.py" "API Keys"
total=$((total + $?))

count_endpoints "src/backend/routers/webhooks.py" "Webhooks"
total=$((total + $?))

count_endpoints "src/backend/routers/monitoring.py" "Monitoring"
total=$((total + $?))

echo
echo "🎯 TOTAL DE ENDPOINTS: $total"
echo

echo "📋 DETALLE DE ENDPOINTS POR ROUTER:"
echo "==================================="

# Función para mostrar endpoints detallados
show_endpoints() {
    local file=$1
    local name=$2
    echo
    echo "🔸 $name Router:"
    if [ -f "$file" ]; then
        grep -n "@router\." "$file" | sed 's/@router\./  /' | head -20
        local count=$(grep -c "@router\." "$file")
        if [ $count -gt 20 ]; then
            echo "  ... y $((count - 20)) endpoints más"
        fi
    else
        echo "  ❌ Archivo no encontrado"
    fi
}

# Mostrar todos los endpoints
show_endpoints "src/backend/routers/health.py" "Health"
show_endpoints "src/backend/routers/vicky.py" "Vicky"
show_endpoints "src/backend/routers/auth.py" "Auth"
show_endpoints "src/backend/routers/users.py" "Users"
show_endpoints "src/backend/routers/translate.py" "Translate"
show_endpoints "src/backend/routers/tts.py" "TTS"
show_endpoints "src/backend/routers/stt.py" "STT"
show_endpoints "src/backend/routers/voice.py" "Voice"
show_endpoints "src/backend/routers/conversations.py" "Conversations"
show_endpoints "src/backend/routers/system.py" "System"
show_endpoints "src/backend/routers/models.py" "Models"
show_endpoints "src/backend/routers/files.py" "Files"
show_endpoints "src/backend/routers/analytics.py" "Analytics"
show_endpoints "src/backend/routers/notifications.py" "Notifications"
show_endpoints "src/backend/routers/admin.py" "Admin"
show_endpoints "src/backend/routers/api_keys.py" "API Keys"
show_endpoints "src/backend/routers/webhooks.py" "Webhooks"
show_endpoints "src/backend/routers/monitoring.py" "Monitoring"

echo
echo "🔍 VERIFICACIÓN DE IMPORTACIONES EN MAIN.PY:"
echo "============================================"
echo "📁 Verificando importaciones..."

# Verificar importaciones
missing_imports=0
for router in health vicky auth users translate tts stt voice conversations system models files analytics notifications admin api_keys webhooks monitoring; do
    if grep -q "from src.backend.routers.$router import router" src/main.py; then
        echo "✅ $router router importado correctamente"
    else
        echo "❌ $router router NO importado"
        missing_imports=$((missing_imports + 1))
    fi
done

echo
echo "#!/bin/bash

echo "🔗 VERIFICACIÓN DE REGISTRO DE ROUTERS:"
echo "======================================"
echo "📁 Verificando registros..."

routers=("health" "vicky" "auth" "users" "translate" "tts" "stt" "voice" "conversations" "system" "models" "files" "analytics" "notifications" "admin" "api_keys" "webhooks" "monitoring")

for router in "${routers[@]}"; do
    if grep -q "app.include_router.*${router}_router.*prefix=" src/main.py; then
        echo "✅ ${router} router registrado correctamente"
    else
        echo "❌ ${router} router NO registrado"
    fi
done

📊 RESUMEN FINAL:"
echo "================"
echo "🎯 Total de endpoints implementados: $total"
echo "📦 Routers creados: 18"
echo "📥 Importaciones faltantes: $missing_imports"
echo "🔗 Registros faltantes: $missing_registers"

if [ $missing_imports -eq 0 ] && [ $missing_registers -eq 0 ]; then
    echo "✅ TODAS LAS IMPORTACIONES Y REGISTROS ESTÁN CORRECTOS!"
else
    echo "⚠️  HAY PROBLEMAS EN LAS IMPORTACIONES O REGISTROS"
fi

echo
echo "🌐 Para probar la API:"
echo "====================="
echo "1. Iniciar servidor: python src/main.py"
echo "2. Documentación: http://localhost:8000/docs"
echo "3. API Root: http://localhost:8000"
echo "4. Health Check: http://localhost:8000/health"
