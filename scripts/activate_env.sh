#!/bin/bash

# Script para activar el entorno virtual de VokaFlow de manera segura
# Creado para asegurar la persistencia del entorno virtual después de reinicios

# Directorio de VokaFlow
VOKAFLOW_DIR="/opt/vokaflow"
VENV_DIR="$VOKAFLOW_DIR/venv"

# Comprobar si el directorio existe
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: El entorno virtual no existe en $VENV_DIR"
    echo "Creando un nuevo entorno virtual..."
    cd "$VOKAFLOW_DIR" || exit 1
    python3 -m venv venv
fi

# Activar el entorno virtual
source "$VENV_DIR/bin/activate"

# Verificar si se activó correctamente
if [[ "$VIRTUAL_ENV" != "$VENV_DIR" ]]; then
    echo "Error: No se pudo activar el entorno virtual"
    return 1
fi

# Establecer variables de entorno necesarias
export PYTHONPATH="$VOKAFLOW_DIR"
echo "Entorno virtual de VokaFlow activado correctamente"

# Cambiar al directorio del proyecto
cd "$VOKAFLOW_DIR" || return 1

# Mostrar mensaje informativo
echo -e "\033[1;32m[VokaFlow]\033[0m Entorno de desarrollo activado"
echo -e "\033[1;34mDirectorio:\033[0m $VOKAFLOW_DIR"
echo -e "\033[1;34mEntorno virtual:\033[0m $VENV_DIR"
echo -e "\033[1;34mPython:\033[0m $(which python)"
echo -e "\033[1;34mVersión de Python:\033[0m $(python --version)" 