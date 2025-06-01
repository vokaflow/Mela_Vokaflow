# 🚀 VokaFlow Backend

<div align="center">

![VokaFlow Logo](static/img/vokaflow-logo.png)

**Sistema de Comunicación Avanzado con IA, Traducción y Reconocimiento de Voz**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)](https://redis.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

[🌐 Demo](http://localhost:8000) • [📖 Documentación](http://localhost:8000/docs) • [🚀 Instalación](#instalación) • [🤝 Contribuir](#contribuir)

</div>

---

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🏗️ Arquitectura](#️-arquitectura)
- [🚀 Instalación](#-instalación)
  - [🐳 Docker (Recomendado)](#-docker-recomendado)
  - [💻 Instalación Manual](#-instalación-manual)
  - [🔧 Servicio Persistente](#-servicio-persistente)
- [⚙️ Configuración](#️-configuración)
- [🎯 Uso](#-uso)
- [📊 API Endpoints](#-api-endpoints)
- [🧠 Vicky AI](#-vicky-ai)
- [🔥 High Scale Tasks](#-high-scale-tasks)
- [🏃 Desarrollo](#-desarrollo)
- [📈 Monitoreo](#-monitoreo)
- [🤝 Contribuir](#-contribuir)
- [📄 Licencia](#-licencia)

## ✨ Características

### 🤖 **Inteligencia Artificial - Vicky**
- 🧠 **Cerebro Dinámico** con balance hemisférico (técnico/emocional)
- 🔄 **Contexto Persistente** entre conversaciones
- 📚 **Memoria Avanzada** con capacidades de aprendizaje
- 🎭 **Personalidad Adaptativa** basada en el usuario

### 🌍 **Sistema de Traducción**
- 🔤 **+10 Idiomas** soportados
- 🚀 **Traducción en Tiempo Real**
- 📊 **Estadísticas de Uso** detalladas
- 💾 **Historial Completo** de traducciones

### 🎤 **Procesamiento de Voz**
- 🗣️ **Speech-to-Text** (STT) con Whisper
- 🔊 **Text-to-Speech** (TTS) con voces personalizadas
- 🎵 **Voces Sintéticas** con entrenamiento personalizado
- 📼 **Gestión de Samples** de audio

### 🔥 **Sistema de Tareas de Alta Escala**
- ⚡ **Millones de solicitudes** por segundo
- 🔄 **Auto-escalado** dinámico
- 📊 **Monitoreo en Tiempo Real**
- 🛡️ **Tolerancia a Fallos** con Dead Letter Queue

### 🖥️ **Integración Hardware**
- 📷 **Kinect Support** con streaming en tiempo real
- 🎥 **Video/Audio** processing
- 📡 **Webhooks** para integraciones externas

### 🔐 **Seguridad y Autenticación**
- 🔑 **JWT Authentication** con refresh tokens
- 🛡️ **API Keys** management
- 👥 **Multi-usuario** con roles
- 🔒 **Rate Limiting** y protección DDoS

### 📊 **Monitoreo y Analytics**
- 📈 **Métricas en Tiempo Real**
- 🚨 **Sistema de Alertas**
- 📋 **Logs Estructurados**
- 💾 **Backup Automático**

## 🏗️ Arquitectura

```mermaid
graph TB
    subgraph "Cliente"
        Web[Web App]
        Mobile[Mobile App]
        API_Client[API Client]
    end
    
    subgraph "VokaFlow Backend"
        Gateway[FastAPI Gateway]
        Auth[Authentication]
        
        subgraph "Core Services"
            Vicky[Vicky AI Engine]
            Translator[Translation Service]
            TTS[Text-to-Speech]
            STT[Speech-to-Text]
        end
        
        subgraph "High Scale System"
            TaskManager[Task Manager]
            Workers[Worker Pools]
            Scheduler[Task Scheduler]
        end
        
        subgraph "Data Layer"
            DB[(SQLite/PostgreSQL)]
            Redis[(Redis Cache)]
            Files[File Storage]
        end
    end
    
    subgraph "External Services"
        Kinect[Kinect Hardware]
        Webhooks[External APIs]
    end
    
    Web --> Gateway
    Mobile --> Gateway
    API_Client --> Gateway
    
    Gateway --> Auth
    Gateway --> Vicky
    Gateway --> Translator
    Gateway --> TTS
    Gateway --> STT
    
    Vicky --> TaskManager
    TaskManager --> Workers
    Workers --> Scheduler
    
    Auth --> Redis
    Vicky --> DB
    Translator --> DB
    TaskManager --> Redis
    
    Gateway --> Kinect
    Gateway --> Webhooks
```

## 🚀 Instalación

### 🐳 Docker (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/vokaflow-backend.git
cd vokaflow-backend

# Construir y ejecutar con Docker Compose
docker-compose up -d

# Verificar que funciona
curl http://localhost:8000/health
```

### 💻 Instalación Manual

#### Requisitos
- Python 3.12+
- Redis 7.0+
- SQLite/PostgreSQL
- OpenCV 4.5+
- libfreenect (para Kinect)

#### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/vokaflow-backend.git
cd vokaflow-backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración

# 5. Inicializar base de datos
python -c "from src.main import *; Base.metadata.create_all(bind=engine)"

# 6. Ejecutar servidor
python src/main.py
```

### 🔧 Servicio Persistente (Linux)

Para configurar VokaFlow como servicio del sistema:

```bash
# Hacer ejecutable el script de gestión
chmod +x manage-vokaflow.sh

# Instalar como servicio
./manage-vokaflow.sh install

# Comandos de gestión
./manage-vokaflow.sh status    # Ver estado
./manage-vokaflow.sh start     # Iniciar
./manage-vokaflow.sh stop      # Detener
./manage-vokaflow.sh restart   # Reiniciar
./manage-vokaflow.sh logs      # Ver logs
./manage-vokaflow.sh health    # Verificar salud
```

## ⚙️ Configuración

### Variables de Entorno

```env
# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False
ENVIRONMENT=production

# Base de Datos
DATABASE_URL=sqlite:///./vokaflow.db
# DATABASE_URL=postgresql://user:pass@localhost/vokaflow

# Redis
REDIS_URL=redis://localhost:6379

# Seguridad
SECRET_KEY=tu-clave-secreta-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Archivos
UPLOADS_DIR=./uploads
MODELS_DIR=./models
MAX_UPLOAD_SIZE=104857600

# APIs Externas
OPENAI_API_KEY=tu-clave-openai
GOOGLE_TRANSLATE_KEY=tu-clave-google

# Kinect
ENABLE_KINECT=true
KINECT_DEVICE_ID=0
```

## 🎯 Uso

### Inicio Rápido

```python
import requests

# Health Check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Traducir texto
translation = requests.post("http://localhost:8000/api/translate", json={
    "text": "Hola mundo",
    "target_lang": "en"
})
print(translation.json())

# Chatear con Vicky
chat = requests.post("http://localhost:8000/api/vicky/process", json={
    "message": "¿Cuál es el sentido de la vida?",
    "user_id": "usuario123"
})
print(chat.json())
```

### Enviar Tareas de Alta Escala

```python
# Enviar tarea computacional
task = requests.post("http://localhost:8000/api/high-scale-tasks/submit", json={
    "function_name": "math.sqrt",
    "args": [16],
    "priority": "HIGH",
    "worker_type": "CPU_INTENSIVE"
})
print(f"Task ID: {task.json()['task_id']}")

# Ver métricas del sistema
metrics = requests.get("http://localhost:8000/api/high-scale-tasks/metrics")
print(metrics.json())
```

## 📊 API Endpoints

### 🏥 Health & Status
- `GET /health` - Health check básico
- `GET /api/health/` - Health check detallado
- `GET /api/health/complete` - Health check completo

### 🔐 Autenticación
- `POST /api/auth/token` - Obtener token de acceso
- `POST /api/auth/register` - Registrar nuevo usuario
- `GET /api/users/me` - Información del usuario actual

### 🌍 Traducción
- `POST /api/translate` - Traducir texto
- `GET /api/translate/languages` - Idiomas soportados
- `GET /api/translate/history` - Historial de traducciones
- `GET /api/translate/stats` - Estadísticas de uso

### 🤖 Vicky AI
- `POST /api/vicky/process` - Procesar mensaje
- `GET /api/vicky/status` - Estado del sistema
- `POST /api/vicky/hemisphere` - Ajustar balance hemisférico

### 🔥 High Scale Tasks
- `POST /api/high-scale-tasks/submit` - Enviar tarea
- `GET /api/high-scale-tasks/metrics` - Métricas del sistema
- `GET /api/high-scale-tasks/status` - Estado general
- `POST /api/high-scale-tasks/control` - Control del sistema
- `GET /api/high-scale-tasks/dlq` - Dead Letter Queue

### 🎤 Voz
- `POST /api/tts/synthesize` - Text-to-Speech
- `POST /api/stt/transcribe` - Speech-to-Text
- `GET /api/voice/samples` - Muestras de voz
- `POST /api/voice/upload` - Subir muestra de voz

### 📊 Monitoreo
- `GET /api/monitoring/system` - Métricas del sistema
- `GET /api/monitoring/api` - Métricas de la API
- `GET /api/monitoring/alerts` - Alertas activas

### 🔧 Administración
- `GET /api/admin/users` - Gestión de usuarios
- `GET /api/admin/logs` - Logs del sistema
- `POST /api/admin/backup` - Crear backup
- `POST /api/system/restart` - Reiniciar sistema

## 🧠 Vicky AI

Vicky es el motor de IA conversacional de VokaFlow con capacidades avanzadas:

### Características
- **Balance Hemisférico**: Ajusta entre respuestas técnicas y emocionales
- **Contexto Persistente**: Mantiene el contexto entre conversaciones
- **Aprendizaje Continuo**: Mejora con cada interacción
- **Multi-modal**: Procesa texto, voz e imágenes

### Uso Avanzado

```python
# Configurar balance hemisférico
requests.post("http://localhost:8000/api/vicky/hemisphere", json={
    "action": "set",
    "technical": 0.7,
    "emotional": 0.3
})

# Conversación con contexto
requests.post("http://localhost:8000/api/vicky/process", json={
    "message": "Explícame machine learning",
    "context": {"nivel": "principiante", "interes": "desarrollo"},
    "session_id": "sesion_123"
})
```

## 🔥 High Scale Tasks

Sistema diseñado para manejar millones de tareas concurrentes:

### Tipos de Workers
- **CPU_INTENSIVE**: Cálculos matemáticos complejos
- **IO_INTENSIVE**: Operaciones de archivo/base de datos
- **MEMORY_INTENSIVE**: Procesamiento de grandes datasets
- **NETWORK_INTENSIVE**: Llamadas a APIs externas
- **GENERAL_PURPOSE**: Tareas generales

### Monitoreo

```bash
# Ver estado en tiempo real
curl http://localhost:8000/api/high-scale-tasks/metrics

# Enviar tareas de demostración
curl -X POST http://localhost:8000/api/high-scale-tasks/demo/submit-demo-tasks?count=10
```

## 🏃 Desarrollo

### Configurar Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Tests
pytest tests/ -v

# Coverage
pytest --cov=src tests/

# Linting
flake8 src/
black src/
isort src/
```

### Estructura del Proyecto

```
vokaflow-backend/
├── src/
│   ├── main.py                 # Punto de entrada
│   └── backend/
│       ├── core/               # Lógica central
│       │   ├── vicky/          # Motor de IA
│       │   └── high_scale_task_manager.py
│       ├── routers/            # Endpoints de API
│       │   ├── auth.py
│       │   ├── translate.py
│       │   ├── vicky.py
│       │   └── high_scale_tasks.py
│       └── utils/              # Utilidades
├── static/                     # Archivos estáticos
├── tests/                      # Tests
├── docs/                       # Documentación
├── scripts/                    # Scripts de utilidad
├── manage-vokaflow.sh         # Script de gestión
├── requirements.txt           # Dependencias
├── Dockerfile                 # Container Docker
├── docker-compose.yml         # Compose config
└── README.md                  # Este archivo
```

## 📈 Monitoreo

### Logs

```bash
# Logs del servicio
journalctl -u vokaflow-backend.service -f

# Logs de la aplicación
tail -f logs/vokaflow_backend.log

# Métricas del sistema
curl http://localhost:8000/api/monitoring/system
```

### Alertas

VokaFlow incluye alertas automáticas para:
- 🔴 **CPU > 80%**
- 🟡 **Memoria > 85%**
- 🔵 **Disco > 90%**
- ⚠️ **Fallos en Redis**
- 📈 **API response time > 2s**

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estándares de Código
- Python 3.12+
- Type hints obligatorios
- Docstrings para todas las funciones
- Tests para nuevo código
- Coverage mínimo 80%

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

<div align="center">

**¿Te gusta VokaFlow? ¡Dale una ⭐!**

Desarrollado con ❤️ por el equipo de VokaFlow

[🌐 Website](https://vokaflow.com) • [📧 Email](mailto:contact@vokaflow.com) • [🐦 Twitter](https://twitter.com/vokaflow)

</div> 