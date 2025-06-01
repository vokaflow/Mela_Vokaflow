#!/bin/bash
# 🚀✨ VokaFlow Enterprise Launch Script ✨🚀

echo "🚀✨ LANZANDO VOKAFLOW ENTERPRISE ✨🚀"
echo "================================="

# Activar entorno virtual
source venv/bin/activate

# Matar procesos previos
echo "🔄 Limpiando procesos previos..."
lsof -ti :8000 | xargs -r kill -9 2>/dev/null
sleep 2

# Lanzar backend en modo production
echo "🚀 Iniciando Backend Enterprise..."
python src/main.py &
BACKEND_PID=$!

# Esperar a que el backend esté listo
echo "⏳ Esperando backend..."
sleep 5

# Verificar que el backend esté funcionando
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend Enterprise ACTIVO en puerto 8000"
    echo "🌟 VokaFlow Enterprise conquistando la galaxia..."
    echo "💫 Acceder a: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    echo ""
    echo "🎯 Para detener: Ctrl+C"
    wait $BACKEND_PID
else
    echo "❌ Error: Backend no responde"
    exit 1
fi
