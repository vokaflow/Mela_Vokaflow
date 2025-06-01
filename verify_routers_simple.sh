#!/bin/bash

echo "🔗 VERIFICACIÓN SIMPLE DE REGISTRO DE ROUTERS:"
echo "=============================================="
echo "📁 Verificando registros en src/main.py..."
echo ""

# Lista de routers a verificar
declare -a routers=("health" "vicky" "auth" "users" "translate" "tts" "stt" "voice" "conversations" "system" "models" "files" "analytics" "notifications" "admin" "api_keys" "webhooks" "monitoring")

registered_count=0
total_routers=${#routers[@]}

for router in "${routers[@]}"; do
    if grep -q "app.include_router.*${router}_router" src/main.py; then
        echo "✅ ${router} router registrado correctamente"
        ((registered_count++))
    else
        echo "❌ ${router} router NO registrado"
    fi
done

echo ""
echo "📊 RESUMEN:"
echo "==========="
echo "🎯 Total de routers: $total_routers"
echo "✅ Registrados: $registered_count"
echo "❌ Faltantes: $((total_routers - registered_count))"

if [ $registered_count -eq $total_routers ]; then
    echo "🎉 ¡TODOS LOS ROUTERS ESTÁN REGISTRADOS!"
else
    echo "⚠️  Faltan routers por registrar"
fi

echo ""
echo "🔍 DETALLES DE REGISTROS ENCONTRADOS:"
echo "===================================="
grep -n "app.include_router" src/main.py | head -20
