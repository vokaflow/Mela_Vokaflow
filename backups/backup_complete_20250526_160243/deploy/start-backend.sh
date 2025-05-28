#!/bin/bash
cd /opt/vokaflow
source venv/bin/activate
export PYTHONPATH=/opt/vokaflow
export PORT=5000
export HOST=0.0.0.0
export PGSSLMODE=disable
export DATABASE_URL=postgresql://vokaflow:vokaflowpass@localhost:5432/vokaflow_db?sslmode=disable
export DATABASE_URL_UNPOOLED=postgresql://vokaflow:vokaflowpass@localhost:5432/vokaflow_db?sslmode=disable
python src/main.py 