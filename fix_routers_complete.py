#!/usr/bin/env python3
"""
Solución completa para corregir routers en main.py
"""
import re
import os

def backup_main():
    """Crear backup del archivo main.py"""
    if os.path.exists('src/main.py'):
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        with open('src/main.py.backup', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Backup creado: src/main.py.backup")
        return content
    return None

def create_router_section():
    """Crear la sección completa de routers"""
    
    # Lista de todos los routers
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
    
    # Crear importaciones
    imports_section = "\n# Importaciones de routers\n"
    for router_name, _ in routers:
        imports_section += f"from src.backend.routers.{router_name} import router as {router_name}_router\n"
    
    # Crear registros
    registers_section = "\n# Registrar todos los routers\n"
    for router_name, tag in routers:
        prefix = router_name.replace('_', '-')
        registers_section += f'app.include_router({router_name}_router, prefix=f"{{settings.API_PREFIX}}/{prefix}", tags=["{tag}"])\n'
    
    return imports_section, registers_section

def fix_main_py_complete():
    """Corregir completamente el archivo main.py"""
    
    print("🔧 INICIANDO CORRECCIÓN COMPLETA DE MAIN.PY")
    print("=" * 50)
    
    # Crear backup
    content = backup_main()
    if not content:
        print("❌ No se pudo leer main.py")
        return False
    
    # Crear secciones de routers
    imports_section, registers_section = create_router_section()
    
    print("📝 Creando nueva versión de main.py...")
    
    # Buscar donde insertar las importaciones (después de las importaciones existentes)
    # Buscar la línea que contiene "from api_info import"
    api_info_pattern = r'(from api_info import initialize_api_info, get_api_info\n)'
    
    if re.search(api_info_pattern, content):
        # Insertar importaciones después de api_info
        content = re.sub(api_info_pattern, r'\1' + imports_section, content)
        print("✅ Importaciones insertadas después de api_info")
    else:
        # Buscar otro punto de inserción
        system_monitor_pattern = r'(from system_monitor import get_system_monitor\n)'
        if re.search(system_monitor_pattern, content):
            content = re.sub(system_monitor_pattern, r'\1' + imports_section, content)
            print("✅ Importaciones insertadas después de system_monitor")
        else:
            print("⚠️ No se encontró punto de inserción para importaciones")
    
    # Buscar donde insertar los registros
    # Buscar antes de la ruta raíz @app.get("/")
    root_route_pattern = r'(@app\.get$$"/"$$)'
    
    if re.search(root_route_pattern, content):
        content = re.sub(root_route_pattern, registers_section + '\n' + r'\1', content)
        print("✅ Registros insertados antes de la ruta raíz")
    else:
        # Buscar otro punto de inserción
        if '# Punto de entrada para ejecución directa' in content:
            content = content.replace('# Punto de entrada para ejecución directa', 
                                    registers_section + '\n# Punto de entrada para ejecución directa')
            print("✅ Registros insertados antes del punto de entrada")
        else:
            print("⚠️ No se encontró punto de inserción para registros")
    
    # Limpiar registros duplicados o conflictivos
    print("🧹 Limpiando registros duplicados...")
    
    # Remover registros antiguos que puedan estar duplicados
    old_patterns = [
        r'app\.include_router\(health_router_new.*?\n',
        r'app\.include_router\(vicky_router_new.*?\n',
        r'app\.include_router\(.*?_router_new.*?\n',
        r'# Registrar NUEVOS routers\n.*?(?=\n@app\.get|\n# Ruta raíz)',
    ]
    
    for pattern in old_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Escribir el archivo corregido
    try:
        with open('src/main.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Archivo main.py actualizado")
        
        # Verificar sintaxis
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', 'src/main.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sintaxis de Python correcta")
            return True
        else:
            print(f"❌ Error de sintaxis: {result.stderr}")
            # Restaurar backup
            with open('src/main.py.backup', 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open('src/main.py', 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print("🔄 Backup restaurado")
            return False
            
    except Exception as e:
        print(f"❌ Error al escribir archivo: {e}")
        return False

def verify_fix():
    """Verificar que la corrección funcionó"""
    print("\n🔍 VERIFICANDO CORRECCIÓN...")
    print("-" * 30)
    
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        routers = ['health', 'vicky', 'auth', 'users', 'translate', 'tts', 'stt', 
                  'voice', 'conversations', 'system', 'models', 'files', 
                  'analytics', 'notifications', 'admin', 'api_keys', 'webhooks', 'monitoring']
        
        imports_found = 0
        registers_found = 0
        
        for router in routers:
            # Verificar importación
            if f"from src.backend.routers.{router} import router as {router}_router" in content:
                imports_found += 1
            
            # Verificar registro
            if f"app.include_router({router}_router" in content:
                registers_found += 1
        
        print(f"📥 Importaciones encontradas: {imports_found}/{len(routers)}")
        print(f"🔗 Registros encontrados: {registers_found}/{len(routers)}")
        
        if imports_found == len(routers) and registers_found == len(routers):
            print("🎉 ¡CORRECCIÓN EXITOSA!")
            return True
        else:
            print("⚠️ Corrección incompleta")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    success = fix_main_py_complete()
    if success:
        verify_success = verify_fix()
        if verify_success:
            print("\n🚀 ¡LISTO PARA REINICIAR EL SERVIDOR!")
            print("Ejecuta: ./restart_with_fixes.sh")
        else:
            print("\n🔧 Necesita ajustes adicionales")
    else:
        print("\n❌ La corrección falló")
        print("💡 Revisa el backup en src/main.py.backup")
