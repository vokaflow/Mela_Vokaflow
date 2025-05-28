#!/bin/bash

# Script para mover el motor de la Kinect a un ángulo específico
# Los ángulos válidos están entre -27 (hacia abajo) y 27 (hacia arriba)

# Verificar si se proporcionó un argumento
if [ $# -ne 1 ]; then
    echo "Uso: $0 <ángulo>"
    echo "  El ángulo debe estar entre -27 (hacia abajo) y 27 (hacia arriba)"
    exit 1
fi

ANGULO=$1

# Verificar que el ángulo esté en el rango válido
if [ $ANGULO -lt -27 ] || [ $ANGULO -gt 27 ]; then
    echo "Error: El ángulo debe estar entre -27 y 27"
    exit 1
fi

echo "Moviendo la Kinect al ángulo $ANGULO..."

# Usar freenect-tiltdemo con timeout para ejecutar solo durante un segundo
# Esto permite establecer el ángulo y salir
timeout 1 freenect-tiltdemo $ANGULO

echo "Motor movido. Posición actual: $ANGULO grados" 