# VokaFlow Backend - Guía Rápida

## 🚀 Iniciar el Backend

Después de reiniciar el PC:

```bash
cd /opt/vokaflow
source venv/bin/activate
python start_backend.py
```

### Método alternativo:
```bash
cd /opt/vokaflow/src
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Probar el Backend

```bash
cd /opt/vokaflow
source venv/bin/activate
python quick_test.py
```

## 📖 Documentación

Una vez que el backend esté ejecutándose:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Página principal**: http://localhost:8000/

## 🔗 Endpoints Principales

### Dashboard Frontend
- `GET /api/dashboard/stats` - Estadísticas del dashboard
- `GET /api/translations/stats` - Estadísticas de traducciones  
- `GET /api/system/health` - Salud del sistema

### Básicos
- `GET /health` - Health check
- `GET /` - Página principal con información

## ✅ Verificación Rápida

```bash
curl http://localhost:8000/health
```

Debería devolver:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "...",
  "message": "VokaFlow API está funcionando correctamente"
}
```

## 📊 Estado Actual

- ✅ Base de datos funcionando (con datos de prueba)
- ✅ Endpoints principales creados
- ✅ Documentación habilitada
- ✅ CORS configurado
- ✅ Sistema de logging

## 🔧 Solución de Problemas

### Puerto ocupado
```bash
# Ver qué proceso usa el puerto 8000
lsof -i :8000

# Matar procesos si es necesario
pkill -f python
```

### Archivos faltantes
Los archivos estáticos para la documentación se descargan automáticamente.

## 🌐 Frontend

El frontend está en: `Frontend_Vokaflow/`
- Deployed: https://dashboard.vokaflow.com
- Local dev: http://localhost:3000 