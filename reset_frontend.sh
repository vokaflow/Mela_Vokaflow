#!/bin/bash

echo "Eliminando frontend actual..."
rm -rf Frontend_Vokaflow

echo "Clonando version limpia desde GitHub..."
git clone https://github.com/vokaflow/VickyFlow.git Frontend_Vokaflow

echo "Verificando estado..."
cd Frontend_Vokaflow
git status

echo "Frontend resetado completamente a version remota!" 