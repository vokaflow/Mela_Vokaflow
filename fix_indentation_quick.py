#!/usr/bin/env python3
"""
Script rápido para arreglar problemas de indentación en high_scale_task_manager.py
"""

import os

def fix_indentation():
    """Arreglar problemas específicos de indentación"""
    file_path = "/opt/vokaflow/src/backend/core/high_scale_task_manager.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Arreglar los docstrings mal indentados específicos
    replacements = [
        ('    """Iniciar workers que consumen colas Redis distribuidas"""', '        """Iniciar workers que consumen colas Redis distribuidas"""'),
        ('    """Worker loop que consume tareas de Redis distribuido"""', '        """Worker loop que consume tareas de Redis distribuido"""'),
        ('    """Procesar una tarea obtenida de Redis"""', '        """Procesar una tarea obtenida de Redis"""'),
        ('    """Resolver nombre de función a función ejecutable"""', '        """Resolver nombre de función a función ejecutable"""'),
        ('    """Registrar completación de tarea con métricas detalladas"""', '        """Registrar completación de tarea con métricas detalladas"""'),
        ('    """Manejar tarea fallida - reintento o dead letter queue"""', '        """Manejar tarea fallida - reintento o dead letter queue"""'),
        ('    """Reencolar tarea para reintento"""', '        """Reencolar tarea para reintento"""'),
        ('    """Enviar tarea fallida a Dead Letter Queue"""', '        """Enviar tarea fallida a Dead Letter Queue"""'),
        ('    """Obtener tareas de Dead Letter Queue"""', '        """Obtener tareas de Dead Letter Queue"""'),
        ('    """Reintentar tarea desde Dead Letter Queue"""', '        """Reintentar tarea desde Dead Letter Queue"""'),
        ('    """Adquirir lock distribuido usando Redis"""', '        """Adquirir lock distribuido usando Redis"""'),
        ('    """Liberar lock distribuido"""', '        """Liberar lock distribuido"""'),
        ('    """Ejecutar función con lock distribuido"""', '        """Ejecutar función con lock distribuido"""'),
        ('    """Procesar tarea en memoria (modo demostración sin Redis)"""', '        """Procesar tarea en memoria (modo demostración sin Redis)"""'),
        ('    """Seleccionar nodo Redis basado en partición"""', '        """Seleccionar nodo Redis basado en partición"""'),
        ('    """Serializar tarea para Redis"""', '        """Serializar tarea para Redis"""'),
        ('    """Loop de monitoreo en tiempo real"""', '        """Loop de monitoreo en tiempo real"""'),
        ('    """Loop de auto-scaling de workers"""', '        """Loop de auto-scaling de workers"""'),
        ('    """Escalar hacia arriba el número de workers"""', '        """Escalar hacia arriba el número de workers"""'),
        ('    """Escalar hacia abajo el número de workers"""', '        """Escalar hacia abajo el número de workers"""'),
        ('    """Obtener métricas globales del sistema"""', '        """Obtener métricas globales del sistema"""'),
        ('    """Shutdown graceful del sistema"""', '        """Shutdown graceful del sistema"""'),
    ]
    
    # Aplicar reemplazos
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Escribir contenido arreglado
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Problemas de indentación arreglados")

if __name__ == "__main__":
    fix_indentation() 