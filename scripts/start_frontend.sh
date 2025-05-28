#!/bin/bash

# Script para iniciar el frontend de VokaFlow en modo producción
# Este script debe ejecutarse con permisos de usuario normal

# Cambiar al directorio del frontend
cd /opt/vokaflow/Frontend_Vokaflow

# Asegurarse de que la compilación está hecha
echo "Compilando la aplicación en modo producción..."
pnpm build || {
    echo "Error durante la compilación"
    exit 1
}

# Iniciar el servidor en modo producción
echo "Iniciando el servidor en modo producción..."
exec pnpm start 