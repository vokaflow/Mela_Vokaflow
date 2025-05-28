#!/bin/bash

# Script para capturar imágenes desde la Kinect
# Utiliza las herramientas de freenect

DIR_CAPTURAS="/opt/vokaflow/data/kinect_captures"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVO_RGB="${DIR_CAPTURAS}/kinect_rgb_${TIMESTAMP}.png"
ARCHIVO_DEPTH="${DIR_CAPTURAS}/kinect_depth_${TIMESTAMP}.png"

# Asegurarse de que el directorio existe
mkdir -p "$DIR_CAPTURAS"

echo "Capturando imagen desde Kinect..."
echo "Archivos de salida:"
echo " - RGB: $ARCHIVO_RGB"
echo " - Profundidad: $ARCHIVO_DEPTH"

# Ejecutar freenect-camtest para capturar una imagen
# El comando se ejecuta en modo headless y captura solo un frame
freenect-camtest -nogui -s "$ARCHIVO_RGB" -c

echo "Captura completada: $(date)"
echo "Para verificar la captura puedes usar:"
echo "scp ${ARCHIVO_RGB} usuario@tupc:/ruta/destino/" 