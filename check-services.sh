#!/bin/bash
echo "🔍 VERIFICANDO SERVICIOS VOKAFLOW"
echo "=================================="

echo "📊 Estado del backend:"
sudo systemctl status vokaflow-backend.service --no-pager -l

echo ""
echo "📊 Estado del dashboard:"
sudo systemctl status vokaflow-dashboard.service --no-pager -l

echo ""
echo "🌐 Puertos en uso:"
sudo netstat -tlnp | grep -E "(8000|3000|3001)"

echo ""
echo "🔗 URLs disponibles:"
echo "Backend API: http://192.168.1.119:8000"
echo "Dashboard: http://192.168.1.119:3000 o http://192.168.1.119:3001"
echo "Documentación: http://192.168.1.119:8000/docs"
