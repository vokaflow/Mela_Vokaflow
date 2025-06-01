#!/usr/bin/env python3
"""
Script para verificar la sintaxis de los archivos modificados
"""

import ast
import sys
import traceback

def check_file_syntax(file_path):
    """Verificar la sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar el código para verificar sintaxis
        ast.parse(content)
        print(f"✅ {file_path}: Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path}: Error de sintaxis en línea {e.lineno}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"⚠️ {file_path}: Error al leer archivo: {e}")
        return False

def main():
    """Verificar sintaxis de los archivos modificados"""
    files_to_check = [
        "src/main.py",
        "src/backend/routers/dashboard.py", 
        "src/backend/routers/system.py",
        "src/backend/routers/translations_dashboard.py"
    ]
    
    print("🔍 Verificando sintaxis de archivos modificados...\n")
    
    all_ok = True
    for file_path in files_to_check:
        if not check_file_syntax(file_path):
            all_ok = False
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ TODOS LOS ARCHIVOS TIENEN SINTAXIS CORRECTA")
        print("🚀 El backend debería poder ejecutarse sin errores")
    else:
        print("❌ HAY ERRORES DE SINTAXIS QUE DEBEN CORREGIRSE")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 