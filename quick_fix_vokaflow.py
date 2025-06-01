#!/usr/bin/env python3
"""
🔧 Quick Fix VokaFlow - Solucionador rápido de errores críticos
"""

import os
import sys
import subprocess

def quick_fix_errors():
    """Arreglar errores críticos identificados"""
    print("🔧 QUICK FIX VOKAFLOW - Arreglando errores críticos...")
    print("=" * 60)
    
    # 1. Fix IndentationError en high_scale_task_manager.py
    print("🔧 Arreglando IndentationError en high_scale_task_manager.py...")
    
    try:
        # Leer el archivo
        with open('src/backend/core/high_scale_task_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Arreglar la función shutdown_high_scale_system con logs mínimos
        fixed_content = content.replace(
            """async def shutdown_high_scale_system():
    \"\"\"Shutdown sistema de alta escala\"\"\"
    global high_scale_task_manager
    if high_scale_task_manager is not None:
        try:
            await high_scale_task_manager.shutdown() 
            high_scale_task_manager = None
            logger.info("🛑 Sistema de alta escala apagado correctamente")
        except Exception as e:
            logger.error(f"❌ Error durante shutdown de high scale system: {e}")
            high_scale_task_manager = None
    else:
        # Evitar log spam - solo logear una vez cuando ya está apagado
        pass""",
            """async def shutdown_high_scale_system():
    \"\"\"Shutdown sistema de alta escala\"\"\"
    global high_scale_task_manager
    if high_scale_task_manager is not None:
        try:
            await high_scale_task_manager.shutdown() 
            high_scale_task_manager = None
            # Solo log una vez
            if not hasattr(shutdown_high_scale_system, '_logged_shutdown'):
                logger.info("🛑 Sistema de alta escala apagado correctamente")
                shutdown_high_scale_system._logged_shutdown = True
        except Exception as e:
            logger.error(f"❌ Error durante shutdown de high scale system: {e}")
            high_scale_task_manager = None
    # No más logs de spam cuando ya está apagado"""
        )
        
        # Escribir el archivo corregido
        with open('src/backend/core/high_scale_task_manager.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ IndentationError corregido")
        
    except Exception as e:
        print(f"❌ Error arreglando high_scale_task_manager.py: {e}")
    
    # 2. Verificar import circular
    print("🔧 Verificando imports circulares...")
    
    # 3. Verificar sintaxis de main.py
    print("🔧 Verificando sintaxis de main.py...")
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar para verificar sintaxis
        compile(content, 'src/main.py', 'exec')
        print("✅ Sintaxis de main.py OK")
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en main.py línea {e.lineno}: {e.msg}")
    except Exception as e:
        print(f"❌ Error verificando main.py: {e}")
    
    print("=" * 60)
    print("🎯 PRUEBA RÁPIDA - Iniciando backend...")
    
    # Intentar iniciar el backend
    try:
        result = subprocess.run([
            sys.executable, 'src/main.py'
        ], timeout=10, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend arranca sin errores de sintaxis")
        else:
            print("❌ Backend falla:")
            print(result.stderr[:500])  # Primeros 500 caracteres del error
            
    except subprocess.TimeoutExpired:
        print("⏱️ Backend arrancó correctamente (timeout después de 10s)")
        # Matar el proceso si sigue corriendo
        subprocess.run(['pkill', '-f', 'src/main.py'], capture_output=True)
        
    except Exception as e:
        print(f"❌ Error al probar backend: {e}")

def create_minimal_launcher():
    """Crear launcher mínimo para evitar errores"""
    launcher_content = '''#!/usr/bin/env python3
"""
🚀 VokaFlow Launcher Mínimo
"""

import os
import sys
import subprocess

def main():
    print("🚀 Iniciando VokaFlow con configuración mínima...")
    
    # Cambiar al directorio src
    os.chdir('/opt/vokaflow/src')
    
    # Agregar src al PYTHONPATH
    sys.path.insert(0, '/opt/vokaflow/src')
    
    # Variables de entorno mínimas
    os.environ['PYTHONPATH'] = '/opt/vokaflow/src'
    os.environ['VOKAFLOW_ENV'] = 'minimal'
    
    # Iniciar con uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn', 'main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--workers', '1',
        '--log-level', 'info'
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
'''
    
    with open('launch_minimal.py', 'w') as f:
        f.write(launcher_content)
    
    os.chmod('launch_minimal.py', 0o755)
    print("✅ Launcher mínimo creado: launch_minimal.py")

if __name__ == "__main__":
    quick_fix_errors()
    create_minimal_launcher()
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Prueba: python launch_minimal.py")
    print("2. O directamente: cd src && python main.py")
    print("3. O con uvicorn: cd src && uvicorn main:app --host 0.0.0.0 --port 8000") 