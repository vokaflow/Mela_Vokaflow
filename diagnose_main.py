#!/usr/bin/env python3
"""
Diagnóstico detallado del archivo main.py
"""

def diagnose_main_py():
    print("🔍 DIAGNÓSTICO DETALLADO DE MAIN.PY")
    print("=" * 50)
    
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Tamaño del archivo: {len(content)} caracteres")
        print(f"📄 Líneas totales: {len(content.splitlines())}")
        
        # Buscar importaciones de routers
        print("\n📥 IMPORTACIONES ENCONTRADAS:")
        print("-" * 30)
        import_lines = []
        for i, line in enumerate(content.splitlines(), 1):
            if 'from src.backend.routers.' in line and 'import router as' in line:
                import_lines.append((i, line.strip()))
                print(f"Línea {i}: {line.strip()}")
        
        if not import_lines:
            print("❌ NO se encontraron importaciones de routers")
        else:
            print(f"✅ Encontradas {len(import_lines)} importaciones")
        
        # Buscar registros de routers
        print("\n🔗 REGISTROS ENCONTRADOS:")
        print("-" * 30)
        register_lines = []
        for i, line in enumerate(content.splitlines(), 1):
            if 'app.include_router(' in line and '_router' in line:
                register_lines.append((i, line.strip()))
                print(f"Línea {i}: {line.strip()}")
        
        if not register_lines:
            print("❌ NO se encontraron registros de routers")
        else:
            print(f"✅ Encontrados {len(register_lines)} registros")
        
        # Buscar patrones problemáticos
        print("\n⚠️ ANÁLISIS DE PROBLEMAS:")
        print("-" * 30)
        
        # Verificar si hay registros duplicados o conflictivos
        if 'include_router(health_router' in content:
            print("✅ health_router encontrado en registros")
        else:
            print("❌ health_router NO encontrado en registros")
            
        if 'include_router(vicky_router' in content:
            print("✅ vicky_router encontrado en registros")
        else:
            print("❌ vicky_router NO encontrado en registros")
        
        # Verificar estructura del archivo
        if 'app = FastAPI(' in content:
            print("✅ Aplicación FastAPI definida")
        else:
            print("❌ Aplicación FastAPI NO encontrada")
        
        # Buscar la sección donde deberían estar los registros
        sections = [
            "# Registrar NUEVOS routers",
            "# Registrar routers",
            "app.include_router(",
            "# Punto de entrada"
        ]
        
        print("\n📍 SECCIONES DEL ARCHIVO:")
        print("-" * 30)
        for section in sections:
            if section in content:
                line_num = content[:content.find(section)].count('\n') + 1
                print(f"✅ '{section}' encontrado en línea {line_num}")
            else:
                print(f"❌ '{section}' NO encontrado")
        
        return content, import_lines, register_lines
        
    except FileNotFoundError:
        print("❌ ERROR: No se encontró el archivo src/main.py")
        return None, [], []
    except Exception as e:
        print(f"❌ ERROR al leer main.py: {e}")
        return None, [], []

if __name__ == "__main__":
    content, imports, registers = diagnose_main_py()
    
    if content:
        print(f"\n📊 RESUMEN:")
        print(f"📥 Importaciones: {len(imports)}")
        print(f"🔗 Registros: {len(registers)}")
        
        if len(imports) == 0 and len(registers) == 0:
            print("\n🚨 PROBLEMA CRÍTICO: No hay importaciones ni registros")
            print("💡 Necesitamos reconstruir la sección de routers")
        elif len(imports) > 0 and len(registers) == 0:
            print("\n⚠️ PROBLEMA: Hay importaciones pero no registros")
            print("💡 Necesitamos agregar los registros")
        elif len(imports) == 0 and len(registers) > 0:
            print("\n⚠️ PROBLEMA: Hay registros pero no importaciones")
            print("💡 Necesitamos agregar las importaciones")
        else:
            print("\n✅ Hay importaciones y registros")
            print("💡 Verificar que coincidan los nombres")
