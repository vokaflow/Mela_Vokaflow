#!/bin/bash

# Script para configurar la Kinect al inicio
# Este script debe ejecutarse con permisos de root

# Establecer permisos para los dispositivos USB de Kinect
for device in $(lsusb | grep -i "Microsoft Corp. Xbox NUI" | awk '{print $2 "/" $4}' | sed 's/:$//')
do
    if [ -n "$device" ]; then
        echo "Configurando permisos para el dispositivo: $device"
        chmod a+rw /dev/bus/usb/$device
    fi
done

# Crear directorio para capturas si no existe
mkdir -p /opt/vokaflow/data/kinect_captures

# Dar permisos al directorio - usar usuario predeterminado dw7
chown -R dw7:dw7 /opt/vokaflow/data/kinect_captures

echo "Configuración de Kinect completada: $(date)" 