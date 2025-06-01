#!/bin/bash
# 🚀 VokaFlow Enterprise - Inicio Total
# Activa TODOS los servicios y componentes

echo "🚀✨ INICIANDO VOKAFLOW ENTERPRISE TOTAL ✨🚀"
echo "=================================================="

# Activar servicios systemd
echo "⚙️ Activando servicios systemd..."
sudo systemctl start vokaflow-enterprise-backend
sudo systemctl start vokaflow-vicky  
sudo systemctl start vokaflow-frontend
sudo systemctl start vokaflow-preload
sudo systemctl start vokaflow-system-check

echo "✅ Servicios systemd iniciados"

# Verificar estado
echo "📊 Estado de servicios:"
sudo systemctl status vokaflow-enterprise-backend --no-pager -l
sudo systemctl status vokaflow-vicky --no-pager -l

echo "🎉 VokaFlow Enterprise TOTAL activado!"
echo "🌐 Backend: http://localhost:8000"
echo "🖥️ Dashboard: http://localhost:3000"
echo "📊 Docs: http://localhost:8000/docs"
