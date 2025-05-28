#!/usr/bin/env python3
"""
Script para agregar manualmente los registros de routers en main.py
"""
import os
import re

def backup_main():
    """Crear backup del archivo main.py"""
    if not os.path.exists('src/main.py.backup'):
        if os.path.exists('src/main.py'):
            with open('src/main.py', 'r', encoding='utf-8') as f:
                content = f.read()
            with open('src/main.py.backup', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Backup creado: src/main.py.backup")
            return content
    else:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ Usando archivo existente (backup ya existe)")
        return content
    return None

def add_router_registrations():
    """Agregar registros de routers directamente"""
    content = backup_main()
    if not content:
        print("❌ No se pudo leer main.py")
        return False
    
    # Lista de routers a registrar
    routers = [
        ('health', 'Health'),
        ('vicky', 'Vicky'),
        ('auth', 'Auth'),
        ('users', 'Users'),
        ('translate', 'Translate'),
        ('tts', 'TTS'),
        ('stt', 'STT'),
        ('voice', 'Voice'),
        ('conversations', 'Conversations'),
        ('system', 'System'),
        ('models', 'Models'),
        ('files', 'Files'),
        ('analytics', 'Analytics'),
        ('notifications', 'Notifications'),
        ('admin', 'Admin'),
        ('api_keys', 'API Keys'),
        ('webhooks', 'Webhooks'),
        ('monitoring', 'Monitoring')
    ]
    
    # Crear bloque de registros
    registration_block = "\n# Registrar todos los routers\n"
    for router_name, tag in routers:
        prefix = router_name.replace('_', '-')
        registration_block += f'app.include_router({router_name}_router, prefix=f"{{settings.API_PREFIX}}/{prefix}", tags=["{tag}"])\n'
    
    # Buscar punto de inserción - justo antes de la ruta raíz
    if '@app.get("/")' in content:
        # Insertar antes de la ruta raíz
        content = content.replace('@app.get("/")', registration_block + '\n@app.get("/")')
        print("✅ Registros insertados antes de la ruta raíz")
    elif '# Punto de entrada para ejecución directa' in content:
        # Insertar antes del punto de entrada
        content = content.replace('# Punto de entrada para ejecución directa', 
                                registration_block + '\n# Punto de entrada para ejecución directa')
        print("✅ Registros insertados antes del punto de entrada")
    else:
        # Insertar al final del archivo
        content += "\n" + registration_block
        print("✅ Registros insertados al final del archivo")
    
    # Eliminar registros duplicados o conflictivos
    # Patrones a buscar y eliminar
    patterns_to_remove = [
        r'# Registrar TODOS los routers\n.*?(?=\n\n)',
        r'# Registrar NUEVOS routers\n.*?(?=\n\n)',
        r'app\.include_router\(.*?_router_new.*?\n',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Guardar el archivo modificado
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo main.py actualizado con registros de routers")
    return True

def create_restart_script():
    """Crear script de reinicio si no existe"""
    if not os.path.exists('./restart_with_fixes.sh'):
        restart_script = """#!/bin/bash
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
"""
        with open('./restart_with_fixes.sh', 'w') as f:
            f.write(restart_script)
        os.chmod('./restart_with_fixes.sh', 0o755)
        print("✅ Script de reinicio creado: restart_with_fixes.sh")
    else:
        print("✅ Script de reinicio ya existe")

def create_verification_fix():
    """Crear script para corregir el verificador si es necesario"""
    verification_fix = """#!/bin/bash
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
"""
    with open('./fix_verification.sh', 'w') as f:
        f.write(verification_fix)
    os.chmod('./fix_verification.sh', 0o755)
    print("✅ Script de corrección de verificación creado: fix_verification.sh")

def main():
    print("🔧 CORRECCIÓN MANUAL DE REGISTROS DE ROUTERS")
    print("=========================================")
    
    # Agregar registros
    if add_router_registrations():
        # Crear script de reinicio
        create_restart_script()
        
        # Crear script para corregir verificador
        create_verification_fix()
        
        print("\n🚀 CORRECCIONES APLICADAS CORRECTAMENTE")
        print("Ejecuta los siguientes comandos:")
        print("1. ./restart_with_fixes.sh")
        print("2. ./fix_verification.sh")
        print("3. ./verify_all_endpoints.sh")
    else:
        print("\n❌ ERROR AL APLICAR CORRECCIONES")

if __name__ == "__main__":
    main()
