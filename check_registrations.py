#!/usr/bin/env python3
"""
Verificación manual de registros de routers
"""

def check_registrations():
    print("🔍 VERIFICACIÓN MANUAL DE REGISTROS DE ROUTERS")
    print("===========================================")
    
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista de routers a verificar
        routers = [
            'health', 'vicky', 'auth', 'users', 'translate', 'tts', 'stt', 
            'voice', 'conversations', 'system', 'models', 'files', 
            'analytics', 'notifications', 'admin', 'api_keys', 'webhooks', 'monitoring'
        ]
        
        # Buscar registros
        print("\n📋 REGISTROS ENCONTRADOS:")
        print("-" * 30)
        
        found_count = 0
        for router in routers:
            pattern = f"app.include_router({router}_router"
            if pattern in content:
                line_num = content[:content.find(pattern)].count('\n') + 1
                print(f"✅ {router}_router - Línea {line_num}")
                found_count += 1
            else:
                print(f"❌ {router}_router - NO ENCONTRADO")
        
        print(f"\n📊 RESUMEN: {found_count}/{len(routers)} registros encontrados")
        
        # Mostrar sección de registros
        if "# Registrar todos los routers" in content:
            start = content.find("# Registrar todos los routers")
            end = content.find("\n\n", start)
            if end == -1:  # Si no hay doble salto de línea, buscar otro patrón
                end = content.find("@app.get", start)
                if end == -1:
                    end = content.find("# Punto de entrada", start)
                    if end == -1:
                        end = len(content)
            
            print("\n📝 SECCIÓN DE REGISTROS:")
            print("-" * 30)
            print(content[start:end])
        
        # Verificar si el servidor está corriendo
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'python.*main.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✅ SERVIDOR CORRIENDO")
            
            # Probar endpoints
            print("\n🧪 PROBANDO ENDPOINTS:")
            print("-" * 30)
            
            endpoints = [
                ('/', 'Raíz'),
                ('/health', 'Health'),
                ('/docs', 'Documentación'),
                ('/api/health', 'API Health')
            ]
            
            for endpoint, name in endpoints:
                cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8000{endpoint}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                status = result.stdout.strip()
                
                if status.startswith('2') or status.startswith('3'):
                    print(f"✅ {name}: {status}")
                else:
                    print(f"❌ {name}: {status}")
        else:
            print("\n❌ SERVIDOR NO ESTÁ CORRIENDO")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    check_registrations()
