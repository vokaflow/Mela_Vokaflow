#!/usr/bin/env python3
"""
Script para corregir automáticamente las importaciones y registros en main.py
"""
import re

def fix_main_py():
    # Leer el archivo main.py actual
    with open('src/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 Corrigiendo importaciones en main.py...")
    
    # Lista de todos los routers que necesitamos importar
    routers_to_import = [
        'health', 'vicky', 'auth', 'users', 'translate', 'tts', 'stt', 
        'voice', 'conversations', 'system', 'models', 'files', 
        'analytics', 'notifications', 'admin', 'api_keys', 'webhooks', 'monitoring'
    ]
    
    # Buscar la sección de importaciones de routers
    import_pattern = r'# Importaciones de TODOS los routers\n(.*?)(?=\n# Configuración de logging|\n# Componentes personalizados)'
    
    # Crear las nuevas importaciones
    new_imports = "# Importaciones de TODOS los routers\n"
    for router in routers_to_import:
        new_imports += f"from src.backend.routers.{router} import router as {router}_router\n"
    
    # Reemplazar las importaciones existentes
    if re.search(import_pattern, content, re.DOTALL):
        content = re.sub(import_pattern, new_imports, content, flags=re.DOTALL)
    else:
        # Si no encuentra el patrón, agregar después de las importaciones de componentes personalizados
        components_pattern = r'(from api_info import initialize_api_info, get_api_info\n)'
        if re.search(components_pattern, content):
            content = re.sub(components_pattern, r'\1\n' + new_imports, content)
    
    print("✅ Importaciones corregidas")
    
    # Ahora corregir los registros de routers
    print("🔧 Corrigiendo registros de routers...")
    
    # Buscar la sección donde se registran los routers nuevos
    register_pattern = r'# Registrar NUEVOS routers\n(.*?)(?=\n# Ruta raíz mejorada|\n@app\.get$$"/"$$)'
    
    # Crear los nuevos registros
    new_registers = "# Registrar NUEVOS routers\n"
    for router in routers_to_import:
        # Determinar el prefijo y tag apropiados
        if router == 'api_keys':
            prefix = 'api-keys'
            tag = 'API Keys'
        else:
            prefix = router.replace('_', '-')
            tag = router.replace('_', ' ').title()
        
        new_registers += f'app.include_router({router}_router, prefix=f"{{settings.API_PREFIX}}/{prefix}", tags=["{tag}"])\n'
    
    # Reemplazar los registros existentes
    if re.search(register_pattern, content, re.DOTALL):
        content = re.sub(register_pattern, new_registers, content, flags=re.DOTALL)
    else:
        # Si no encuentra el patrón, buscar antes de la ruta raíz
        root_pattern = r'(@app\.get$$"/"$$)'
        if re.search(root_pattern, content):
            content = re.sub(root_pattern, new_registers + '\n' + r'\1', content)
    
    print("✅ Registros corregidos")
    
    # Escribir el archivo corregido
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🎉 main.py corregido exitosamente!")
    
    # Verificar los cambios
    print("\n🔍 Verificando cambios...")
    with open('src/main.py', 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    imports_found = 0
    registers_found = 0
    
    for router in routers_to_import:
        if f"from src.backend.routers.{router} import router as {router}_router" in new_content:
            imports_found += 1
        if f"{router}_router" in new_content and "include_router" in new_content:
            registers_found += 1
    
    print(f"📥 Importaciones encontradas: {imports_found}/{len(routers_to_import)}")
    print(f"🔗 Registros encontrados: {registers_found}/{len(routers_to_import)}")
    
    if imports_found == len(routers_to_import) and registers_found == len(routers_to_import):
        print("✅ TODAS LAS CORRECCIONES APLICADAS CORRECTAMENTE!")
        return True
    else:
        print("⚠️ ALGUNAS CORRECCIONES NO SE APLICARON CORRECTAMENTE")
        return False

if __name__ == "__main__":
    success = fix_main_py()
    if success:
        print("\n🚀 Listo para reiniciar el servidor!")
    else:
        print("\n❌ Revisa manualmente el archivo main.py")
