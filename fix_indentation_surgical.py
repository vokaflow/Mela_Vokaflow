#!/usr/bin/env python3
"""
Script quirúrgico para arreglar problemas específicos de indentación en high_scale_task_manager.py
"""

import re

def fix_indentation_surgical():
    """Arreglar problemas específicos de indentación"""
    file_path = "/opt/vokaflow/src/backend/core/high_scale_task_manager.py"
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Arreglos específicos de indentación
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Problema específico en líneas con docstrings mal indentados después de funciones async def
        if 'async def _start_redis_workers(self):' in line:
            fixed_lines.append(line)
            # La siguiente línea debe ser el docstring con indentación correcta
            if i + 1 < len(lines) and '"""Iniciar workers que consumen colas Redis distribuidas"""' in lines[i + 1]:
                fixed_lines.append('        """Iniciar workers que consumen colas Redis distribuidas"""\n')
                continue
        elif '"""Iniciar workers que consumen colas Redis distribuidas"""' in line and line.strip().startswith('"""'):
            # Ya fue manejado arriba
            continue
        elif 'async def _redis_worker_loop(self, worker_type: WorkerType, worker_id: int):' in line:
            fixed_lines.append(line)
            # La siguiente línea debe ser el docstring con indentación correcta
            if i + 1 < len(lines) and '"""Worker loop que consume tareas de Redis distribuido"""' in lines[i + 1]:
                fixed_lines.append('        """Worker loop que consume tareas de Redis distribuido"""\n')
                continue
        elif '"""Worker loop que consume tareas de Redis distribuido"""' in line and line.strip().startswith('"""'):
            # Ya fue manejado arriba
            continue
        # Línea problemática específica
        elif line_num == 321 and 'logger.info("🚀 Iniciando workers Redis distribuidos...")' in line:
            # Esta línea debe tener indentación de 8 espacios
            fixed_lines.append('        logger.info("🚀 Iniciando workers Redis distribuidos...")\n')
        elif line_num == 338 and 'worker_name = f"{worker_type.value}-{worker_id}"' in line:
            # Esta línea debe tener indentación de 8 espacios
            fixed_lines.append('        worker_name = f"{worker_type.value}-{worker_id}"\n')
        # Arreglar cualquier otra línea que tenga problemas similares
        elif re.match(r'^    async def .+:\s*$', line):
            # Función async def correcta
            fixed_lines.append(line)
        elif re.match(r'^    """.*"""$', line.strip()) and not line.startswith('        '):
            # Docstring mal indentado - debe tener 8 espacios
            fixed_lines.append('        ' + line.strip() + '\n')
        else:
            # Mantener línea original
            fixed_lines.append(line)
    
    # Escribir archivo corregido
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Problemas de indentación específicos arreglados en high_scale_task_manager.py")

if __name__ == "__main__":
    fix_indentation_surgical() 