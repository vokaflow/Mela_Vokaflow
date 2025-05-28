#!/bin/bash
cd /opt/vokaflow
source venv/bin/activate
export PYTHONPATH=/opt/vokaflow
export PORT=8000
export HOST=0.0.0.0
export PGSSLMODE=disable
export DATABASE_URL=postgresql://vokaflow:vokaflowpass@localhost:5432/vokaflow_db?sslmode=disable
export DATABASE_URL_UNPOOLED=postgresql://vokaflow:vokaflowpass@localhost:5432/vokaflow_db?sslmode=disable

# Forzar el uso de puerto 8000 en todas las interfaces (0.0.0.0)
echo "Forzando el uso del puerto 8000 en todas las interfaces (0.0.0.0)"

# Usar uvicorn directamente para asegurarnos que escuche en todas las interfaces
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info 