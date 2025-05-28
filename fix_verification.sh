#!/bin/bash
echo "🔧 CORRIGIENDO SCRIPT DE VERIFICACIÓN"
echo "==================================="

# Buscar el patrón de verificación en el script
if grep -q "app.include_router.*_router.*prefix" verify_all_endpoints.sh; then
    echo "✅ Script de verificación parece correcto"
else
    echo "⚠️ Ajustando script de verificación..."
    
    # Hacer backup
    cp verify_all_endpoints.sh verify_all_endpoints.sh.backup
    
    # Modificar el patrón de búsqueda para los registros
    sed -i 's/include_router(.*_router/include_router(.*_router.*prefix/g' verify_all_endpoints.sh
    
    echo "✅ Script de verificación ajustado"
fi

echo "🔍 Ejecutando verificación actualizada..."
./verify_all_endpoints.sh
