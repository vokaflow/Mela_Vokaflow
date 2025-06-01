#!/usr/bin/env python3
"""
🔧 Fix Main.py Syntax
Arregla el main.py eliminando HTML mezclado y corrigiendo errores de sintaxis
"""

import os
import re
from pathlib import Path

def fix_main_py():
    """Arreglar main.py eliminando HTML y corrigiendo sintaxis"""
    
    main_file = Path("/opt/vokaflow/src/main.py")
    backup_file = Path("/opt/vokaflow/src/main.py.backup.syntax_fix")
    
    print("🔧 Arreglando main.py...")
    
    # Crear backup
    if main_file.exists():
        print(f"📋 Creando backup: {backup_file}")
        with open(main_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(backup_content)
    
    # Leer archivo actual
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el punto donde termina el código Python válido
    # Buscamos el último bloque if __name__ == "__main__":
    lines = content.split('\n')
    
    # Encontrar la línea del if __name__ == "__main__":
    main_block_start = None
    for i, line in enumerate(lines):
        if 'if __name__ == "__main__":' in line:
            main_block_start = i
    
    if main_block_start is None:
        print("❌ No se encontró el bloque if __name__ == '__main__':")
        return False
    
    # Buscar el final del bloque if principal
    # El bloque if termina cuando encontramos una línea sin indentación o HTML
    end_of_python = None
    
    for i in range(main_block_start + 1, len(lines)):
        line = lines[i].strip()
        
        # Si encontramos HTML o código que no es Python, aquí termina
        if ('<' in line and '>' in line) or line.startswith('app.include_router'):
            # Buscar hacia atrás para encontrar el final real del bloque if
            for j in range(i-1, main_block_start, -1):
                prev_line = lines[j].strip()
                if prev_line and not prev_line.startswith('#'):
                    end_of_python = j + 1
                    break
            break
    
    if end_of_python is None:
        # Si no encontramos HTML, buscar hasta el final del bloque if
        indent_level = 0
        for i in range(main_block_start + 1, len(lines)):
            line = lines[i]
            if line.strip():  # línea no vacía
                current_indent = len(line) - len(line.lstrip())
                if current_indent == 0:  # vuelta a nivel 0, fin del bloque
                    end_of_python = i
                    break
        
        if end_of_python is None:
            end_of_python = len(lines)
    
    # Construir el contenido limpio
    clean_lines = lines[:end_of_python]
    
    # Agregar línea final si no existe
    if clean_lines and not clean_lines[-1].strip() == "":
        clean_lines.append("")
    
    # Escribir archivo limpio
    clean_content = '\n'.join(clean_lines)
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print(f"✅ main.py arreglado")
    print(f"📊 Líneas originales: {len(lines)}")
    print(f"📊 Líneas limpias: {len(clean_lines)}")
    print(f"🔄 Eliminadas: {len(lines) - len(clean_lines)} líneas")
    
    return True

def verify_syntax():
    """Verificar que la sintaxis de Python sea correcta"""
    
    main_file = "/opt/vokaflow/src/main.py"
    
    print("🔍 Verificando sintaxis de Python...")
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Intentar compilar el código
        compile(code, main_file, 'exec')
        print("✅ Sintaxis de Python correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error al verificar sintaxis: {e}")
        return False

def main():
    """Función principal"""
    print("🔧✨ FIX MAIN.PY SYNTAX ✨🔧")
    print("=" * 50)
    
    # Verificar archivo existe
    main_file = Path("/opt/vokaflow/src/main.py")
    if not main_file.exists():
        print("❌ main.py no encontrado")
        return
    
    # Arreglar archivo
    if fix_main_py():
        # Verificar sintaxis
        if verify_syntax():
            print("\n🎉 ¡main.py arreglado y verificado!")
        else:
            print("\n⚠️ main.py arreglado pero hay errores de sintaxis")
    else:
        print("\n❌ Error arreglando main.py")

if __name__ == "__main__":
    main() 