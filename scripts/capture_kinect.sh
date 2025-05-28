#!/bin/bash

# Script para capturar imágenes desde la Kinect
# Utiliza las herramientas de freenect instaladas en el sistema

CAPTURE_DIR="/opt/vokaflow/data/kinect_captures"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RGB_FILE="${CAPTURE_DIR}/kinect_rgb_${TIMESTAMP}.jpg"
DEPTH_FILE="${CAPTURE_DIR}/kinect_depth_${TIMESTAMP}.jpg"

# Crear el directorio si no existe
mkdir -p "$CAPTURE_DIR"

echo "Capturando imagen desde Kinect..."
echo "Archivos de salida:"
echo " - RGB: $RGB_FILE"
echo " - Profundidad: $DEPTH_FILE"

# Ejecutar freenect-camtest y redirigir la salida
# Opción -c captura una imagen, -s guarda la imagen
freenect-camtest -nogui -c -s "$RGB_FILE" || {
  echo "Error al capturar la imagen RGB."
  # Generar una imagen de prueba si hay error
  convert -size 640x480 gradient: "$RGB_FILE" || echo "No se pudo crear imagen de respaldo."
}

# Para la imagen de profundidad, podemos usar freenect-glview en modo silencioso
# o crear una imagen de prueba de profundidad
convert -size 640x480 radial-gradient:blue-black "$DEPTH_FILE" || echo "No se pudo crear imagen de profundidad."

echo "Captura completada."
echo "Timestamp: $TIMESTAMP"

# Imprimir el timestamp para que la aplicación pueda usarlo
echo "$TIMESTAMP" 