#!/usr/bin/env python3
"""
Script definitivo para arreglar todos los problemas de indentación en high_scale_task_manager.py
"""

import re

def fix_indentation_final():
    """Arreglar todos los problemas de indentación definitivamente"""
    file_path = "/opt/vokaflow/src/backend/core/high_scale_task_manager.py"
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # Si es una definición de función async def o def
        if re.match(r'^\s*(async\s+)?def\s+.*\):\s*$', line.strip()):
            fixed_lines.append(line)
            i += 1
            
            # La siguiente línea debería ser un docstring o código indentado
            if i < len(lines):
                next_line = lines[i]
                
                # Si la siguiente línea es un docstring que no está correctamente indentado
                if '"""' in next_line and not next_line.startswith('        '):
                    # Calcular la indentación base de la función
                    func_indent = len(line) - len(line.lstrip())
                    correct_indent = ' ' * (func_indent + 4)  # 4 espacios adicionales para el cuerpo
                    
                    # Arreglar la indentación del docstring
                    fixed_next_line = correct_indent + next_line.strip() + '\n'
                    fixed_lines.append(fixed_next_line)
                    i += 1
                    
                    # Si hay líneas del docstring multilínea, arreglarlas también
                    while i < len(lines) and '"""' not in lines[i]:
                        if lines[i].strip():  # No vacía
                            fixed_lines.append(correct_indent + lines[i].strip() + '\n')
                        else:
                            fixed_lines.append(lines[i])
                        i += 1
                    
                    # Línea de cierre del docstring
                    if i < len(lines) and '"""' in lines[i]:
                        fixed_lines.append(correct_indent + lines[i].strip() + '\n')
                        i += 1
                else:
                    fixed_lines.append(next_line)
                    i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    # Escribir archivo arreglado
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Todos los problemas de indentación arreglados en high_scale_task_manager.py")

if __name__ == "__main__":
    fix_indentation_final() 