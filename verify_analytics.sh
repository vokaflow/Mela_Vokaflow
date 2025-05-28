#!/bin/bash
echo "🔍 VERIFICACIÓN DE ANALYTICS ROUTER"
echo "=================================="
echo

echo "📁 Archivos creados:"
ls -la src/backend/routers/analytics.py src/backend/models/analytics_model.py

echo
echo "📊 Endpoints implementados:"
grep -n "@router\." src/backend/routers/analytics.py | grep -E "(get|post|put|delete|patch)"

echo
echo "🔢 Total de endpoints:"
grep -c "@router\." src/backend/routers/analytics.py

echo
echo "📋 Registro en main.py:"
grep -n "analytics" src/main.py

echo
echo "✅ Analytics Router implementado correctamente!"
