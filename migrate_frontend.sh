#!/bin/bash
# Migrar dashboard a Frontend_Vokaflow

echo "🔄 Migrando dashboard a Frontend_Vokaflow..."

# Ir al directorio base
cd /opt/vokaflow

# Eliminar Frontend_Vokaflow si existe
if [ -d "Frontend_Vokaflow" ]; then
    echo "🧹 Limpiando Frontend_Vokaflow existente..."
    rm -rf Frontend_Vokaflow
fi

# Crear nuevo directorio Frontend_Vokaflow
echo "📁 Creando directorio Frontend_Vokaflow..."
mkdir -p Frontend_Vokaflow

# Copiar todo el contenido de dashboard a Frontend_Vokaflow
echo "📋 Copiando contenido de dashboard a Frontend_Vokaflow..."
cp -r dashboard/* Frontend_Vokaflow/

# Verificar que se copió package.json
if [ -f "Frontend_Vokaflow/package.json" ]; then
    echo "✅ package.json encontrado en Frontend_Vokaflow"
    echo "🎉 ¡Migración completada!"
    echo ""
    echo "📋 Scripts disponibles en Frontend_Vokaflow:"
    cd Frontend_Vokaflow
    npm run 2>/dev/null | grep -A 20 "available scripts:" || echo "   • dev, build, start (scripts estándar Next.js)"
    cd ..
else
    echo "❌ Error: package.json no encontrado en Frontend_Vokaflow"
    exit 1
fi

echo ""
echo "🚀 Ahora el launcher debería encontrar el frontend correctamente"
echo "💫 Ejecuta: python launch_enterprise_vokaflow_fixed.py" 