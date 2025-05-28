#!/bin/bash
echo "🔄 REINICIANDO SERVIDOR CON CORRECCIONES"
echo "======================================="

# Matar procesos existentes
echo "🛑 Deteniendo servidor actual..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn.*main:app" 2>/dev/null || true
sleep 3

# Verificar que no hay procesos corriendo
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️ Forzando cierre de procesos..."
    pkill -9 -f "python.*main.py" 2>/dev/null || true
    sleep 2
fi

echo "✅ Servidor detenido"

# Limpiar logs anteriores
echo "🧹 Limpiando logs..."
mkdir -p logs
> logs/server_restart.log

# Verificar sintaxis de Python
echo "🔍 Verificando sintaxis de main.py..."
if python -m py_compile src/main.py; then
    echo "✅ Sintaxis correcta"
else
    echo "❌ Error de sintaxis en main.py"
    exit 1
fi

# Reiniciar servidor
echo "🚀 Iniciando servidor corregido..."
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

# Iniciar en background con logs
nohup python src/main.py > logs/server_restart.log 2>&1 &
SERVER_PID=$!

echo "📋 Servidor iniciado con PID: $SERVER_PID"
echo "📁 Logs en: logs/server_restart.log"

# Esperar un momento para que inicie
echo "⏳ Esperando que el servidor inicie..."
sleep 5

# Verificar que está corriendo
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ Servidor ejecutándose correctamente"
    
    # Probar conexión
    echo "🔍 Probando conexión..."
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Servidor respondiendo en http://localhost:8000"
        echo "📚 Documentación: http://localhost:8000/docs"
        
        # Mostrar algunos logs
        echo
        echo "📋 Últimas líneas del log:"
        tail -10 logs/server_restart.log
        
    else
        echo "❌ Servidor no responde"
        echo "📋 Revisando logs..."
        tail -20 logs/server_restart.log
    fi
else
    echo "❌ Error al iniciar servidor"
    echo "📋 Revisando logs de error..."
    cat logs/server_restart.log
fi

echo
echo "🎯 COMANDOS ÚTILES:"
echo "=================="
echo "📊 Ver logs en tiempo real: tail -f logs/server_restart.log"
echo "🔍 Verificar endpoints: ./verify_all_endpoints.sh"
echo "🧪 Probar endpoints: ./test_live_endpoints.sh"
echo "🛑 Detener servidor: pkill -f 'python.*main.py'"
