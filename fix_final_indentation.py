#!/usr/bin/env python3
"""
Script muy específico para arreglar SOLO los problemas de indentación detectados
sin tocar ni borrar nada más del código
"""

def fix_specific_indentation():
    """Arreglar solo los problemas específicos detectados"""
    file_path = "/opt/vokaflow/src/backend/core/high_scale_task_manager.py"
    
    # Leer archivo
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Arreglos específicos muy puntuales
    for i in range(len(lines)):
        line = lines[i].rstrip()
        line_num = i + 1
        
        # Arreglo específico para línea ~1129: optimized_workers dict indentation
        if 'WorkerType.CPU_INTENSIVE: max(1, cpu_count // 2)' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: optimized_workers indentation")
            
        elif 'WorkerType.IO_INTENSIVE: cpu_count' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: optimized_workers indentation")
            
        elif 'WorkerType.MEMORY_INTENSIVE: max(1, cpu_count // 4)' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: optimized_workers indentation")
            
        elif 'WorkerType.NETWORK_INTENSIVE: cpu_count' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: optimized_workers indentation")
            
        elif 'WorkerType.GENERAL_PURPOSE: max(2, cpu_count // 2)' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: optimized_workers indentation")
        
        # Arreglo para return HighScaleTaskManager
        elif 'max_workers_per_type=optimized_workers,' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: HighScaleTaskManager parameter indentation")
            
        elif 'enable_auto_scaling=True,' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: HighScaleTaskManager parameter indentation")
            
        elif 'enable_monitoring=True,' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: HighScaleTaskManager parameter indentation")
            
        elif 'partition_count=8  # Reducido de 16' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: HighScaleTaskManager parameter indentation")
        
        # Arreglo para initialize_high_scale_system function body
        elif 'high_scale_task_manager = create_optimized_high_scale_manager()' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: initialize_high_scale_system body")
            
        elif 'await high_scale_task_manager.initialize()' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: initialize_high_scale_system body")
            
        elif 'logger.info("🚀 Sistema de alta escala inicializado correctamente")' in line and not line.startswith('        '):
            lines[i] = '        ' + line.lstrip() + '\n'
            print(f"✅ Arreglada línea {line_num}: initialize_high_scale_system body")
    
    # Escribir archivo corregido
    with open(file_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ Problemas específicos de indentación arreglados")

if __name__ == "__main__":
    fix_specific_indentation() 