#!/bin/bash

# Script para verificar el estado de la Kinect

echo "=== Estado de dispositivos Kinect ==="
echo ""

# Buscar dispositivos Kinect conectados
echo "Dispositivos Kinect conectados:"
lsusb | grep -i "Microsoft Corp. Xbox NUI" || echo "No se encontraron dispositivos Kinect"
echo ""

# Verificar permisos de los dispositivos
echo "Permisos de dispositivos USB:"
for device in $(lsusb | grep -i "Microsoft Corp. Xbox NUI" | awk '{print $2 "/" $4}' | sed 's/:$//')
do
    if [ -n "$device" ]; then
        echo "Dispositivo: $device"
        ls -la /dev/bus/usb/$device
    fi
done
echo ""

# Verificar directorio de capturas
echo "Directorio de capturas:"
ls -la /opt/vokaflow/data/kinect_captures
echo ""

# Verificar herramientas disponibles
echo "Herramientas de Kinect disponibles:"
for tool in freenect-camtest freenect-glview freenect-tiltdemo freenect-regtest freenect-glpclview
do
    if which $tool > /dev/null; then
        echo "$tool: Instalado ($(which $tool))"
    else
        echo "$tool: No instalado"
    fi
done

echo ""
echo "Verificación completada: $(date)" 