#!/bin/bash

echo "🔍 PROBANDO CONEXIÓN FRONTEND ↔ BACKEND"
echo "======================================"

# Verificar backend
echo "📡 Backend (localhost:8000):"
curl -s http://localhost:8000/health | jq . || echo "❌ Backend no responde"

# Verificar endpoints específicos
echo "🎮 Kinect Status:"
curl -s http://localhost:8000/api/v1/kinect/status | jq . || echo "❌ Kinect no responde"

echo "📊 Dashboard Stats:"
curl -s http://localhost:8000/api/v1/dashboard/stats | jq . || echo "❌ Dashboard no responde"

echo "🌍 Translate Stats:"
curl -s http://localhost:8000/api/v1/translate/stats | jq . || echo "❌ Translate no responde"

# Verificar frontend
echo "🖥️ Frontend (localhost:3000):"
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend corriendo" || echo "❌ Frontend no responde"

echo "✅ Prueba completada"
