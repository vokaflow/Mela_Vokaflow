#!/bin/bash
# Script para reiniciar Nginx y aplicar la nueva configuración

echo "Verificando la configuración de Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "La configuración de Nginx es válida."
    echo "Reiniciando Nginx..."
    sudo systemctl restart nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx se ha reiniciado correctamente."
    else
        echo "❌ Hubo un problema al reiniciar Nginx."
    fi
else
    echo "❌ La configuración de Nginx no es válida. Por favor, corrija los errores antes de reiniciar."
fi 